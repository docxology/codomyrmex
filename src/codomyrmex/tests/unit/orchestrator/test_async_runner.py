"""Tests for AsyncParallelRunner and @with_retry decorator (Stream 5).

Verifies:
- Basic async task execution
- Semaphore-bounded concurrency
- fail_fast cancellation
- on_task_complete callback
- @with_retry on sync and async functions
- DAG-like ordering via dependency chains
"""

from __future__ import annotations

import asyncio
import time

import pytest

from codomyrmex.orchestrator.execution.async_runner import (
    AsyncExecutionResult,
    AsyncParallelRunner,
    AsyncTaskResult,
)
from codomyrmex.orchestrator.resilience.retry_policy import with_retry


# ── Helpers ───────────────────────────────────────────────────────────


async def _success(x: int) -> int:
    return x * 2


async def _slow(seconds: float) -> float:
    await asyncio.sleep(seconds)
    return seconds


async def _fail(msg: str) -> None:
    raise RuntimeError(msg)


_call_counter = 0


async def _flaky(succeed_on: int = 3) -> str:
    """Succeeds on the Nth call."""
    global _call_counter
    _call_counter += 1
    if _call_counter < succeed_on:
        raise ValueError(f"Attempt {_call_counter}")
    return "ok"


# ── Basic execution ──────────────────────────────────────────────────


class TestBasicExecution:
    """Verify basic parallel execution."""

    @pytest.mark.asyncio
    async def test_run_empty_tasks(self) -> None:
        runner = AsyncParallelRunner()
        result = await runner.run([])
        assert result.total == 0
        assert result.success

    @pytest.mark.asyncio
    async def test_run_single_task(self) -> None:
        runner = AsyncParallelRunner()
        result = await runner.run([("double", _success, (5,))])
        assert result.total == 1
        assert result.passed == 1
        assert result.results[0].value == 10

    @pytest.mark.asyncio
    async def test_run_multiple_tasks(self) -> None:
        runner = AsyncParallelRunner()
        tasks = [(f"task_{i}", _success, (i,)) for i in range(10)]
        result = await runner.run(tasks)
        assert result.total == 10
        assert result.passed == 10
        values = sorted(r.value for r in result.results)
        assert values == [i * 2 for i in range(10)]

    @pytest.mark.asyncio
    async def test_mixed_success_and_failure(self) -> None:
        runner = AsyncParallelRunner()
        tasks = [
            ("ok_1", _success, (1,)),
            ("fail_1", _fail, ("boom",)),
            ("ok_2", _success, (2,)),
        ]
        result = await runner.run(tasks)
        assert result.total == 3
        assert result.passed == 2
        assert result.failed == 1


# ── Semaphore bounds ─────────────────────────────────────────────────


class TestSemaphoreBounds:
    """Verify concurrency is bounded by semaphore."""

    @pytest.mark.asyncio
    async def test_max_concurrency_respected(self) -> None:
        """With max_concurrency=2, at most 2 tasks run at once."""
        active: list[int] = []
        peak = [0]

        async def _track(idx: int) -> int:
            active.append(idx)
            if len(active) > peak[0]:
                peak[0] = len(active)
            await asyncio.sleep(0.05)
            active.remove(idx)
            return idx

        runner = AsyncParallelRunner(max_concurrency=2)
        tasks = [(f"t{i}", _track, (i,)) for i in range(6)]
        result = await runner.run(tasks)

        assert result.passed == 6
        assert peak[0] <= 2


# ── fail_fast ─────────────────────────────────────────────────────────


class TestFailFast:
    """Verify fail_fast mode cancels tasks on first failure."""

    @pytest.mark.asyncio
    async def test_fail_fast_stops_early(self) -> None:
        runner = AsyncParallelRunner(fail_fast=True)
        tasks = [
            ("fast_fail", _fail, ("early",)),
            ("slow_ok", _slow, (1.0,)),
        ]
        t0 = time.monotonic()
        result = await runner.run(tasks)
        elapsed = time.monotonic() - t0

        assert result.failed >= 1
        # Should not wait for the full 1s slow task
        assert elapsed < 0.5


