"""Unit tests for concurrency.result_aggregator module.

Covers:
- AggregateResult dataclass: success_rate property, field defaults
- ResultAggregator: add, add_batch, aggregate, clear, count

Zero-Mock Policy: all tests use real TaskResult objects from task_worker.
"""

import pytest

from codomyrmex.concurrency.result_aggregator import AggregateResult, ResultAggregator
from codomyrmex.concurrency.tasks.task_worker import TaskResult

# ===========================================================================
# AggregateResult dataclass
# ===========================================================================

@pytest.mark.unit
class TestAggregateResult:
    """Tests for AggregateResult dataclass."""

    def test_defaults(self):
        ar = AggregateResult()
        assert ar.total_tasks == 0
        assert ar.successful == 0
        assert ar.failed == 0
        assert ar.results == []
        assert ar.mean_duration_ms == 0.0
        assert ar.worker_stats == {}

    def test_success_rate_zero_tasks(self):
        ar = AggregateResult(total_tasks=0)
        assert ar.success_rate == 0.0

    def test_success_rate_all_success(self):
        ar = AggregateResult(total_tasks=10, successful=10, failed=0)
        assert ar.success_rate == 1.0

    def test_success_rate_partial(self):
        ar = AggregateResult(total_tasks=10, successful=7, failed=3)
        assert abs(ar.success_rate - 0.7) < 0.001

    def test_success_rate_all_failed(self):
        ar = AggregateResult(total_tasks=5, successful=0, failed=5)
        assert ar.success_rate == 0.0


# ===========================================================================
# ResultAggregator - basic operations
# ===========================================================================

