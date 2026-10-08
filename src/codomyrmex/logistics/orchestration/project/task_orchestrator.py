"""Task Orchestrator for Codomyrmex.

This module provides capability for scheduling, executing, and tracking individual tasks
within the logistics system.

Task dispatch
-------------
A task names the code it runs with ``module`` and ``action``. The orchestrator
resolves that pair to a callable and calls it with ``**task.parameters``:

1. An explicit registration in the orchestrator's :class:`ActionRegistry`
   (``orchestrator.register_action(module, action, func)``) wins.
2. Otherwise ``importlib.import_module(f"codomyrmex.{module}")`` is imported and
   the public attribute ``action`` is looked up on it.

An unknown module or action, or an exception raised by the callable, fails the
task (``TaskStatus.FAILED`` with the error recorded). Nothing is reported as
executed unless the callable actually ran and returned. Awaitables returned by
the callable are run to completion with :func:`asyncio.run` in the worker
thread.

Resources
---------
``Task.resources`` are allocated from the orchestrator's
:class:`~.resource_manager.ResourceManager` immediately before the task runs and
released when it finishes. A requirement that can never be met (unknown
resource or type, amount above capacity, resource offline) fails the task; a
requirement that is only temporarily unavailable keeps the task queued until
capacity is released.
"""

import asyncio
import importlib
import inspect
import re
import threading
import time
import uuid
from collections import deque
from collections.abc import Callable, Iterable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from codomyrmex.exceptions import CodomyrmexError, TaskExecutionError
from codomyrmex.logging_monitoring import get_logger

from .resource_manager import (
    Resource,
    ResourceAllocation,
    ResourceManager,
    ResourceStatus,
    ResourceType,
    get_resource_manager,
)

logger = get_logger(__name__)

ActionCallable = Callable[..., Any]

_MODULE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*")
_ACTION_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]*")


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
    resource_id: str | None = None  # Specific resource ID if needed


@dataclass
class TaskResult:
    """Result of a task execution."""

    task_id: str
    status: TaskStatus
    result: Any = None
    error: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Return True if task completed successfully."""
        return self.status == TaskStatus.COMPLETED

    def to_dict(self) -> dict[str, Any]:
        """Convert the result to a serializable dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "error": self.error,
            "success": self.success,
        }


