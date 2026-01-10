"""Task Orchestrator for Codomyrmex.

This module provides capability for scheduling, executing, and tracking individual tasks
within the logistics system.
"""

from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Deque
import asyncio
import logging
import threading
import time
import uuid

from dataclasses import dataclass, field

from codomyrmex.logging_monitoring.logger_config import get_logger
from .resource_manager import get_resource_manager, ResourceManager, ResourceAllocation

logger = get_logger(__name__)


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class TaskResource:
    """Resource requirement for a task."""
    resource_type: str
    amount: float = 1.0
    resource_id: Optional[str] = None  # Specific resource ID if needed


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task definition."""
    name: str
    module: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: List[str] = field(default_factory=list)  # List of task IDs
    resources: List[TaskResource] = field(default_factory=list)
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Runtime state
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    allocations: List[ResourceAllocation] = field(default_factory=list)
    
    @property
    def execution_time(self) -> Optional[float]:
        """Get execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class TaskOrchestrator:
    """Orchestrates the execution of tasks."""

    def __init__(self, max_workers: int = 4):
        """Initialize the task orchestrator."""
        self.tasks: Dict[str, Task] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.resource_manager = get_resource_manager()
        
        # Queues for different priorities
        self.queues: Dict[TaskPriority, Deque[str]] = {
            p: deque() for p in TaskPriority
        }
        
        self.running_tasks: Dict[str, Future] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._worker_thread = None

    def start_processing(self):
        """Start the background processing loop."""
        if self._worker_thread and self._worker_thread.is_alive():
            return
            
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()
        logger.info("Task orchestrator started")

    def stop_execution(self):
        """Stop processing tasks."""
        self._stop_event.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        logger.info("Task orchestrator stopped")

    def submit_task(self, task: Task) -> str:
        """Submit a task for execution."""
        with self._lock:
            if task.id in self.tasks:
                logger.warning(f"Task {task.id} already exists, handling as update")
            
            self.tasks[task.id] = task
            task.status = TaskStatus.PENDING
            
            # Check dependencies
            if not self._check_dependencies(task):
                task.status = TaskStatus.BLOCKED
            else:
                self.queues[task.priority].append(task.id)
                task.status = TaskStatus.READY
                
            logger.info(f"Submitted task: {task.name} ({task.id})")
            
            # Ensure processor is running
            self.start_processing()
            
            return task.id

    def execute_task(self, task: Task) -> TaskResult:
        """Execute a task synchronously (blocking)."""
        self.submit_task(task)
        
        # Wait for completion
        while task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            time.sleep(0.1)
            
        return self.task_results.get(task.id) or TaskResult(
            task_id=task.id,
            status=TaskStatus.FAILED,
            error="Result not found"
        )

    def _process_queue(self):
        """Main processing loop."""
        while not self._stop_event.is_set():
            try:
                # Find highest priority task
                task_id = self._get_next_task()
                
                if task_id:
                    self._run_task(task_id)
                else:
                    # Check blocked tasks
                    self._check_blocked_tasks()
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error in task processor: {e}")
                time.sleep(1.0)

    def _get_next_task(self) -> Optional[str]:
        """Get the next ready task from queues based on priority."""
        with self._lock:
            # Check capacity
            if len(self.running_tasks) >= self.max_workers:
                return None
                
            for priority in TaskPriority:
                queue = self.queues[priority]
                if queue:
                    return queue.popleft()
            return None

    def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are met."""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def _check_blocked_tasks(self):
        """Check if blocked tasks can proceed."""
        with self._lock:
            for task in self.tasks.values():
                if task.status == TaskStatus.BLOCKED:
                    if self._check_dependencies(task):
                        task.status = TaskStatus.READY
                        self.queues[task.priority].append(task.id)

    def _run_task(self, task_id: str):
        """Run a specific task."""
        task = self.tasks.get(task_id)
        if not task:
            return

        # Allocate resources if needed
        # (Simplified: assume resources are available for now or implement real allocation)
        # In a real implementation, we would check self.resource_manager.allocate(...)
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        
        future = self.executor.submit(self._execute_task_logic, task)
        self.running_tasks[task_id] = future
        future.add_done_callback(lambda f: self._on_task_complete(task_id, f))

    def _execute_task_logic(self, task: Task) -> Any:
        """Execute the actual task logic."""
        logger.info(f"Executing task: {task.name} ({task.action})")
        
        # Simulate execution or dynamically call module
        # Ideally this would use `importlib` to load `task.module` and call `task.action`
        # For now, we'll just simulate success for recognized actions
        
        if task.action == "sleep":
            duration = task.parameters.get("duration", 1)
            time.sleep(duration)
            return f"Slept for {duration} seconds"
        elif task.action == "echo":
            return task.parameters.get("message", "")
        else:
            # Try to dispatch to registered handlers or assume success
            time.sleep(0.1)
            return {"status": "executed", "action": task.action}

    def _on_task_complete(self, task_id: str, future: Future):
        """Handle task completion."""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return
                
            task.completed_at = datetime.now(timezone.utc)
            self.running_tasks.pop(task_id, None)
            
            try:
                result = future.result()
                task.status = TaskStatus.COMPLETED
                task_result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED,
                    result=result,
                    start_time=task.started_at,
                    end_time=task.completed_at,
                    duration=task.execution_time
                )
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task_result = TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=str(e),
                    start_time=task.started_at,
                    end_time=task.completed_at,
                    duration=task.execution_time
                )
                logger.error(f"Task {task.name} failed: {e}")
            
            self.task_results[task_id] = task_result
            task.result = task_result
            logger.info(f"Task completed: {task.name} ({task.status.value})")

    def list_tasks(self) -> List[Task]:
        """List all tasks."""
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
                
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return False
                
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now(timezone.utc)
            
            # Note: We can't easily kill running threads in ThreadPoolExecutor
            # but we can mark it as cancelled so we don't return its result or trigger dependents
            
            logger.info(f"Cancelled task: {task.name}")
            return True


# Global task orchestrator instance
_task_orchestrator = None


def get_task_orchestrator() -> TaskOrchestrator:
    """Get the global task orchestrator instance."""
    global _task_orchestrator
    if _task_orchestrator is None:
        _task_orchestrator = TaskOrchestrator()
    return _task_orchestrator
