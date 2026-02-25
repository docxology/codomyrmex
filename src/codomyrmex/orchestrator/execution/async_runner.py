"""Async-first parallel runner using native ``asyncio.TaskGroup`` (3.11+).

Provides ``AsyncParallelRunner`` as the next-generation replacement for
``ParallelRunner`` which uses a ``ThreadPoolExecutor``.  Key improvements:

- Native ``asyncio.TaskGroup`` structured concurrency (Python 3.11+)
- ``Semaphore`` for bounded parallelism
- ``fail_fast`` to cancel remaining tasks on first error
- ``on_task_complete`` callback for progress tracking
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable, Coroutine

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------


@dataclass
class AsyncTaskResult:
    """Outcome of a single async task."""

    name: str
    success: bool
    value: Any = None
    error: str | None = None
    error_type: str | None = None
    execution_time: float = 0.0


@dataclass
class AsyncExecutionResult:
    """Aggregated outcome of a parallel execution batch."""

    batch_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    total: int = 0
    passed: int = 0
    failed: int = 0
    cancelled: int = 0
    execution_time: float = 0.0
    results: list[AsyncTaskResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """All tasks passed."""
        return self.failed == 0 and self.cancelled == 0

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict."""
        return {
            "batch_id": self.batch_id,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "execution_time": self.execution_time,
            "success": self.success,
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "value": r.value,
                    "error": r.error,
                    "execution_time": r.execution_time,
                }
                for r in self.results
            ],
        }


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

OnTaskComplete = Callable[[AsyncTaskResult], None]


# ---------------------------------------------------------------------------
# AsyncParallelRunner
# ---------------------------------------------------------------------------


class AsyncParallelRunner:
    """Run async tasks concurrently with bounded parallelism.

    Parameters
    ----------
    max_concurrency:
        Upper bound on simultaneous tasks. ``None`` means unbounded.
    fail_fast:
        When ``True``, cancel all outstanding tasks after the first failure.
    on_task_complete:
        Callback invoked every time a task finishes (success or failure).

    Usage::

        runner = AsyncParallelRunner(max_concurrency=4, fail_fast=True)

        async def fetch(url: str) -> str: ...

        result = await runner.run([
            ("google", fetch, ("https://google.com",)),
            ("github", fetch, ("https://github.com",)),
        ])
    """

    def __init__(
        self,
        *,
        max_concurrency: int | None = None,
        fail_fast: bool = False,
        on_task_complete: OnTaskComplete | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._max_concurrency = max_concurrency
        self._fail_fast = fail_fast
        self._on_task_complete = on_task_complete
        self._semaphore: asyncio.Semaphore | None = (
            asyncio.Semaphore(max_concurrency) if max_concurrency else None
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(
        self,
        tasks: list[
            tuple[
                str,
                Callable[..., Coroutine[Any, Any, Any]],
                tuple[Any, ...],
            ]
        ],
    ) -> AsyncExecutionResult:
        """Execute *tasks* concurrently.

        Parameters
        ----------
        tasks:
            List of ``(name, coroutine_func, args)`` triples.

        Returns
        -------
        AsyncExecutionResult
            Aggregated result for all tasks.
        """
        result = AsyncExecutionResult(total=len(tasks))
        t0 = time.monotonic()

        if not tasks:
            return result

        # If fail_fast, use gather with cancel; otherwise use TaskGroup
        if self._fail_fast:
            await self._run_fail_fast(tasks, result)
        else:
            await self._run_all(tasks, result)

        result.execution_time = time.monotonic() - t0
        logger.info(
            "Batch %s: %d/%d passed in %.2fs",
            result.batch_id,
            result.passed,
            result.total,
            result.execution_time,
        )
        return result

    # ------------------------------------------------------------------
    # Internal — run all tasks
    # ------------------------------------------------------------------

    async def _run_all(
        self,
        tasks: list[tuple[str, Callable, tuple]],
        result: AsyncExecutionResult,
    ) -> None:
        """Run all tasks, collecting results even if some fail."""
        coros = [self._guarded_run(name, coro, args, result) for name, coro, args in tasks]
        await asyncio.gather(*coros)

    async def _run_fail_fast(
        self,
        tasks: list[tuple[str, Callable, tuple]],
        result: AsyncExecutionResult,
    ) -> None:
        """Run tasks using TaskGroup for structured concurrency (fail_fast)."""
        try:
            async with asyncio.TaskGroup() as tg:
                for name, coro, args in tasks:
                    tg.create_task(
                        self._guarded_run(name, coro, args, result),
                        name=name,
                    )
        except* Exception:
            # TaskGroup raises ExceptionGroup on any unhandled failures.
            # _guarded_run already catches per-task errors, so this only
            # fires if _guarded_run itself has a bug — unlikely but safe.
            pass

    # ------------------------------------------------------------------
    # Single-task wrapper
    # ------------------------------------------------------------------

    async def _guarded_run(
        self,
        name: str,
        coro_func: Callable[..., Coroutine[Any, Any, Any]],
        args: tuple[Any, ...],
        batch_result: AsyncExecutionResult,
    ) -> None:
        """Execute a single task, respecting semaphore and recording outcome."""
        t0 = time.monotonic()

        try:
            if self._semaphore:
                async with self._semaphore:
                    value = await coro_func(*args)
            else:
                value = await coro_func(*args)

            task_result = AsyncTaskResult(
                name=name,
                success=True,
                value=value,
                execution_time=time.monotonic() - t0,
            )
            batch_result.passed += 1

        except asyncio.CancelledError:
            task_result = AsyncTaskResult(
                name=name,
                success=False,
                error="Cancelled",
                error_type="CancelledError",
                execution_time=time.monotonic() - t0,
            )
            batch_result.cancelled += 1

        except Exception as exc:
            task_result = AsyncTaskResult(
                name=name,
                success=False,
                error=str(exc),
                error_type=type(exc).__name__,
                execution_time=time.monotonic() - t0,
            )
            batch_result.failed += 1
            logger.warning("Task %s failed: %s", name, exc)

            if self._fail_fast:
                raise  # Let TaskGroup propagate cancellation

        batch_result.results.append(task_result)

        if self._on_task_complete:
            try:
                self._on_task_complete(task_result)
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
                logger.debug("on_task_complete callback error for %s", name)


__all__ = [
    "AsyncParallelRunner",
    "AsyncTaskResult",
    "AsyncExecutionResult",
    "OnTaskComplete",
]