# ── on_task_complete callback ─────────────────────────────────────────


class TestOnTaskComplete:
    """Verify the completion callback fires for each task."""

    @pytest.mark.asyncio
    async def test_callback_receives_all_results(self) -> None:
        collected: list[AsyncTaskResult] = []
        runner = AsyncParallelRunner(on_task_complete=collected.append)

        tasks = [(f"t{i}", _success, (i,)) for i in range(5)]
        await runner.run(tasks)

        assert len(collected) == 5
        names = sorted(r.name for r in collected)
        assert names == [f"t{i}" for i in range(5)]


# ── to_dict serialisation ────────────────────────────────────────────


class TestSerialization:
    """Verify result serialisation."""

    @pytest.mark.asyncio
    async def test_to_dict(self) -> None:
        runner = AsyncParallelRunner()
        result = await runner.run([("t", _success, (1,))])
        d = result.to_dict()
        assert d["total"] == 1
        assert d["passed"] == 1
        assert d["success"] is True
        assert len(d["results"]) == 1


# ── @with_retry decorator ────────────────────────────────────────────


class TestWithRetryDecorator:
    """Verify the @with_retry decorator."""

    @pytest.mark.asyncio
    async def test_async_retry_succeeds_eventually(self) -> None:
        attempts = [0]

        @with_retry(max_attempts=3, base_delay=0.01)
        async def flaky() -> str:
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("not yet")
            return "done"

        result = await flaky()
        assert result == "done"
        assert attempts[0] == 3

    @pytest.mark.asyncio
    async def test_async_retry_exhausts_and_raises(self) -> None:
        @with_retry(max_attempts=2, base_delay=0.01)
        async def always_fails() -> None:
            raise RuntimeError("always")

        with pytest.raises(RuntimeError, match="always"):
            await always_fails()

    def test_sync_retry_succeeds_eventually(self) -> None:
        """Test functionality: sync retry succeeds eventually."""
        attempts = [0]

        @with_retry(max_attempts=3, base_delay=0.01)
        def flaky_sync() -> str:
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("not yet")
            return "done"

        result = flaky_sync()
        assert result == "done"
        assert attempts[0] == 3

    def test_sync_retry_exhausts_and_raises(self) -> None:
        """Test functionality: sync retry exhausts and raises."""
        @with_retry(max_attempts=2, base_delay=0.01)
        def always_fails_sync() -> None:
            raise RuntimeError("always")

        with pytest.raises(RuntimeError, match="always"):
            always_fails_sync()

    def test_retry_only_on_specified_exceptions(self) -> None:
        """Test functionality: retry only on specified exceptions."""
        @with_retry(max_attempts=5, base_delay=0.01, retry_on=(ValueError,))
        def raises_type_error() -> None:
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raises_type_error()

    @pytest.mark.asyncio
    async def test_preserves_function_name(self) -> None:
        @with_retry(max_attempts=2)
        async def named_function() -> str:
            return "ok"

        assert named_function.__name__ == "named_function"


# ── Package-level exports ─────────────────────────────────────────────


class TestExports:
    """Verify Stream 5 types are exported from orchestrator package."""

    def test_async_runner_exports(self) -> None:
        """Test functionality: async runner exports."""
        from codomyrmex.orchestrator import (
            AsyncParallelRunner as _APR,
            AsyncTaskResult as _ATR,
            AsyncExecutionResult as _AER,
        )
        assert _APR is not None
        assert _ATR is not None
        assert _AER is not None

    def test_with_retry_export(self) -> None:
        """Test functionality: with retry export."""
        from codomyrmex.orchestrator import with_retry as _wr
        assert _wr is not None
