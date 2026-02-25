"""Async worker pool with bounded concurrency.

Provides ``AsyncWorkerPool`` — a managed pool of async workers
that uses ``asyncio.Semaphore`` for bounded concurrency.

Usage::

    async with AsyncWorkerPool(max_workers=4) as pool:
        results = await pool.map(process_item, items)
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class TaskResult:
    """Result from a pool task execution."""

    task_id: str
    success: bool
    result: Any = None
    error: str | None = None
    elapsed_ms: float = 0.0


@dataclass
class PoolStats:
    """Aggregate pool statistics."""

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
        """Execute   Init   operations natively."""
        self._max_workers = max_workers
        self._name = name
        self._semaphore = asyncio.Semaphore(max_workers)
        self._stats = PoolStats()
        self._tasks: list[asyncio.Task[Any]] = []
        self._closed = False

    async def __aenter__(self) -> AsyncWorkerPool:
        return self

    async def __aexit__(self, *exc: Any) -> None:
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
            *args: Positional arguments.
            task_id: Optional identifier for tracking.
            **kwargs: Keyword arguments.

        Returns:
            TaskResult with success/error details.
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
            List of TaskResults in input order.
        """
        tasks = [
            self.submit(coro_fn, item, task_id=f"{self._name}-{i}")
            for i, item in enumerate(items)
        ]
        return list(await asyncio.gather(*tasks))

    async def shutdown(self) -> None:
        """Wait for all pending tasks and prevent new submissions."""
        self._closed = True
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()

    @property
    def stats(self) -> PoolStats:
        """Current pool statistics."""
        return self._stats
