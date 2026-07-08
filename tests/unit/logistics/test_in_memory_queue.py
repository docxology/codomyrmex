"""
Unit tests for logistics.task.backends.in_memory_queue — Zero-Mock compliant.

Covers: InMemoryQueue (enqueue, dequeue priority ordering, dequeue empty,
schedule future job, get_status, cancel queued / cancel nonexistent,
get_stats, scheduled-job activation on dequeue).
"""

from datetime import datetime, timedelta

import pytest

from codomyrmex.logistics.task.backends.in_memory_queue import InMemoryQueue
from codomyrmex.logistics.task.job import Job, JobStatus


def _make_job(task: str = "do_work", priority: int = 0) -> Job:
    return Job(task=task, priority=priority)


@pytest.mark.unit
class TestInMemoryQueueEnqueue:
    def test_enqueue_returns_job_id(self):
        q = InMemoryQueue()
        job = _make_job()
        result_id = q.enqueue(job)
        assert result_id == job.job_id

    def test_enqueue_stores_job(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        assert q.get_stats()["queue_length"] == 1

    def test_enqueue_multiple_increments_count(self):
        q = InMemoryQueue()
        for _ in range(3):
            q.enqueue(_make_job())
        assert q.get_stats()["queue_length"] == 3

    def test_enqueue_tracks_total_jobs(self):
        q = InMemoryQueue()
        q.enqueue(_make_job())
        q.enqueue(_make_job())
        assert q.get_stats()["total_jobs"] == 2


@pytest.mark.unit
class TestInMemoryQueueDequeue:
    def test_dequeue_empty_returns_none(self):
        q = InMemoryQueue()
        assert q.dequeue() is None

    def test_dequeue_returns_job(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        result = q.dequeue()
        assert result is job

    def test_dequeue_marks_job_running(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        result = q.dequeue()
        assert result.status == JobStatus.RUNNING

    def test_dequeue_decrements_queue_length(self):
        q = InMemoryQueue()
        q.enqueue(_make_job())
        q.dequeue()
        assert q.get_stats()["queue_length"] == 0

    def test_dequeue_higher_priority_first(self):
        """Higher priority int → served first (heap uses -priority)."""
        q = InMemoryQueue()
        low = _make_job("low", priority=1)
        high = _make_job("high", priority=10)
        q.enqueue(low)
        q.enqueue(high)
        first = q.dequeue()
        assert first.task == "high"

    def test_dequeue_order_multiple(self):
        q = InMemoryQueue()
        jobs = [_make_job(f"t{i}", priority=i) for i in range(5)]
        for j in jobs:
            q.enqueue(j)
        results = [q.dequeue() for _ in range(5)]
        priorities = [r.priority for r in results]
        # Should be descending (highest first)
        assert priorities == sorted(priorities, reverse=True)

    def test_dequeue_activates_scheduled_job(self):
        """A scheduled job whose time has passed is activated on dequeue."""
        q = InMemoryQueue()
        job = _make_job()
        past = datetime.now() - timedelta(seconds=1)
        q.schedule(job, when=past)
        result = q.dequeue()
        assert result is job


@pytest.mark.unit
class TestInMemoryQueueSchedule:
    def test_schedule_returns_job_id(self):
        q = InMemoryQueue()
        job = _make_job()
        result_id = q.schedule(job, when=datetime.now() + timedelta(hours=1))
        assert result_id == job.job_id

    def test_schedule_increments_scheduled_count(self):
        q = InMemoryQueue()
        q.schedule(_make_job(), when=datetime.now() + timedelta(hours=1))
        assert q.get_stats()["scheduled_count"] == 1

    def test_scheduled_future_job_not_dequeued_early(self):
        q = InMemoryQueue()
        future = datetime.now() + timedelta(days=1)
        q.schedule(_make_job(), when=future)
        assert q.dequeue() is None

    def test_schedule_tracks_total_jobs(self):
        q = InMemoryQueue()
        q.schedule(_make_job(), when=datetime.now() + timedelta(hours=1))
        assert q.get_stats()["total_jobs"] == 1


@pytest.mark.unit
class TestInMemoryQueueGetStatus:
    def test_get_status_pending_after_enqueue(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        assert q.get_status(job.job_id) == JobStatus.PENDING

    def test_get_status_running_after_dequeue(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        q.dequeue()
        assert q.get_status(job.job_id) == JobStatus.RUNNING

    def test_get_status_unknown_returns_pending(self):
        q = InMemoryQueue()
        assert q.get_status("no-such-id") == JobStatus.PENDING


@pytest.mark.unit
class TestInMemoryQueueCancel:
    def test_cancel_queued_job_returns_true(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        assert q.cancel(job.job_id) is True

    def test_cancel_sets_status_cancelled(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        q.cancel(job.job_id)
        assert q.get_status(job.job_id) == JobStatus.CANCELLED

    def test_cancel_removes_from_queue(self):
        q = InMemoryQueue()
        job = _make_job()
        q.enqueue(job)
        q.cancel(job.job_id)
        assert q.get_stats()["queue_length"] == 0

    def test_cancel_scheduled_job_removes_from_scheduled(self):
        q = InMemoryQueue()
        job = _make_job()
        q.schedule(job, when=datetime.now() + timedelta(hours=1))
        q.cancel(job.job_id)
        assert q.get_stats()["scheduled_count"] == 0

    def test_cancel_nonexistent_returns_false(self):
        q = InMemoryQueue()
        assert q.cancel("no-such-id") is False


@pytest.mark.unit
class TestInMemoryQueueStats:
    def test_stats_initial_all_zero(self):
        q = InMemoryQueue()
        stats = q.get_stats()
        assert stats["queue_length"] == 0
        assert stats["scheduled_count"] == 0
        assert stats["total_jobs"] == 0

    def test_stats_keys_present(self):
        q = InMemoryQueue()
        stats = q.get_stats()
        for k in ("queue_length", "scheduled_count", "total_jobs"):
            assert k in stats

    def test_stats_after_mixed_operations(self):
        q = InMemoryQueue()
        j1 = _make_job()
        j2 = _make_job()
        q.enqueue(j1)
        q.schedule(j2, when=datetime.now() + timedelta(hours=1))
        stats = q.get_stats()
        assert stats["queue_length"] == 1
        assert stats["scheduled_count"] == 1
        assert stats["total_jobs"] == 2
