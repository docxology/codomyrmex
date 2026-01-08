from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Optional
import logging
import time

from dataclasses import asdict, dataclass, field
from enum import Enum
from queue import PriorityQueue as StdPriorityQueue
import signal
import threading
import uuid

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol import MCPErrorDetail, MCPToolResult
from codomyrmex.performance import PerformanceMonitor, monitor_performance






"""
Task Orchestration System for Codomyrmex

This module provides task-level orchestration capabilities, handling individual
task execution, dependency management, and coordination across Codomyrmex modules.
"""


# Import Codomyrmex modules
try:

    logger = get_logger(__name__)
except ImportError:

    logger = logging.getLogger(__name__)

try:

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
            return func

        return decorator


try:

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    READY = "ready"  # Dependencies satisfied, ready to run
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Task execution priority."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ResourceType(Enum):
    """Types of resources that tasks can use."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    FILE = "file"
    DATABASE = "database"
    EXTERNAL_API = "external_api"


@dataclass
class TaskResource:
    """Represents a resource required by a task."""

    type: ResourceType
    identifier: str  # Resource ID/name
    mode: str = "read"  # read, write, exclusive
    timeout: Optional[int] = None


@dataclass
class TaskResult:
    """Result of task execution."""

    success: bool
    data: Any = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskResult":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Task:
    """Represents an individual task in the orchestration system."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    module: str = ""  # Codomyrmex module name
    action: str = ""  # Module action/function name
    parameters: dict[str, Any] = field(default_factory=dict)

    # Dependencies and scheduling
    dependencies: list[str] = field(default_factory=list)  # Task IDs this depends on
    priority: TaskPriority = TaskPriority.NORMAL
    resources: list[TaskResource] = field(default_factory=list)

    # Execution control
    timeout: Optional[int] = None
    max_retries: int = 3
    retry_delay: float = 1.0  # Seconds between retries

    # Status tracking
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[TaskResult] = None

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization setup."""
        if not self.name:
            self.name = (
                f"{self.module}.{self.action}"
                if self.module and self.action
                else self.id
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        data["resources"] = [asdict(r) for r in self.resources]
        data["created_at"] = self.created_at.isoformat()
        if self.started_at:
            data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        if self.result:
            data["result"] = self.result.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create from dictionary."""
        data = data.copy()
        if "priority" in data:
            data["priority"] = TaskPriority(data["priority"])
        if "status" in data:
            data["status"] = TaskStatus(data["status"])
        if "resources" in data:
            data["resources"] = [TaskResource(**r) for r in data["resources"]]
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "started_at" in data and data["started_at"]:
            data["started_at"] = datetime.fromisoformat(data["started_at"])
        if "completed_at" in data and data["completed_at"]:
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        if "result" in data and data["result"]:
            data["result"] = TaskResult.from_dict(data["result"])
        return cls(**data)

    @property
    def execution_time(self) -> Optional[float]:
        """Get task execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.status == TaskStatus.FAILED and self.retry_count < self.max_retries

    def is_ready(self, completed_tasks: set[str]) -> bool:
        """Check if task is ready to execute (dependencies satisfied)."""
        return self.status == TaskStatus.PENDING and all(
            dep_id in completed_tasks for dep_id in self.dependencies
        )


class ResourceManager:
    """Manages resource allocation and locking for tasks."""

    def __init__(self):
        """Initialize the resource manager."""
        self.resource_locks: dict[str, threading.Lock] = {}
        self.resource_users: dict[str, set[str]] = {}  # resource_id -> set of task_ids
        self.lock = threading.Lock()

    def acquire_resources(self, task: Task) -> bool:
        """Acquire all resources needed by a task."""
        acquired = []

        try:
            with self.lock:
                # Check if all resources are available
                for resource in task.resources:
                    resource_key = f"{resource.type.value}:{resource.identifier}"

                    if resource_key not in self.resource_locks:
                        self.resource_locks[resource_key] = threading.Lock()
                        self.resource_users[resource_key] = set()

                    # Check availability based on mode
                    if resource.mode == "exclusive":
                        if self.resource_users[resource_key]:
                            # Resource is in use, cannot acquire
                            return False
                    elif resource.mode == "write":
                        # Cannot write if anyone is using it
                        if self.resource_users[resource_key]:
                            return False
                    # Read mode allows multiple readers

                # All resources are available, acquire them
                for resource in task.resources:
                    resource_key = f"{resource.type.value}:{resource.identifier}"
                    self.resource_users[resource_key].add(task.id)
                    acquired.append(resource_key)

                return True

        except Exception as e:
            # Release any acquired resources on failure
            self.release_resources(task, acquired)
            logger.error(f"Error acquiring resources for task {task.id}: {e}")
            return False

    def release_resources(self, task: Task, resource_keys: Optional[list[str]] = None):
        """Release resources used by a task."""
        if resource_keys is None:
            resource_keys = [f"{r.type.value}:{r.identifier}" for r in task.resources]

        with self.lock:
            for resource_key in resource_keys:
                if resource_key in self.resource_users:
                    self.resource_users[resource_key].discard(task.id)


class TaskQueue:
    """Priority queue for managing task execution order."""

    def __init__(self):
        """Initialize the task queue."""
        self.queue = StdPriorityQueue()
        self.tasks: dict[str, Task] = {}
        self.lock = threading.Lock()

    def add_task(self, task: Task):
        """Add a task to the queue."""
        with self.lock:
            self.tasks[task.id] = task
            # Priority queue uses negative priority for max-heap behavior
            priority_value = -task.priority.value
            self.queue.put((priority_value, task.created_at.timestamp(), task.id))

    def get_next_ready_task(self, completed_tasks: set[str]) -> Optional[Task]:
        """Get the next ready task from the queue."""
        temp_tasks = []

        try:
            while not self.queue.empty():
                priority, timestamp, task_id = self.queue.get()

                with self.lock:
                    if task_id not in self.tasks:
                        continue  # Task was removed

                    task = self.tasks[task_id]

                    if task.is_ready(completed_tasks):
                        # Put back any temporarily removed tasks
                        for temp_item in temp_tasks:
                            self.queue.put(temp_item)
                        return task
                    else:
                        # Task not ready, remember it for later
                        temp_tasks.append((priority, timestamp, task_id))

            # Put back all tasks
            for temp_item in temp_tasks:
                self.queue.put(temp_item)

            return None

        except Exception as e:
            # Put back all temporarily removed tasks
            for temp_item in temp_tasks:
                self.queue.put(temp_item)
            logger.error(f"Error getting next ready task: {e}")
            return None

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the queue."""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
        return False

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        with self.lock:
            return self.tasks.get(task_id)

    def list_tasks(self) -> list[Task]:
        """List all tasks in the queue."""
        with self.lock:
            return list(self.tasks.values())


