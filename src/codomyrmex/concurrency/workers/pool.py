"""Async worker pool with bounded concurrency.

Provides ``AsyncWorkerPool`` — a managed pool of async workers
that uses ``asyncio.Semaphore`` for bounded concurrency.

Usage::

    async with AsyncWorkerPool(max_workers=4) as pool:
        results = await pool.map(process_item, items)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self, TypeVar

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger(__name__)

__all__ = ["AsyncWorkerPool", "PoolStats", "TaskResult"]

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class TaskResult:
    """Result from a pool task execution.

    Attributes:
        task_id: Unique identifier for the task.
        success: Whether the task completed successfully.
        result: The return value of the task.
        error: Error message if the task failed.
        elapsed_ms: Time taken to execute the task in milliseconds.
    """

    task_id: str
    success: bool
    result: Any = None
    error: str | None = None
    elapsed_ms: float = 0.0


@dataclass
class PoolStats:
    """Aggregate pool statistics.

    Attributes:
        submitted: Total tasks submitted to the pool.
        completed: Total tasks successfully completed.
        failed: Total tasks that failed.
        total_elapsed_ms: Sum of execution times for all tasks.
    """

    submitted: int = 0
    completed: int = 0
    failed: int = 0
    total_elapsed_ms: float = 0.0


class AsyncWorkerPool:
    """Bounded async worker pool.

    Args:
        max_workers: Maximum concurrent tasks.
        name: Pool name for logging.

    """

    def __init__(self, max_workers: int = 4, *, name: str = "pool"):
        """Initialize worker pool.

        Args:
            max_workers: Maximum number of concurrent async tasks.
            name: Descriptive name for the pool.

        Example:
            >>> pool = AsyncWorkerPool(max_workers=10)
        """
        self._max_workers = max_workers
        self._name = name
        self._semaphore = asyncio.Semaphore(max_workers)
        self._stats = PoolStats()
        self._tasks: list[asyncio.Task[Any]] = []
        self._closed = False

    async def __aenter__(self) -> Self:
        """Enter async context.

        Returns:
            The pool instance.

        Example:
            >>> async with AsyncWorkerPool() as pool:
            ...     pass
        """
        return self

    async def __aexit__(self, *exc: object) -> None:
        """Exit async context and shut down the pool.

        Args:
            *exc: Exception details.

        Example:
            >>> await pool.__aexit__(None, None, None)
        """
        await self.shutdown()

    async def submit(
        self,
        coro_fn: Callable[..., Awaitable[R]],
        *args: Any,
        task_id: str = "",
        **kwargs: Any,
    ) -> TaskResult:
        """Submit a coroutine for execution with bounded concurrency.

        Args:
            coro_fn: Async callable to execute.
            *args: Positional arguments for coro_fn.
            task_id: Optional identifier for tracking.
            **kwargs: Keyword arguments for coro_fn.

        Returns:
            TaskResult with success/error details.

        Raises:
            RuntimeError: If the pool is already shut down.

        Example:
            >>> result = await pool.submit(my_coro, 1, 2, task_id="task-1")
        """
        if self._closed:
            raise RuntimeError(f"Pool {self._name!r} is shut down")

        task_id = task_id or f"{self._name}-{self._stats.submitted}"
        self._stats.submitted += 1

        async with self._semaphore:
            t0 = time.monotonic()
            try:
                result = await coro_fn(*args, **kwargs)
                elapsed = (time.monotonic() - t0) * 1000
                self._stats.completed += 1
                self._stats.total_elapsed_ms += elapsed
                return TaskResult(
                    task_id=task_id, success=True, result=result, elapsed_ms=elapsed
                )
            except Exception as exc:
                elapsed = (time.monotonic() - t0) * 1000
                self._stats.failed += 1
                self._stats.total_elapsed_ms += elapsed
                logger.warning("Pool %s task %s failed: %s", self._name, task_id, exc)
                return TaskResult(
                    task_id=task_id, success=False, error=str(exc), elapsed_ms=elapsed
                )

    async def map(
        self,
        coro_fn: Callable[[T], Awaitable[R]],
        items: list[T],
    ) -> list[TaskResult]:
        """Apply coro_fn to each item concurrently, respecting pool limits.

        Args:
            coro_fn: Async callable taking one argument.
            items: Items to process.

        Returns:
            list of TaskResults in input order.

        Example:
            >>> results = await pool.map(fetch_url, ["url1", "url2"])
        """
        tasks = [
            self.submit(coro_fn, item, task_id=f"{self._name}-{i}")
            for i, item in enumerate(items)
        ]
        return list(await asyncio.gather(*tasks))

    async def shutdown(self) -> None:
        """Wait for all pending tasks and prevent new submissions.

        Example:
            >>> await pool.shutdown()
        """
        self._closed = True
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()

    @property
    def stats(self) -> PoolStats:
        """Current pool statistics.

        Returns:
            PoolStats object.

        Example:
            >>> print(pool.stats.completed)
        """
        return self._stats
