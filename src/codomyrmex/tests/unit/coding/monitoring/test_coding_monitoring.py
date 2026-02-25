"""Tests for coding.monitoring submodule.

Tests ExecutionMonitor, ResourceMonitor, and MetricsCollector
using real implementations with no mocks.
"""

import time

import pytest

from codomyrmex.coding.monitoring import (
    ExecutionMonitor,
    MetricsCollector,
    ResourceMonitor,
)


@pytest.mark.unit
class TestExecutionMonitor:
    """Tests for ExecutionMonitor.start_execution / end_execution / get_execution_stats."""

    def setup_method(self):
        self.monitor = ExecutionMonitor()

    def test_initial_state_has_empty_executions(self):
        """ExecutionMonitor starts with empty executions list."""
        assert self.monitor.executions == []
        assert self.monitor.start_time is None
        assert self.monitor.end_time is None

    def test_start_execution_appends_entry(self):
        """start_execution appends an entry with correct fields."""
        self.monitor.start_execution("exec-001", "python", 42)
        assert len(self.monitor.executions) == 1
        entry = self.monitor.executions[0]
        assert entry["execution_id"] == "exec-001"
        assert entry["language"] == "python"
        assert entry["code_length"] == 42
        assert entry["status"] == "running"
        assert entry["start_time"] is not None

    def test_end_execution_updates_status_and_timing(self):
        """end_execution updates the matching entry status and adds timing."""
        self.monitor.start_execution("exec-002", "javascript", 100)
        self.monitor.end_execution("exec-002", "success", {"output": "ok"})
        entry = self.monitor.executions[0]
        assert entry["status"] == "success"
        assert "execution_time" in entry
        assert entry["execution_time"] >= 0
        assert entry["result"] == {"output": "ok"}

    def test_end_execution_without_result(self):
        """end_execution works without an explicit result dict."""
        self.monitor.start_execution("exec-003", "python", 10)
        self.monitor.end_execution("exec-003", "error")
        entry = self.monitor.executions[0]
        assert entry["status"] == "error"
        assert "result" not in entry

    def test_get_execution_stats_empty(self):
        """get_execution_stats returns zeros when no executions recorded."""
        stats = self.monitor.get_execution_stats()
        assert stats["total_executions"] == 0
        assert stats["average_execution_time"] == 0
        assert stats["success_count"] == 0
        assert stats["error_count"] == 0

    def test_get_execution_stats_with_completed_executions(self):
        """get_execution_stats correctly aggregates completed executions."""
        self.monitor.start_execution("e1", "python", 10)
        time.sleep(0.01)
        self.monitor.end_execution("e1", "success")
        self.monitor.start_execution("e2", "python", 20)
        self.monitor.end_execution("e2", "error")

        stats = self.monitor.get_execution_stats()
        assert stats["total_executions"] == 2
        assert stats["success_count"] == 1
        assert stats["error_count"] == 1
        assert stats["average_execution_time"] >= 0

    def test_multiple_executions_tracked_independently(self):
        """Multiple execution IDs are tracked independently."""
        self.monitor.start_execution("exec-A", "python", 5)
        self.monitor.start_execution("exec-B", "python", 10)
        self.monitor.end_execution("exec-A", "success")
        self.monitor.end_execution("exec-B", "error")

        exec_a = next(e for e in self.monitor.executions if e["execution_id"] == "exec-A")
        exec_b = next(e for e in self.monitor.executions if e["execution_id"] == "exec-B")
        assert exec_a["status"] == "success"
        assert exec_b["status"] == "error"

    def test_stats_distinguishes_completed_from_running(self):
        """Stats only counts completed executions for timing averages."""
        self.monitor.start_execution("running-1", "python", 5)
        # Don't end this one
        self.monitor.start_execution("done-1", "python", 10)
        self.monitor.end_execution("done-1", "success")

        stats = self.monitor.get_execution_stats()
        assert stats["total_executions"] == 2
        assert stats["completed_executions"] == 1