class TaskOrchestrator:
    """Orchestrates task execution with dependency management and resource control."""

    def __init__(self, max_workers: int = 4):
        """Initialize the task orchestrator."""
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.resource_manager = ResourceManager()
        self.task_queue = TaskQueue()

        # Execution tracking
        self.completed_tasks: set[str] = set()
        self.running_tasks: dict[str, threading.Thread] = {}
        self.task_results: dict[str, TaskResult] = {}

        # Control
        self.shutdown_requested = False
        self.execution_thread: Optional[threading.Thread] = None

        # Performance monitoring
        self.performance_monitor = (
            PerformanceMonitor() if PERFORMANCE_AVAILABLE else None
        )

        logger.info(f"TaskOrchestrator initialized with {max_workers} workers")

    def add_task(self, task: Task) -> str:
        """Add a task to the orchestrator."""
        self.task_queue.add_task(task)
        logger.info(f"Added task: {task.name} ({task.id})")
        return task.id

    def create_task(self, name: str, module: str, action: str, **kwargs) -> Task:
        """Create and add a new task."""
        task = Task(
            name=name,
            module=module,
            action=action,
            parameters=kwargs.get("parameters", {}),
            dependencies=kwargs.get("dependencies", []),
            priority=kwargs.get("priority", TaskPriority.NORMAL),
            timeout=kwargs.get("timeout"),
            max_retries=kwargs.get("max_retries", 3),
            resources=kwargs.get("resources", []),
            tags=kwargs.get("tags", []),
            metadata=kwargs.get("metadata", {}),
        )

        self.add_task(task)
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.task_queue.get_task(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> list[Task]:
        """List tasks, optionally filtered by status."""
        tasks = self.task_queue.list_tasks()
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def start_execution(self):
        """Start the task execution engine."""
        if self.execution_thread and self.execution_thread.is_alive():
            logger.warning("Task execution already running")
            return

        self.shutdown_requested = False
        self.execution_thread = threading.Thread(
            target=self._execution_loop, daemon=True
        )
        self.execution_thread.start()
        logger.info("Task execution engine started")

    def stop_execution(self):
        """Stop the task execution engine."""
        self.shutdown_requested = True
        if self.execution_thread:
            self.execution_thread.join(timeout=5.0)
        logger.info("Task execution engine stopped")

    def _execution_loop(self):
        """Main execution loop for processing tasks."""
        logger.info("Task execution loop started")

        while not self.shutdown_requested:
            try:
                # Get next ready task
                task = self.task_queue.get_next_ready_task(self.completed_tasks)

                if task is None:
                    # No ready tasks, wait a bit
                    time.sleep(0.1)
                    continue

                # Try to acquire resources
                if not self.resource_manager.acquire_resources(task):
                    # Resources not available, try again later
                    time.sleep(0.1)
                    continue

                # Execute task
                self._execute_task_async(task)

            except Exception as e:
                logger.error(f"Error in execution loop: {e}")
                time.sleep(1.0)

        logger.info("Task execution loop stopped")

    def _execute_task_async(self, task: Task):
        """Execute a task asynchronously."""

        def task_wrapper():
            """Wrapper for async task execution."""
            try:
                result = self.execute_task(task)
                self.task_results[task.id] = result

                if result.success:
                    task.status = TaskStatus.COMPLETED
                    self.completed_tasks.add(task.id)
                    logger.info(f"Task completed: {task.name} ({task.id})")
                else:
                    if task.can_retry():
                        task.retry_count += 1
                        task.status = TaskStatus.PENDING
                        time.sleep(task.retry_delay)
                        logger.info(
                            f"Retrying task: {task.name} (attempt {task.retry_count + 1})"
                        )
                    else:
                        task.status = TaskStatus.FAILED
                        logger.error(
                            f"Task failed: {task.name} ({task.id}) - {result.error_message}"
                        )

            except Exception as e:
                task.status = TaskStatus.FAILED
                result = TaskResult(success=False, error_message=str(e))
                self.task_results[task.id] = result
                logger.error(f"Task execution error: {task.name} ({task.id}) - {e}")

            finally:
                task.completed_at = datetime.now(timezone.utc)
                self.resource_manager.release_resources(task)
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]

        thread = threading.Thread(target=task_wrapper, daemon=True)
        self.running_tasks[task.id] = thread
        thread.start()

    @monitor_performance(function_name="execute_task")
    def execute_task(self, task: Task) -> TaskResult:
        """Execute a single task synchronously."""
        task.started_at = datetime.now(timezone.utc)
        task.status = TaskStatus.RUNNING

        logger.info(f"Executing task: {task.name} ({task.module}.{task.action})")

        start_time = time.time()

        try:
            # Import the module dynamically
            module_name = f"codomyrmex.{task.module}"
            module = __import__(module_name, fromlist=[task.action])

            # Get the action function
            if not hasattr(module, task.action):
                return TaskResult(
                    success=False,
                    error_message=f"Action '{task.action}' not found in module '{task.module}'",
                    error_type="AttributeError",
                    execution_time=time.time() - start_time,
                )

            action_func = getattr(module, task.action)

            # Execute with timeout if specified
            if task.timeout:

                def timeout_handler(signum, frame):
                    """Handle task timeout signal."""
                    raise TimeoutError(f"Task timed out after {task.timeout} seconds")

                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(task.timeout)

            try:
                # Execute the action
                result_data = action_func(**task.parameters)

                # Cancel timeout if set
                if task.timeout:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)

                execution_time = time.time() - start_time

                return TaskResult(
                    success=True,
                    data=result_data,
                    execution_time=execution_time,
                    metadata={
                        "module": task.module,
                        "action": task.action,
                        "task_id": task.id,
                    },
                )

            except TimeoutError as e:
                if task.timeout:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                raise e

        except ImportError as e:
            return TaskResult(
                success=False,
                error_message=f"Module '{task.module}' not available: {e}",
                error_type="ImportError",
                execution_time=time.time() - start_time,
            )
        except TimeoutError as e:
            return TaskResult(
                success=False,
                error_message=str(e),
                error_type="TimeoutError",
                execution_time=time.time() - start_time,
            )
        except Exception as e:
            return TaskResult(
                success=False,
                error_message=f"Task execution error: {e}",
                error_type=type(e).__name__,
                execution_time=time.time() - start_time,
            )

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = self.get_task(task_id)
        if not task:
            return False

        if task.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc)

        # If task is running, we can't really stop it (would need more complex threading)
        # But we mark it as cancelled

        self.resource_manager.release_resources(task)
        logger.info(f"Cancelled task: {task.name} ({task.id})")
        return True

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed task."""
        return self.task_results.get(task_id)

    def get_execution_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        tasks = self.list_tasks()

        stats = {
            "total_tasks": len(tasks),
            "pending": len([t for t in tasks if t.status == TaskStatus.PENDING]),
            "ready": len([t for t in tasks if t.status == TaskStatus.READY]),
            "running": len([t for t in tasks if t.status == TaskStatus.RUNNING]),
            "completed": len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
            "failed": len([t for t in tasks if t.status == TaskStatus.FAILED]),
            "cancelled": len([t for t in tasks if t.status == TaskStatus.CANCELLED]),
            "total_execution_time": sum(
                t.execution_time or 0 for t in tasks if t.execution_time
            ),
            "average_execution_time": 0,
        }

        completed_tasks = [t for t in tasks if t.execution_time]
        if completed_tasks:
            stats["average_execution_time"] = stats["total_execution_time"] / len(
                completed_tasks
            )

        return stats

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete."""
        start_time = time.time()

        while True:
            pending_tasks = [
                t
                for t in self.list_tasks()
                if t.status
                in [TaskStatus.PENDING, TaskStatus.READY, TaskStatus.RUNNING]
            ]

            if not pending_tasks:
                return True

            if timeout and (time.time() - start_time) > timeout:
                return False

            time.sleep(0.1)

    def __del__(self):
        """Cleanup when orchestrator is destroyed."""
        self.stop_execution()
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)


# Global task orchestrator instance
_task_orchestrator = None


def get_task_orchestrator() -> TaskOrchestrator:
    """Get the global task orchestrator instance."""
    global _task_orchestrator
    if _task_orchestrator is None:
        _task_orchestrator = TaskOrchestrator()
    return _task_orchestrator
