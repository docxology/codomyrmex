"""Maintenance task scheduler.

Provides a cron-like scheduler for recurring maintenance tasks
such as dependency audits, stale file cleanup, and health checks.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class TaskPriority(Enum):
    """Priority levels for maintenance tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Execution status of a maintenance task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ScheduleConfig:
    """Schedule configuration for a maintenance task.

    Attributes:
        interval_seconds: Time between runs.
        max_retries: Maximum retry attempts on failure.
        retry_delay_seconds: Delay between retries.
        timeout_seconds: Maximum run time before killing.
        run_on_startup: Whether to run immediately on scheduler start.
    """

    interval_seconds: float = 3600.0  # 1 hour
    max_retries: int = 3
    retry_delay_seconds: float = 60.0
    timeout_seconds: float = 300.0
    run_on_startup: bool = False


@dataclass
class TaskResult:
    """Result of a maintenance task execution.

    Attributes:
        task_name: Name of the task.
        status: Final status.
        started_at: Unix timestamp when execution began.
        completed_at: Unix timestamp when execution ended.
        duration_seconds: Wall-clock time.
        retries_used: Number of retries consumed.
        output: Task output or result data.
        error: Error message if failed.
    """

    task_name: str
    status: TaskStatus
    started_at: float
    completed_at: float
    duration_seconds: float
    retries_used: int = 0
    output: Any = None
    error: str = ""


@dataclass
class MaintenanceTask:
    """A registered maintenance task.

    Attributes:
        name: Unique task identifier.
        description: Human-readable description.
        action: The callable to execute.
        schedule: Scheduling configuration.
        priority: Task priority level.
        enabled: Whether the task is active.
        last_run: Timestamp of last execution.
        last_result: Result of last execution.
        run_count: Total number of executions.
    """

    name: str
    description: str
    action: Callable[[], Any]
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    priority: TaskPriority = TaskPriority.MEDIUM
    enabled: bool = True
    last_run: float = 0.0
    last_result: TaskResult | None = None
    run_count: int = 0


class MaintenanceScheduler:
    """Manages and executes recurring maintenance tasks.

    Provides registration, scheduling, and execution of maintenance
    tasks with retry logic and result tracking.

    Example::

        scheduler = MaintenanceScheduler()
        scheduler.register(MaintenanceTask(
            name="dep_audit",
            description="Check dependencies for CVEs",
            action=lambda: run_dep_audit(),
            schedule=ScheduleConfig(interval_seconds=3600),
        ))
        due = scheduler.get_due_tasks(now=time.time())
        for task in due:
            result = scheduler.execute(task.name)
    """

    def __init__(self) -> None:
        self._tasks: dict[str, MaintenanceTask] = {}
        self._history: list[TaskResult] = []

    def register(self, task: MaintenanceTask) -> None:
        """Register a maintenance task."""
        self._tasks[task.name] = task

    def unregister(self, name: str) -> bool:
        """Unregister a task by name. Returns True if found."""
        return self._tasks.pop(name, None) is not None

    def get_task(self, name: str) -> MaintenanceTask | None:
        """Look up a task by name."""
        return self._tasks.get(name)

    @property
    def task_count(self) -> int:
        """Number of registered tasks."""
        return len(self._tasks)

    def list_tasks(self) -> list[MaintenanceTask]:
        """Return all registered tasks, sorted by priority."""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }
        return sorted(
            self._tasks.values(),
            key=lambda t: priority_order.get(t.priority, 99),
        )

    def get_due_tasks(self, now: float) -> list[MaintenanceTask]:
        """Return tasks that are due for execution.

        A task is due if it is enabled and enough time has elapsed
        since its last run (or it has ``run_on_startup`` and hasn't
        run yet).

        Args:
            now: Current unix timestamp.

        Returns:
            List of due tasks sorted by priority.
        """
        due = []
        for task in self._tasks.values():
            if not task.enabled:
                continue
            if task.last_run == 0.0 and task.schedule.run_on_startup:
                due.append(task)
            elif now - task.last_run >= task.schedule.interval_seconds:
                due.append(task)

        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }
        due.sort(key=lambda t: priority_order.get(t.priority, 99))
        return due

    def execute(self, name: str) -> TaskResult:
        """Execute a maintenance task with retry logic.

        Args:
            name: Name of the task to execute.

        Returns:
            TaskResult with execution details.

        Raises:
            KeyError: If no task exists with the given name.
        """
        task = self._tasks.get(name)
        if task is None:
            raise KeyError(f"No task registered with name '{name}'")

        started = time.time()
        retries = 0
        last_error = ""

        while retries <= task.schedule.max_retries:
            try:
                output = task.action()
                completed = time.time()
                result = TaskResult(
                    task_name=name,
                    status=TaskStatus.COMPLETED,
                    started_at=started,
                    completed_at=completed,
                    duration_seconds=completed - started,
                    retries_used=retries,
                    output=output,
                )
                task.last_run = completed
                task.last_result = result
                task.run_count += 1
                self._history.append(result)
                return result
            except Exception as exc:
                last_error = str(exc)
                retries += 1
                if retries <= task.schedule.max_retries:
                    time.sleep(min(task.schedule.retry_delay_seconds, 0.001))

        completed = time.time()
        result = TaskResult(
            task_name=name,
            status=TaskStatus.FAILED,
            started_at=started,
            completed_at=completed,
            duration_seconds=completed - started,
            retries_used=retries - 1,
            error=last_error,
        )
        task.last_run = completed
        task.last_result = result
        task.run_count += 1
        self._history.append(result)
        return result

    def history(self, limit: int = 50) -> list[TaskResult]:
        """Return execution history, most recent first."""
        return list(reversed(self._history[-limit:]))

    def clear_history(self) -> None:
        """Clear execution history."""
        self._history.clear()
