"""Tests for Sprint 32: Distributed Task Queue.

Covers TaskQueue (priority, dedup, deadline, dead-letters),
TaskWorker (error isolation), TaskScheduler (strategies),
and ResultAggregator.
"""

import pytest

from codomyrmex.concurrency.result_aggregator import ResultAggregator
from codomyrmex.concurrency.tasks.task_queue import Task, TaskPriority, TaskQueue
from codomyrmex.concurrency.tasks.task_scheduler import (
    SchedulingStrategy,
    TaskScheduler,
)
from codomyrmex.concurrency.tasks.task_worker import TaskResult, TaskWorker

# ─── TaskQueue ────────────────────────────────────────────────────────

class TestTaskQueue:
    """Test suite for TaskQueue."""

    def test_priority_ordering(self):
        """Test functionality: priority ordering."""
        queue = TaskQueue()
        queue.enqueue(Task(task_id="low", priority=TaskPriority.LOW))
        queue.enqueue(Task(task_id="high", priority=TaskPriority.HIGH))
        queue.enqueue(Task(task_id="crit", priority=TaskPriority.CRITICAL))

        assert queue.dequeue().task_id == "crit"
        assert queue.dequeue().task_id == "high"
        assert queue.dequeue().task_id == "low"

    def test_deduplication(self):
        """Test functionality: deduplication."""
        queue = TaskQueue()
        assert queue.enqueue(Task(task_id="a")) is True
        assert queue.enqueue(Task(task_id="a")) is False
        assert queue.pending_count == 1

    def test_ack_completes_task(self):
        """Test functionality: ack completes task."""
        queue = TaskQueue()
        queue.enqueue(Task(task_id="t1"))
        queue.dequeue()
        assert queue.in_flight_count == 1
        queue.ack("t1")
        assert queue.in_flight_count == 0

    def test_nack_requeues(self):
        """Test functionality: nack requeues."""
        queue = TaskQueue()
        queue.enqueue(Task(task_id="t1", max_retries=3))
        queue.dequeue()
        result = queue.nack("t1")
        assert result is True
        assert queue.pending_count == 1

    def test_nack_dead_letters_after_max_retries(self):
        """Test functionality: nack dead letters after max retries."""
        queue = TaskQueue()
        queue.enqueue(Task(task_id="t1", max_retries=1))
        queue.dequeue()
        queue.nack("t1")  # retry_count becomes 1 → dead letter
        assert queue.dead_letter_count == 1

    def test_requeue_dead_letters(self):
        """Test functionality: requeue dead letters."""
        queue = TaskQueue()
        queue.enqueue(Task(task_id="t1", max_retries=1))
        queue.dequeue()
        queue.nack("t1")
        count = queue.requeue_dead_letters()
        assert count == 1
        assert queue.pending_count == 1


# ─── TaskWorker ───────────────────────────────────────────────────────

class TestTaskWorker:
    """Test suite for TaskWorker."""

    def test_process_success(self):
        """Test functionality: process success."""
        worker = TaskWorker(worker_id="w1")
        task = Task(task_id="t1")
        result = worker.process_one(task)
        assert result.success is True
        assert result.worker_id == "w1"

    def test_error_isolation(self):
        """Worker survives task failure."""
        def failing_handler(task):
            raise RuntimeError("boom")

        worker = TaskWorker(worker_id="w1", handler=failing_handler)
        task = Task(task_id="t1")
        result = worker.process_one(task)
        assert result.success is False
        assert "boom" in result.error
        assert worker.tasks_failed == 1

    def test_lifecycle(self):
        """Test functionality: lifecycle."""
        worker = TaskWorker()
        assert worker.is_running is False
        worker.start()
        assert worker.is_running is True
        worker.stop()
        assert worker.is_running is False


# ─── TaskScheduler ───────────────────────────────────────────────────

class TestTaskScheduler:
    """Test suite for TaskScheduler."""

    def test_round_robin(self):
        """Test functionality: round robin."""
        scheduler = TaskScheduler(strategy=SchedulingStrategy.ROUND_ROBIN)
        scheduler.register_worker("w1")
        scheduler.register_worker("w2")
        task = Task(task_id="t1")

        assignments = [scheduler.assign(task) for _ in range(4)]
        assert "w1" in assignments
        assert "w2" in assignments

    def test_least_loaded(self):
        """Test functionality: least loaded."""
        scheduler = TaskScheduler(strategy=SchedulingStrategy.LEAST_LOADED)
        scheduler.register_worker("w1")
        scheduler.register_worker("w2")

        # Load w1
        scheduler.assign(Task(task_id="t1"))
        # Next should go to w2 (least loaded)
        assigned = scheduler.assign(Task(task_id="t2"))
        assert assigned == "w2"

    def test_affinity_routing(self):
        """Test functionality: affinity routing."""
        scheduler = TaskScheduler(strategy=SchedulingStrategy.AFFINITY)
        scheduler.register_worker("w1")
        scheduler.register_worker("w2")
        scheduler.set_affinity("analyze", "w2")

        assigned = scheduler.assign(Task(task_id="t1", task_type="analyze"))
        assert assigned == "w2"

    def test_capability_filter(self):
        """Test functionality: capability filter."""
        scheduler = TaskScheduler()
        scheduler.register_worker("w1", capabilities=["analyze"])
        scheduler.register_worker("w2", capabilities=["deploy"])

        assigned = scheduler.assign(Task(task_id="t1", task_type="deploy"))
        assert assigned == "w2"


# ─── ResultAggregator ───────────────────────────────────────────────

class TestResultAggregator:
    """Test suite for ResultAggregator."""

    def test_aggregate_stats(self):
        """Test functionality: aggregate stats."""
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=100))
        agg.add(TaskResult(task_id="t2", worker_id="w1", success=False, duration_ms=200))
        summary = agg.aggregate()
        assert summary.total_tasks == 2
        assert summary.successful == 1
        assert summary.success_rate == pytest.approx(0.5)
        assert summary.worker_stats["w1"]["success"] == 1
