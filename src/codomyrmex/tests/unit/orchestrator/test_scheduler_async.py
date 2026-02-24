"""Tests for AsyncScheduler (Stream 5).

Verifies:
- Job scheduling and execution
- Priority-based ordering
- Semaphore-bounded concurrency
- EventBus lifecycle events
- Metrics tracking
- Job cancellation
"""

from __future__ import annotations

import asyncio

import pytest

from codomyrmex.orchestrator.execution.async_scheduler import (
    AsyncJob,
    AsyncJobStatus,
    AsyncScheduler,
    SchedulerMetrics,
)


# ── Helpers ───────────────────────────────────────────────────────────


async def _double(x: int) -> int:
    return x * 2


async def _slow(seconds: float) -> float:
    await asyncio.sleep(seconds)
    return seconds


async def _fail_job() -> None:
    raise RuntimeError("job failed")


# ── Basic scheduling ─────────────────────────────────────────────────


class TestBasicScheduling:
    """Verify basic job scheduling and execution."""

    @pytest.mark.asyncio
    async def test_schedule_and_run_single_job(self) -> None:
        scheduler = AsyncScheduler()
        job_id = scheduler.schedule(_double, args=(5,), name="double_5")
        results = await scheduler.run_all()
        assert job_id in results
        assert results[job_id].result == 10
        assert results[job_id].status == AsyncJobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_schedule_multiple_jobs(self) -> None:
        scheduler = AsyncScheduler()
        ids = [scheduler.schedule(_double, args=(i,), name=f"job_{i}") for i in range(5)]
        results = await scheduler.run_all()
        assert len(results) == 5
        for i, jid in enumerate(ids):
            assert results[jid].result == i * 2

    @pytest.mark.asyncio
    async def test_run_all_no_pending_jobs(self) -> None:
        scheduler = AsyncScheduler()
        results = await scheduler.run_all()
        assert results == {}


# ── Priority ordering ────────────────────────────────────────────────


class TestPriorityOrdering:
    """Verify priority-based execution ordering."""

    @pytest.mark.asyncio
    async def test_lower_priority_runs_first(self) -> None:
        """Jobs with lower priority number get higher execution priority."""
        execution_order: list[str] = []

        async def _track(name: str) -> str:
            execution_order.append(name)
            return name

        # Use max_concurrency=1 to force sequential execution
        scheduler = AsyncScheduler(max_concurrency=1)
        scheduler.schedule(_track, args=("low",), priority=10, name="low_priority")
        scheduler.schedule(_track, args=("high",), priority=1, name="high_priority")
        scheduler.schedule(_track, args=("med",), priority=5, name="med_priority")

        await scheduler.run_all()

        # With concurrency=1, TaskGroup doesn't guarantee exact order,
        # but run_all sorts by priority before creating tasks.
        # The first task created should be "high", then "med", then "low".
        assert execution_order[0] == "high"

    @pytest.mark.asyncio
    async def test_priority_comparison(self) -> None:
        """AsyncJob __lt__ works correctly for sorting."""
        job_a = AsyncJob(name="a", priority=1)
        job_b = AsyncJob(name="b", priority=5)
        assert job_a < job_b
        assert not job_b < job_a


# ── Concurrency bounds ───────────────────────────────────────────────


class TestConcurrencyBounds:
    """Verify semaphore limits concurrent execution."""

    @pytest.mark.asyncio
    async def test_max_concurrency_is_respected(self) -> None:
        active: list[int] = []
        peak = [0]

        async def _track(idx: int) -> int:
            active.append(idx)
            if len(active) > peak[0]:
                peak[0] = len(active)
            await asyncio.sleep(0.05)
            active.remove(idx)
            return idx

        scheduler = AsyncScheduler(max_concurrency=2)
        for i in range(6):
            scheduler.schedule(_track, args=(i,), name=f"job_{i}")

        await scheduler.run_all()
        assert peak[0] <= 2


# ── Error handling ────────────────────────────────────────────────────


class TestErrorHandling:
    """Verify failed jobs are recorded correctly."""

    @pytest.mark.asyncio
    async def test_failed_job_records_error(self) -> None:
        scheduler = AsyncScheduler()
        job_id = scheduler.schedule(_fail_job, name="bad_job")

        # run_all uses TaskGroup — a failing task raises ExceptionGroup
        try:
            await scheduler.run_all()
        except BaseException:
            pass

        job = scheduler.get_job(job_id)
        assert job is not None
        assert job.status == AsyncJobStatus.FAILED
        assert job.error is not None
        assert "job failed" in job.error


# ── Metrics ───────────────────────────────────────────────────────────