@pytest.mark.unit
class TestResourceMonitor:
    """Tests for ResourceMonitor.start_monitoring / update_monitoring / get_resource_usage."""

    def setup_method(self):
        self.monitor = ResourceMonitor()

    def test_initial_state(self):
        """ResourceMonitor starts with None start_time."""
        assert self.monitor.start_time is None
        assert self.monitor.cpu_usage == []

    def test_start_monitoring_sets_start_time(self):
        """start_monitoring records a numeric start_time."""
        before = time.time()
        self.monitor.start_monitoring()
        after = time.time()
        assert self.monitor.start_time is not None
        assert before <= self.monitor.start_time <= after

    def test_get_resource_usage_before_start(self):
        """get_resource_usage before start returns zero execution_time."""
        usage = self.monitor.get_resource_usage()
        assert usage["execution_time_seconds"] == 0
        assert "memory_start_mb" in usage
        assert "memory_peak_mb" in usage
        assert "cpu_samples" in usage

    def test_get_resource_usage_after_start(self):
        """get_resource_usage after start returns positive execution_time."""
        self.monitor.start_monitoring()
        time.sleep(0.05)
        usage = self.monitor.get_resource_usage()
        assert usage["execution_time_seconds"] > 0

    def test_update_monitoring_does_not_raise(self):
        """update_monitoring does not raise regardless of psutil availability."""
        self.monitor.start_monitoring()
        self.monitor.update_monitoring()
        usage = self.monitor.get_resource_usage()
        assert usage["cpu_samples"] >= 0

    def test_resource_usage_returns_correct_types(self):
        """Resource usage values are numeric (int or float)."""
        self.monitor.start_monitoring()
        usage = self.monitor.get_resource_usage()
        assert isinstance(usage["execution_time_seconds"], (int, float))
        assert isinstance(usage["memory_start_mb"], (int, float))
        assert isinstance(usage["memory_peak_mb"], (int, float))
        assert isinstance(usage["cpu_samples"], int)
        assert isinstance(usage["cpu_average_percent"], (int, float))
        assert isinstance(usage["cpu_peak_percent"], (int, float))


@pytest.mark.unit
class TestCodingMetricsCollector:
    """Tests for coding.monitoring.MetricsCollector."""

    def setup_method(self):
        self.collector = MetricsCollector()

    def test_empty_summary_returns_zeros(self):
        """get_summary returns zeros with no recorded executions."""
        summary = self.collector.get_summary()
        assert summary["total_executions"] == 0
        assert summary["success_rate"] == 0
        assert summary["average_execution_time"] == 0

    def test_record_execution_populates_metrics(self):
        """record_execution stores execution data for later summary."""
        self.collector.record_execution({
            "language": "python",
            "status": "success",
            "execution_time": 1.5,
            "exit_code": 0,
        })
        summary = self.collector.get_summary()
        assert summary["total_executions"] == 1
        assert summary["success_count"] == 1

    def test_summary_aggregates_multiple_executions(self):
        """get_summary correctly computes rates across multiple executions."""
        self.collector.record_execution({
            "language": "python",
            "status": "success",
            "execution_time": 1.5,
        })
        self.collector.record_execution({
            "language": "python",
            "status": "error",
            "execution_time": 0.2,
        })
        summary = self.collector.get_summary()
        assert summary["total_executions"] == 2
        assert summary["success_count"] == 1
        assert summary["error_count"] == 1
        assert abs(summary["success_rate"] - 50.0) < 0.01
        assert summary["average_execution_time"] > 0

    def test_get_language_stats_groups_by_language(self):
        """get_language_stats groups execution counts by programming language."""
        self.collector.record_execution({"language": "python", "status": "success", "execution_time": 1.0})
        self.collector.record_execution({"language": "python", "status": "error", "execution_time": 0.5})
        self.collector.record_execution({"language": "javascript", "status": "success", "execution_time": 2.0})

        stats = self.collector.get_language_stats()
        assert "python" in stats
        assert "javascript" in stats
        assert stats["python"]["count"] == 2
        assert stats["javascript"]["count"] == 1
        assert stats["python"]["success_count"] == 1
        assert stats["python"]["error_count"] == 1

    def test_clear_resets_all_metrics(self):
        """clear() removes all recorded metrics."""
        self.collector.record_execution({"language": "python", "status": "success", "execution_time": 1.0})
        self.collector.clear()
        summary = self.collector.get_summary()
        assert summary["total_executions"] == 0

    def test_language_stats_computes_averages(self):
        """Language stats include average_execution_time per language."""
        self.collector.record_execution({"language": "python", "status": "success", "execution_time": 2.0})
        self.collector.record_execution({"language": "python", "status": "success", "execution_time": 4.0})
        stats = self.collector.get_language_stats()
        assert abs(stats["python"]["average_execution_time"] - 3.0) < 0.01