@dataclass
class Task:
    """Task definition."""

    name: str
    module: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: list[str] = field(default_factory=list)  # list of task IDs
    resources: list[TaskResource] = field(default_factory=list)
    timeout: float | None = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)

    # Runtime state
    status: TaskStatus = TaskStatus.PENDING
    result: TaskResult | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    allocations: list[ResourceAllocation] = field(default_factory=list)

    @property
    def execution_time(self) -> float | None:
        """Get execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


TERMINAL_STATUSES = frozenset(
    {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}
)

# Resource states in which waiting can eventually yield an allocation.
_WAITABLE_RESOURCE_STATUSES = frozenset(
    {ResourceStatus.AVAILABLE, ResourceStatus.ALLOCATED, ResourceStatus.BUSY}
)


def resolve_module_action(module: str, action: str) -> ActionCallable:
    """Resolve ``codomyrmex.<module>.<action>`` to a callable.

    Args:
        module: Module path relative to the ``codomyrmex`` package
            (e.g. ``"coding.static_analysis"``).
        action: Public attribute of that module to call.

    Returns:
        The callable named by ``module`` and ``action``.

    Raises:
        TaskExecutionError: If either name is malformed, the module cannot be
            imported, or it has no public callable named ``action``.
    """
    if not isinstance(module, str) or not _MODULE_NAME.fullmatch(module):
        raise TaskExecutionError(
            f"Invalid task module {module!r}: expected a dotted module path "
            "relative to the codomyrmex package"
        )
    if not isinstance(action, str) or not _ACTION_NAME.fullmatch(action):
        raise TaskExecutionError(
            f"Invalid task action {action!r}: expected a public attribute name"
        )

    module_path = f"codomyrmex.{module}"
    try:
        imported = importlib.import_module(module_path)
    except ImportError as exc:
        raise TaskExecutionError(
            f"Cannot import module '{module_path}' for action '{action}': {exc}"
        ) from exc

    func = getattr(imported, action, None)
    if func is None:
        raise TaskExecutionError(f"Module '{module_path}' has no action '{action}'")
    if not callable(func):
        raise TaskExecutionError(f"'{module_path}.{action}' is not callable")
    return func


def invoke_action(func: ActionCallable, parameters: dict[str, Any]) -> Any:
    """Call ``func(**parameters)``, running a returned awaitable to completion."""
    result = func(**parameters)
    if inspect.isawaitable(result):
        awaitable = result

        async def _await_result() -> Any:
            return await awaitable

        return asyncio.run(_await_result())
    return result


class ActionRegistry:
    """Explicit ``(module, action) -> callable`` registrations for task dispatch.

    Registered actions take precedence over import-based resolution, which lets
    callers expose functions that do not live in a ``codomyrmex`` module.
    """

    def __init__(self) -> None:
        self._actions: dict[tuple[str, str], ActionCallable] = {}
        self._lock = threading.Lock()

    def register(self, module: str, action: str, func: ActionCallable) -> None:
        """Register ``func`` as the implementation of ``module``/``action``."""
        if not callable(func):
            raise TypeError(f"Action {module}.{action} must be callable, got {func!r}")
        with self._lock:
            self._actions[(module, action)] = func

    def unregister(self, module: str, action: str) -> bool:
        """Remove a registration; return True if one existed."""
        with self._lock:
            return self._actions.pop((module, action), None) is not None

    def get(self, module: str, action: str) -> ActionCallable | None:
        """Return the registered callable for ``module``/``action``, if any."""
        with self._lock:
            return self._actions.get((module, action))

    def resolve(self, module: str, action: str) -> ActionCallable:
        """Return the registered callable, else resolve it by import."""
        registered = self.get(module, action)
        if registered is not None:
            return registered
        return resolve_module_action(module, action)


def describe_exception(exc: BaseException) -> str:
    """Render an exception raised by an action as a task error message."""
    if isinstance(exc, CodomyrmexError):
        return str(exc)
    return f"{type(exc).__name__}: {exc}"


class TaskOrchestrator:
    """Orchestrates the execution of tasks."""

    def __init__(
        self,
        max_workers: int = 4,
        resource_manager: ResourceManager | None = None,
        actions: ActionRegistry | None = None,
    ):
        """Initialize the task orchestrator.

        Args:
            max_workers: Maximum number of tasks executing concurrently.
            resource_manager: Pool that ``Task.resources`` are allocated from.
                Defaults to the global resource manager.
            actions: Registry consulted before import-based dispatch. A new,
                empty registry is created when omitted.
        """
        self.tasks: dict[str, Task] = {}
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.resource_manager = (
            resource_manager if resource_manager is not None else get_resource_manager()
        )
        self.actions = actions if actions is not None else ActionRegistry()

        # Queues for different priorities
        self.queues: dict[TaskPriority, deque[str]] = {p: deque() for p in TaskPriority}

        self.running_tasks: dict[str, Future] = {}
        self.task_results: dict[str, TaskResult] = {}
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._worker_thread = None

    def register_action(self, module: str, action: str, func: ActionCallable) -> None:
        """Register ``func`` as the implementation of ``module``/``action``."""
        self.actions.register(module, action, func)

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
                logger.warning("Task %s already exists, handling as update", task.id)

            self.tasks[task.id] = task
            task.status = TaskStatus.PENDING

            state, reason = self._dependency_state(task)
            if state == "ready":
                self.queues[task.priority].append(task.id)
                task.status = TaskStatus.READY
            elif state == "blocked":
                task.status = TaskStatus.BLOCKED
            else:
                self._finalize(task, TaskStatus.FAILED, error=reason)

            logger.info("Submitted task: %s (%s)", task.name, task.id)

            # Ensure processor is running
            self.start_processing()

            return task.id

    def execute_task(self, task: Task) -> TaskResult:
        """Execute a task synchronously (blocking until it reaches a final state)."""
        self.submit_task(task)
        self.wait_for_tasks([task.id])
        with self._lock:
            result = self.task_results.get(task.id)
        if result is None:
            raise TaskExecutionError(
                f"Task {task.name} finished without a recorded result", task_id=task.id
            )
        return result

    def _process_queue(self):
        """Main processing loop."""
        while not self._stop_event.is_set():
            try:
                # Find highest priority task
                task_id = self._get_next_task()

                if task_id:
                    if not self._run_task(task_id):
                        # Resources are busy: let running tasks release them.
                        self._check_blocked_tasks()
                        time.sleep(0.05)
                else:
                    # Check blocked tasks
                    self._check_blocked_tasks()
                    time.sleep(0.1)

            except Exception as e:
                logger.error("Error in task processor: %s", e)
                time.sleep(1.0)

    def _get_next_task(self) -> str | None:
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

    def _dependency_state(self, task: Task) -> tuple[str, str | None]:
        """Classify a task's dependencies as ``ready``, ``blocked`` or ``failed``.

        A dependency that failed or was cancelled can never be satisfied, so the
        dependent task fails instead of staying blocked forever. A dependency ID
        that is not (yet) known keeps the task blocked.
        """
        blocked = False
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if dep_task is None:
                blocked = True
                continue
            if dep_task.status in (TaskStatus.FAILED, TaskStatus.CANCELLED):
                return (
                    "failed",
                    f"Dependency '{dep_task.name}' ({dep_id}) "
                    f"{dep_task.status.value}; task not run",
                )
            if dep_task.status != TaskStatus.COMPLETED:
                blocked = True
        return ("blocked", None) if blocked else ("ready", None)

    def _check_dependencies(self, task: Task) -> bool:
        """Check if task dependencies are met."""
        return self._dependency_state(task)[0] == "ready"

    def _check_blocked_tasks(self):
        """Promote blocked tasks whose dependencies completed; fail those whose failed."""
        with self._lock:
            for task in list(self.tasks.values()):
                if task.status != TaskStatus.BLOCKED:
                    continue
                state, reason = self._dependency_state(task)
                if state == "ready":
                    task.status = TaskStatus.READY
                    self.queues[task.priority].append(task.id)
                elif state == "failed":
                    self._finalize(task, TaskStatus.FAILED, error=reason)

    def _run_task(self, task_id: str) -> bool:
        """Start a queued task.

        Returns:
            False if the task was put back in its queue because its resources
            are temporarily unavailable, True otherwise.
        """
        with self._lock:
            task = self.tasks.get(task_id)
            # Cancelled (or duplicate) queue entries are skipped.
            if task is None or task.status != TaskStatus.READY:
                return True

            try:
                acquired = self._acquire_resources(task)
            except TaskExecutionError as exc:
                self._finalize(task, TaskStatus.FAILED, error=str(exc))
                return True

            if not acquired:
                self.queues[task.priority].append(task_id)
                return False

            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(UTC)

            future = self.executor.submit(self._execute_task_logic, task)
            self.running_tasks[task_id] = future
            future.add_done_callback(lambda f: self._on_task_complete(task_id, f))
            return True

    def _resolve_resource(self, requirement: TaskResource) -> Resource:
        """Pick the resource that will satisfy ``requirement``.

        Raises:
            TaskExecutionError: If the requirement can never be satisfied.
        """
        if requirement.amount <= 0:
            raise TaskExecutionError(
                f"Resource amount must be positive, got {requirement.amount}"
            )

        if requirement.resource_id is not None:
            resource = self.resource_manager.get_resource(requirement.resource_id)
            if resource is None:
                raise TaskExecutionError(
                    f"Unknown resource id '{requirement.resource_id}'"
                )
            if resource.type.value != requirement.resource_type:
                raise TaskExecutionError(
                    f"Resource '{resource.id}' has type '{resource.type.value}', "
                    f"not '{requirement.resource_type}'"
                )
            candidates = [resource]
        else:
            try:
                resource_type = ResourceType(requirement.resource_type)
            except ValueError as exc:
                raise TaskExecutionError(
                    f"Unknown resource type '{requirement.resource_type}'"
                ) from exc
            candidates = self.resource_manager.list_resources(resource_type)
            if not candidates:
                raise TaskExecutionError(
                    f"No resource of type '{requirement.resource_type}' is registered"
                )

        usable = [
            resource
            for resource in candidates
            if resource.status in _WAITABLE_RESOURCE_STATUSES
            and resource.capacity >= requirement.amount
        ]
        if not usable:
            raise TaskExecutionError(
                f"Resource requirement {requirement.amount} x "
                f"'{requirement.resource_type}' cannot be satisfied: candidates "
                + ", ".join(
                    f"{r.id} (capacity {r.capacity}, {r.status.value})"
                    for r in candidates
                )
            )
        return max(usable, key=lambda r: r.capacity - r.allocated)

    def _acquire_resources(self, task: Task) -> bool:
        """Allocate every resource the task requires, all or nothing.

        Returns:
            True when all requirements were allocated (recorded on
            ``task.allocations``), False when capacity is temporarily short.

        Raises:
            TaskExecutionError: If a requirement can never be satisfied.
        """
        allocations: list[ResourceAllocation] = []
        for requirement in task.resources:
            resource = self._resolve_resource(requirement)
            allocation = self.resource_manager.allocate(
                resource.id, task.id, requirement.amount
            )
            if allocation is None:
                self._release_allocations(allocations)
                return False
            allocations.append(allocation)
        task.allocations = allocations
        return True

    def _release_allocations(self, allocations: Iterable[ResourceAllocation]) -> None:
        for allocation in allocations:
            if not self.resource_manager.release(allocation.allocation_id):
                logger.error(
                    "Allocation %s was already released", allocation.allocation_id
                )

    def _execute_task_logic(self, task: Task) -> Any:
        """Resolve ``task.module``/``task.action`` and call it with the parameters."""
        logger.info("Executing task: %s (%s.%s)", task.name, task.module, task.action)
        func = self.actions.resolve(task.module, task.action)
        return invoke_action(func, task.parameters)

    def _finalize(
        self,
        task: Task,
        status: TaskStatus,
        result: Any = None,
        error: str | None = None,
    ) -> None:
        """Record the final result of a task. Caller must hold ``self._lock``."""
        if task.completed_at is None:
            task.completed_at = datetime.now(UTC)
        metadata: dict[str, Any] = {}
        if task.allocations:
            metadata["allocations"] = [a.allocation_id for a in task.allocations]
        task_result = TaskResult(
            task_id=task.id,
            status=status,
            result=result,
            error=error,
            start_time=task.started_at,
            end_time=task.completed_at,
            duration=task.execution_time,
            metadata=metadata,
        )
        # Publish the result before the terminal status so that anyone who
        # observes the terminal status also finds the result.
        self.task_results[task.id] = task_result
        task.result = task_result
        task.error = error
        task.status = status
        if status == TaskStatus.FAILED:
            logger.error("Task %s failed: %s", task.name, error)
        logger.info("Task finished: %s (%s)", task.name, status.value)

    def _on_task_complete(self, task_id: str, future: Future):
        """Handle task completion."""
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return

            self.running_tasks.pop(task_id, None)
            self._release_allocations(task.allocations)

            if task.status == TaskStatus.CANCELLED:
                # cancel_task already recorded the cancellation; the late
                # result of the uncancellable thread is discarded.
                task.allocations = []
                return

            task.completed_at = datetime.now(UTC)
            exc = future.exception()
            if exc is None:
                self._finalize(task, TaskStatus.COMPLETED, result=future.result())
            else:
                self._finalize(task, TaskStatus.FAILED, error=describe_exception(exc))
            task.allocations = []

    def list_tasks(self) -> list[Task]:
        """list all tasks."""
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.

        A queued or blocked task is removed and never runs. A running task
        cannot be interrupted; it is marked cancelled immediately and its
        eventual return value is discarded.
        """
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return False

            if task.status in TERMINAL_STATUSES:
                return False

            if task.status == TaskStatus.RUNNING:
                error = "Task was cancelled while running; its result is discarded"
            else:
                error = "Task was cancelled before it started"
                queue = self.queues[task.priority]
                if task_id in queue:
                    queue.remove(task_id)

            self._finalize(task, TaskStatus.CANCELLED, error=error)
            logger.info("Cancelled task: %s", task.name)
            return True

    def wait_for_tasks(
        self, task_ids: Iterable[str], timeout: float | None = None
    ) -> bool:
        """Wait until every task in ``task_ids`` reaches a final state.

        Args:
            task_ids: IDs of submitted tasks.
            timeout: Maximum seconds to wait; ``None`` waits indefinitely.

        Returns:
            True if all tasks finished, False if the timeout expired first.

        Raises:
            KeyError: If an ID does not belong to a submitted task.
            TaskExecutionError: If processing was stopped while some of the
                tasks are still queued or blocked (they could never finish).
        """
        ids = list(task_ids)
        with self._lock:
            unknown = [task_id for task_id in ids if task_id not in self.tasks]
        if unknown:
            raise KeyError(f"Unknown task ids: {unknown}")

        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            with self._lock:
                pending = [
                    self.tasks[t]
                    for t in ids
                    if self.tasks[t].status not in TERMINAL_STATUSES
                ]
                if not pending:
                    return True
                # Running tasks still finish after a stop; queued ones never do.
                stalled = [t.name for t in pending if t.status != TaskStatus.RUNNING]
                if self._stop_event.is_set() and stalled:
                    raise TaskExecutionError(
                        f"Task orchestrator was stopped; tasks {stalled} cannot run"
                    )
            if deadline is not None and time.monotonic() >= deadline:
                return False
            time.sleep(0.05)

    def wait_for_completion(self, timeout: float | None = 10.0) -> bool:
        """Wait for all tasks to complete."""
        effective_timeout = (
            timeout if timeout is not None else 86400.0
        )  # 1 day fallback
        start = time.time()
        while time.time() - start < effective_timeout:
            with self._lock:
                all_completed = all(
                    task.status in TERMINAL_STATUSES for task in self.tasks.values()
                )
                if (
                    all_completed
                    and not any(self.queues.values())
                    and not self.running_tasks
                ):
                    return True
            time.sleep(0.1)
        return False

    def get_task_result(self, task_id: str) -> TaskResult | None:
        """Return the result recorded for a task, if available."""
        task = self.tasks.get(task_id)
        if task:
            return task.result
        return self.task_results.get(task_id)

    def get_execution_stats(self) -> dict:
        """Get stats on execution."""
        with self._lock:
            tasks = list(self.tasks.values())
            running = len(self.running_tasks)

        def count(*statuses: TaskStatus) -> int:
            return sum(1 for t in tasks if t.status in statuses)

        return {
            "total_tasks": len(tasks),
            "pending": count(TaskStatus.PENDING, TaskStatus.READY),
            "blocked": count(TaskStatus.BLOCKED),
            "running": running,
            "completed": count(TaskStatus.COMPLETED),
            "failed": count(TaskStatus.FAILED),
            "cancelled": count(TaskStatus.CANCELLED),
        }


# Global task orchestrator instance
_task_orchestrator = None


def get_task_orchestrator() -> TaskOrchestrator:
    """Get the global task orchestrator instance."""
    global _task_orchestrator
    if _task_orchestrator is None:
        _task_orchestrator = TaskOrchestrator()
    return _task_orchestrator
