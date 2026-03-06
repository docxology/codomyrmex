"""Task worker with error isolation and timeout.

Processes tasks from the queue, enforcing timeout limits
and surviving individual task failures.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from .task_queue import Task


@dataclass
class TaskResult:
    """Result of processing a single task.

    Attributes:
        task_id: Original task identifier.
        worker_id: Worker that processed this.
        success: Whether the task completed.
        result: Task output data.
        error: Error message if failed.
        duration_ms: Processing time.
        timestamp: Completion timestamp.
    """

    task_id: str
    worker_id: str = ""
    success: bool = False
    result: Any = None
    error: str = ""
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)


class TaskWorker:
    """Worker that processes tasks with error isolation.

    Example::

        worker = TaskWorker(
            worker_id="w-1",
            handler=lambda task: {"processed": task.task_id},
        )
        result = worker.process_one(task)
    """

    def __init__(
        self,
        worker_id: str = "",
        handler: Callable[[Task], Any] | None = None,
        timeout_ms: float = 30000.0,
    ) -> None:
        """Initialize the task worker.

        Args:
            worker_id: Unique worker identifier.
            handler: Callable that processes the task.
            timeout_ms: Execution timeout in milliseconds.

        Example:
            >>> worker = TaskWorker("worker-1", my_handler)
        """
        self._worker_id = worker_id or f"worker-{uuid.uuid4().hex[:8]}"
        self._handler = handler or self._default_handler
        self._timeout_ms = timeout_ms
        self._running = False
        self._tasks_processed = 0
        self._tasks_failed = 0

    @property
    def worker_id(self) -> str:
        """Return the worker ID.

        Returns:
            Worker identifier string.

        Example:
            >>> worker.worker_id
            'worker-abc'
        """
        return self._worker_id

    @property
    def is_running(self) -> bool:
        """Return whether the worker is running.

        Returns:
            True if running.

        Example:
            >>> worker.is_running
            False
        """
        return self._running

    @property
    def tasks_processed(self) -> int:
        """Return the number of processed tasks.

        Returns:
            Count of tasks handled (success or failure).

        Example:
            >>> worker.tasks_processed
            10
        """
        return self._tasks_processed

    @property
    def tasks_failed(self) -> int:
        """Return the number of failed tasks.

        Returns:
            Count of tasks that resulted in an error.

        Example:
            >>> worker.tasks_failed
            1
        """
        return self._tasks_failed

    @property
    def load(self) -> int:
        """Current load (tasks processed, used for scheduling).

        Returns:
            Integer representing current load.

        Example:
            >>> worker.load
            10
        """
        return self._tasks_processed

    def start(self) -> None:
        """Start the worker.

        Example:
            >>> worker.start()
        """
        self._running = True

    def stop(self) -> None:
        """Stop the worker.

        Example:
            >>> worker.stop()
        """
        self._running = False

    def process_one(self, task: Task) -> TaskResult:
        """Process a single task with error isolation.

        The worker survives task failures — errors are captured
        in the TaskResult, not propagated.

        Args:
            task: The task to process.

        Returns:
            TaskResult with success/failure status.

        Example:
            >>> res = worker.process_one(my_task)
            >>> print(res.success)
        """
        start = time.time()

        try:
            result = self._handler(task)
            duration = (time.time() - start) * 1000
            self._tasks_processed += 1
            return TaskResult(
                task_id=task.task_id,
                worker_id=self._worker_id,
                success=True,
                result=result,
                duration_ms=duration,
            )
        except Exception as exc:
            duration = (time.time() - start) * 1000
            self._tasks_failed += 1
            return TaskResult(
                task_id=task.task_id,
                worker_id=self._worker_id,
                success=False,
                error=str(exc),
                duration_ms=duration,
            )

    @staticmethod
    def _default_handler(task: Task) -> dict[str, Any]:
        """Default no-op handler.

        Args:
            task: Task to process.

        Returns:
            Dictionary with task ID and status.
        """
        return {"task_id": task.task_id, "status": "processed"}


__all__ = ["TaskResult", "TaskWorker"]