@pytest.mark.unit
class TestResultAggregatorBasic:
    """Tests for ResultAggregator add, count, clear."""

    def test_empty_aggregator(self):
        agg = ResultAggregator()
        assert agg.count == 0

    def test_add_single_result(self):
        agg = ResultAggregator()
        result = TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=10.0)
        agg.add(result)
        assert agg.count == 1

    def test_add_multiple_results(self):
        agg = ResultAggregator()
        for i in range(5):
            agg.add(TaskResult(task_id=f"t{i}", worker_id="w1", success=True, duration_ms=1.0))
        assert agg.count == 5

    def test_add_batch(self):
        agg = ResultAggregator()
        batch = [
            TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=5.0),
            TaskResult(task_id="t2", worker_id="w1", success=False, error="fail", duration_ms=3.0),
            TaskResult(task_id="t3", worker_id="w2", success=True, duration_ms=7.0),
        ]
        agg.add_batch(batch)
        assert agg.count == 3

    def test_add_batch_empty(self):
        agg = ResultAggregator()
        agg.add_batch([])
        assert agg.count == 0

    def test_clear(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        agg.add(TaskResult(task_id="t2", worker_id="w1", success=True, duration_ms=1.0))
        assert agg.count == 2
        agg.clear()
        assert agg.count == 0


# ===========================================================================
# ResultAggregator - aggregate method
# ===========================================================================

@pytest.mark.unit
class TestResultAggregatorAggregate:
    """Tests for ResultAggregator.aggregate()."""

    def test_aggregate_empty(self):
        agg = ResultAggregator()
        result = agg.aggregate()
        assert result.total_tasks == 0
        assert result.successful == 0
        assert result.failed == 0
        assert result.mean_duration_ms == 0.0
        assert result.worker_stats == {}
        assert result.results == []

    def test_aggregate_all_success(self):
        agg = ResultAggregator()
        for i in range(3):
            agg.add(TaskResult(
                task_id=f"t{i}",
                worker_id="w1",
                success=True,
                duration_ms=10.0,
            ))
        result = agg.aggregate()
        assert result.total_tasks == 3
        assert result.successful == 3
        assert result.failed == 0
        assert result.mean_duration_ms == 10.0

    def test_aggregate_all_failed(self):
        agg = ResultAggregator()
        for i in range(2):
            agg.add(TaskResult(
                task_id=f"t{i}",
                worker_id="w1",
                success=False,
                error="boom",
                duration_ms=5.0,
            ))
        result = agg.aggregate()
        assert result.total_tasks == 2
        assert result.successful == 0
        assert result.failed == 2

    def test_aggregate_mixed(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=10.0))
        agg.add(TaskResult(task_id="t2", worker_id="w1", success=False, duration_ms=20.0))
        agg.add(TaskResult(task_id="t3", worker_id="w2", success=True, duration_ms=30.0))
        result = agg.aggregate()
        assert result.total_tasks == 3
        assert result.successful == 2
        assert result.failed == 1
        assert abs(result.mean_duration_ms - 20.0) < 0.001

    def test_aggregate_worker_stats(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        agg.add(TaskResult(task_id="t2", worker_id="w1", success=False, duration_ms=1.0))
        agg.add(TaskResult(task_id="t3", worker_id="w2", success=True, duration_ms=1.0))
        agg.add(TaskResult(task_id="t4", worker_id="w2", success=True, duration_ms=1.0))
        result = agg.aggregate()
        assert "w1" in result.worker_stats
        assert "w2" in result.worker_stats
        assert result.worker_stats["w1"]["success"] == 1
        assert result.worker_stats["w1"]["failed"] == 1
        assert result.worker_stats["w2"]["success"] == 2
        assert result.worker_stats["w2"]["failed"] == 0

    def test_aggregate_results_list(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        result = agg.aggregate()
        assert len(result.results) == 1
        assert result.results[0].task_id == "t1"

    def test_aggregate_mean_duration(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=100.0))
        agg.add(TaskResult(task_id="t2", worker_id="w1", success=True, duration_ms=200.0))
        agg.add(TaskResult(task_id="t3", worker_id="w1", success=True, duration_ms=300.0))
        result = agg.aggregate()
        assert result.mean_duration_ms == 200.0

    def test_aggregate_success_rate(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        agg.add(TaskResult(task_id="t2", worker_id="w1", success=False, duration_ms=1.0))
        result = agg.aggregate()
        assert result.success_rate == 0.5

    def test_aggregate_preserves_results_as_copy(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        result = agg.aggregate()
        # The results list should be a new list (not the internal one)
        assert result.results is not agg._results

    def test_aggregate_after_clear(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        agg.clear()
        result = agg.aggregate()
        assert result.total_tasks == 0


# ===========================================================================
# ResultAggregator - edge cases
# ===========================================================================

@pytest.mark.unit
class TestResultAggregatorEdgeCases:
    """Edge case tests for ResultAggregator."""

    def test_single_worker_many_tasks(self):
        agg = ResultAggregator()
        for i in range(100):
            agg.add(TaskResult(
                task_id=f"t{i}",
                worker_id="w1",
                success=i % 3 != 0,
                duration_ms=float(i),
            ))
        result = agg.aggregate()
        assert result.total_tasks == 100
        assert result.worker_stats["w1"]["success"] + result.worker_stats["w1"]["failed"] == 100

    def test_many_workers(self):
        agg = ResultAggregator()
        for i in range(10):
            agg.add(TaskResult(
                task_id=f"t{i}",
                worker_id=f"w{i}",
                success=True,
                duration_ms=1.0,
            ))
        result = agg.aggregate()
        assert len(result.worker_stats) == 10

    def test_add_and_batch_combined(self):
        agg = ResultAggregator()
        agg.add(TaskResult(task_id="t1", worker_id="w1", success=True, duration_ms=1.0))
        agg.add_batch([
            TaskResult(task_id="t2", worker_id="w1", success=True, duration_ms=2.0),
            TaskResult(task_id="t3", worker_id="w1", success=True, duration_ms=3.0),
        ])
        assert agg.count == 3
        result = agg.aggregate()
        assert result.total_tasks == 3
        assert result.mean_duration_ms == 2.0