class TestMetrics:
    """Verify scheduler metrics tracking."""

    @pytest.mark.asyncio
    async def test_metrics_track_completions(self) -> None:
        scheduler = AsyncScheduler()
        for i in range(3):
            scheduler.schedule(_double, args=(i,), name=f"j{i}")

        await scheduler.run_all()
        m = scheduler.metrics
        assert m.jobs_scheduled == 3
        assert m.jobs_completed == 3
        assert m.jobs_failed == 0
        assert m.total_execution_time > 0

    def test_metrics_to_dict(self) -> None:
        """Test functionality: metrics to dict."""
        m = SchedulerMetrics(jobs_scheduled=5, jobs_completed=3, jobs_failed=2)
        d = m.to_dict()
        assert d["jobs_scheduled"] == 5
        assert d["jobs_completed"] == 3
        assert d["jobs_failed"] == 2

    @pytest.mark.asyncio
    async def test_metrics_track_failures(self) -> None:
        scheduler = AsyncScheduler()
        scheduler.schedule(_fail_job, name="bad")

        try:
            await scheduler.run_all()
        except BaseException:
            pass

        assert scheduler.metrics.jobs_failed == 1


# ── Job management ───────────────────────────────────────────────────


class TestJobManagement:
    """Verify job listing, retrieval, and cancellation."""

    def test_list_jobs(self) -> None:
        """Test functionality: list jobs."""
        scheduler = AsyncScheduler()
        scheduler.schedule(_double, args=(1,), name="a")
        scheduler.schedule(_double, args=(2,), name="b")

        jobs = scheduler.list_jobs()
        assert len(jobs) == 2

    def test_list_jobs_by_status(self) -> None:
        """Test functionality: list jobs by status."""
        scheduler = AsyncScheduler()
        scheduler.schedule(_double, args=(1,), name="a")
        jid = scheduler.schedule(_double, args=(2,), name="b")
        scheduler.cancel(jid)

        pending = scheduler.list_jobs(status=AsyncJobStatus.PENDING)
        cancelled = scheduler.list_jobs(status=AsyncJobStatus.CANCELLED)
        assert len(pending) == 1
        assert len(cancelled) == 1

    def test_cancel_pending_job(self) -> None:
        """Test functionality: cancel pending job."""
        scheduler = AsyncScheduler()
        jid = scheduler.schedule(_double, args=(1,), name="cancel_me")
        assert scheduler.cancel(jid) is True

        job = scheduler.get_job(jid)
        assert job is not None
        assert job.status == AsyncJobStatus.CANCELLED

    def test_cancel_nonexistent_job(self) -> None:
        """Test functionality: cancel nonexistent job."""
        scheduler = AsyncScheduler()
        assert scheduler.cancel("nonexistent") is False

    @pytest.mark.asyncio
    async def test_cancelled_job_not_executed(self) -> None:
        scheduler = AsyncScheduler()
        jid = scheduler.schedule(_double, args=(1,), name="cancelled")
        scheduler.cancel(jid)

        results = await scheduler.run_all()
        assert jid not in results  # Cancelled jobs are filtered out


# ── EventBus integration ─────────────────────────────────────────────


class TestEventBusIntegration:
    """Verify EventBus lifecycle events are emitted."""

    @pytest.mark.asyncio
    async def test_events_emitted_on_schedule_and_run(self) -> None:
        events: list[dict] = []

        class FakeEventBus:
            def publish(self, event):
                events.append({"type": getattr(event.event_type, "value", str(event.event_type)), "data": event.data})

        scheduler = AsyncScheduler(event_bus=FakeEventBus())
        scheduler.schedule(_double, args=(1,), name="test_job")
        await scheduler.run_all()

        event_types = [e["type"] for e in events]
        assert "job.scheduled" in event_types
        assert "job.started" in event_types
        assert "job.completed" in event_types

    @pytest.mark.asyncio
    async def test_job_failed_event(self) -> None:
        events: list[dict] = []

        class FakeEventBus:
            def publish(self, event):
                events.append({"type": getattr(event.event_type, "value", str(event.event_type)), "data": event.data})

        scheduler = AsyncScheduler(event_bus=FakeEventBus())
        scheduler.schedule(_fail_job, name="bad_job")

        try:
            await scheduler.run_all()
        except BaseException:
            pass

        event_types = [e["type"] for e in events]
        assert "job.failed" in event_types


# ── Package exports ───────────────────────────────────────────────────


class TestExports:
    """Verify Stream 5 scheduler types are exported."""

    def test_async_scheduler_exports(self) -> None:
        """Test functionality: async scheduler exports."""
        from codomyrmex.orchestrator import (
            AsyncScheduler as _AS,
            AsyncJob as _AJ,
            AsyncJobStatus as _AJS,
            SchedulerMetrics as _SM,
        )
        assert _AS is not None
        assert _AJ is not None
        assert _AJS is not None
        assert _SM is not None
