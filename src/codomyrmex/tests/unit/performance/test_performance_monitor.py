"""Unit tests for codomyrmex.performance.monitoring.performance_monitor.

Tests cover: PerformanceMetrics, SystemMetrics, SystemMonitor,
PerformanceMonitor, decorators, context managers, and module-level helpers.
Zero-mock policy: all objects are real instances.
"""

import json
import time

import pytest

from codomyrmex.performance.monitoring.performance_monitor import (
    HAS_PSUTIL,
    PerformanceMetrics,
    PerformanceMonitor,
    SystemMetrics,
    SystemMonitor,
    clear_performance_metrics,
    get_performance_stats,
    get_system_metrics,
    monitor_performance,
    performance_context,
    profile_function,
    profile_memory_usage,
    track_resource_usage,
)

# ---------------------------------------------------------------------------
# Dataclass tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPerformanceMetrics:
    """Tests for the PerformanceMetrics dataclass."""

    def test_basic_construction(self):
        m = PerformanceMetrics(
            function_name="foo",
            execution_time=1.5,
            memory_usage_mb=100.0,
            cpu_percent=25.0,
        )
        assert m.function_name == "foo"
        assert m.execution_time == 1.5
        assert m.memory_usage_mb == 100.0
        assert m.cpu_percent == 25.0
        assert isinstance(m.timestamp, float)
        assert m.metadata == {}

    def test_custom_metadata(self):
        m = PerformanceMetrics(
            function_name="bar",
            execution_time=0.1,
            memory_usage_mb=50.0,
            cpu_percent=10.0,
            metadata={"key": "value"},
        )
        assert m.metadata == {"key": "value"}

    def test_explicit_timestamp(self):
        ts = 1000000.0
        m = PerformanceMetrics(
            function_name="t",
            execution_time=0.0,
            memory_usage_mb=0.0,
            cpu_percent=0.0,
            timestamp=ts,
        )
        assert m.timestamp == ts


@pytest.mark.unit
class TestSystemMetrics:
    """Tests for the SystemMetrics dataclass."""

    def test_basic_construction(self):
        s = SystemMetrics(
            cpu_percent=10.0,
            memory_percent=50.0,
            memory_used_mb=4096.0,
            memory_total_mb=8192.0,
            disk_usage_percent=60.0,
            disk_free_gb=100.0,
            network_bytes_sent=1024,
            network_bytes_recv=2048,
        )
        assert s.cpu_percent == 10.0
        assert s.memory_percent == 50.0
        assert s.memory_used_mb == 4096.0
        assert s.memory_total_mb == 8192.0
        assert s.disk_usage_percent == 60.0
        assert s.disk_free_gb == 100.0
        assert s.network_bytes_sent == 1024
        assert s.network_bytes_recv == 2048
        assert isinstance(s.timestamp, float)

    def test_zero_values(self):
        s = SystemMetrics(0, 0, 0, 0, 0, 0, 0, 0)
        assert s.cpu_percent == 0
        assert s.network_bytes_recv == 0


# ---------------------------------------------------------------------------
# SystemMonitor tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSystemMonitor:
    """Tests for the SystemMonitor class."""

    def test_init_default_interval(self):
        mon = SystemMonitor()
        assert mon.interval == 1.0
        assert mon._monitoring is False
        assert mon._monitor_thread is None

    def test_init_custom_interval(self):
        mon = SystemMonitor(interval=0.5)
        assert mon.interval == 0.5

    @pytest.mark.skipif(not HAS_PSUTIL, reason="Requires psutil")
    def test_get_current_metrics_returns_system_metrics(self):
        mon = SystemMonitor()
        result = mon.get_current_metrics()
        assert isinstance(result, SystemMetrics)
        assert result.memory_total_mb > 0

    def test_get_current_metrics_without_psutil_returns_zeros(self):
        """When psutil is missing the fallback returns all-zero metrics."""
        if HAS_PSUTIL:
            pytest.skip("psutil is installed; cannot test no-psutil path directly")
        mon = SystemMonitor()
        result = mon.get_current_metrics()
        assert result.cpu_percent == 0
        assert result.memory_used_mb == 0

    @pytest.mark.skipif(not HAS_PSUTIL, reason="Requires psutil")
    def test_start_and_stop_monitoring(self):
        mon = SystemMonitor(interval=0.1)
        mon.start_monitoring()
        assert mon._monitoring is True
        assert mon._monitor_thread is not None
        time.sleep(0.25)
        mon.stop_monitoring()
        assert mon._monitoring is False

    def test_start_monitoring_is_idempotent(self):
        """Calling start_monitoring twice should not spawn a second thread."""
        if not HAS_PSUTIL:
            pytest.skip("Requires psutil")
        mon = SystemMonitor(interval=0.1)
        mon.start_monitoring()
        first_thread = mon._monitor_thread
        mon.start_monitoring()
        assert mon._monitor_thread is first_thread
        mon.stop_monitoring()

    def test_stop_monitoring_when_not_started(self):
        """stop_monitoring is safe to call even if never started."""
        mon = SystemMonitor()
        mon.stop_monitoring()  # should not raise
        assert mon._monitoring is False


# ---------------------------------------------------------------------------
# PerformanceMonitor tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPerformanceMonitor:
    """Tests for the PerformanceMonitor class."""

    def test_init_no_log_file(self):
        pm = PerformanceMonitor()
        assert pm.log_file is None
        assert pm.metrics == []

    def test_init_with_log_file(self, tmp_path):
        log = tmp_path / "perf.log"
        pm = PerformanceMonitor(log_file=str(log))
        assert pm.log_file == log

    def test_record_metrics_explicit_values(self):
        pm = PerformanceMonitor()
        pm.record_metrics(
            function_name="test_fn",
            execution_time=0.5,
            memory_usage_mb=128.0,
            cpu_percent=15.0,
            metadata={"run": 1},
        )
        assert len(pm.metrics) == 1
        m = pm.metrics[0]
        assert m.function_name == "test_fn"
        assert m.execution_time == 0.5
        assert m.memory_usage_mb == 128.0
        assert m.cpu_percent == 15.0
        assert m.metadata == {"run": 1}

    def test_record_metrics_auto_fills_memory_and_cpu(self):
        pm = PerformanceMonitor()
        pm.record_metrics(function_name="auto", execution_time=0.1)
        assert len(pm.metrics) == 1
        m = pm.metrics[0]
        assert isinstance(m.memory_usage_mb, float)
        assert isinstance(m.cpu_percent, float)

    def test_record_metrics_writes_to_log_file(self, tmp_path):
        log = tmp_path / "perf.jsonl"
        pm = PerformanceMonitor(log_file=str(log))
        pm.record_metrics(
            function_name="logged_fn",
            execution_time=1.0,
            memory_usage_mb=64.0,
            cpu_percent=5.0,
        )
        content = log.read_text()
        data = json.loads(content.strip())
        assert data["function_name"] == "logged_fn"
        assert data["execution_time"] == 1.0

    def test_record_metrics_log_file_error_silenced(self, tmp_path):
        """OSError on invalid log file path is silently caught.

        The except clause catches (OSError, ValueError) so writing to an
        unwritable path is silently swallowed — metrics are still stored
        in memory.
        """
        pm = PerformanceMonitor(log_file="/nonexistent_dir_xyz/perf.log")
        # Should NOT raise — OSError is caught and silenced
        pm.record_metrics(
            function_name="nolog",
            execution_time=0.1,
            memory_usage_mb=10.0,
            cpu_percent=1.0,
        )
        # Metric was still recorded in memory despite log file error
        assert len(pm.metrics) == 1
        assert pm.metrics[0].function_name == "nolog"

    def test_record_metrics_log_file_normal_write(self, tmp_path):
        """Verify metrics are logged when the log path is valid."""
        log = tmp_path / "normal.jsonl"
        pm = PerformanceMonitor(log_file=str(log))
        pm.record_metrics("fn", 0.2, 32.0, 3.0)
        assert len(pm.metrics) == 1
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["function_name"] == "fn"

    def test_get_stats_empty(self):
        pm = PerformanceMonitor()
        assert pm.get_stats() == {}
        assert pm.get_stats("nonexistent") == {}

    def test_get_stats_all(self):
        pm = PerformanceMonitor()
        pm.record_metrics("a", 1.0, 10.0, 5.0)
        pm.record_metrics("b", 2.0, 20.0, 10.0)
        stats = pm.get_stats()
        assert stats["function_name"] == "all"
        assert stats["total_calls"] == 2
        assert stats["execution_time"]["min"] == 1.0
        assert stats["execution_time"]["max"] == 2.0
        assert stats["execution_time"]["avg"] == 1.5
        assert stats["execution_time"]["total"] == 3.0

    def test_get_stats_filtered_by_function(self):
        pm = PerformanceMonitor()
        pm.record_metrics("target", 0.5, 10.0, 2.0)
        pm.record_metrics("other", 1.0, 20.0, 4.0)
        pm.record_metrics("target", 1.5, 30.0, 6.0)
        stats = pm.get_stats("target")
        assert stats["function_name"] == "target"
        assert stats["total_calls"] == 2
        assert stats["execution_time"]["min"] == 0.5
        assert stats["execution_time"]["max"] == 1.5

    def test_clear_metrics(self):
        pm = PerformanceMonitor()
        pm.record_metrics("x", 1.0, 10.0, 5.0)
        assert len(pm.metrics) == 1
        pm.clear_metrics()
        assert len(pm.metrics) == 0

    def test_export_metrics(self, tmp_path):
        pm = PerformanceMonitor()
        pm.record_metrics("fn1", 0.5, 10.0, 5.0, {"k": "v"})
        pm.record_metrics("fn2", 1.0, 20.0, 10.0)

        export_path = tmp_path / "export.json"
        pm.export_metrics(export_path)

        data = json.loads(export_path.read_text())
        assert len(data) == 2
        assert data[0]["function_name"] == "fn1"
        assert data[0]["metadata"] == {"k": "v"}
        assert data[1]["function_name"] == "fn2"

    def test_export_empty_metrics(self, tmp_path):
        pm = PerformanceMonitor()
        export_path = tmp_path / "empty.json"
        pm.export_metrics(export_path)
        data = json.loads(export_path.read_text())
        assert data == []

    def test_get_memory_usage(self):
        pm = PerformanceMonitor()
        mem = pm._get_memory_usage()
        if HAS_PSUTIL:
            assert mem > 0
        else:
            assert mem == 0.0

    def test_get_cpu_percent(self):
        pm = PerformanceMonitor()
        cpu = pm._get_cpu_percent()
        assert isinstance(cpu, float)


# ---------------------------------------------------------------------------
# Decorator tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestMonitorPerformanceDecorator:
    """Tests for the monitor_performance decorator."""

    def test_decorator_records_metrics(self):
        pm = PerformanceMonitor()

        @monitor_performance(function_name="decorated", monitor=pm)
        def sample():
            time.sleep(0.01)
            return 42

        result = sample()
        assert result == 42
        assert len(pm.metrics) == 1
        assert pm.metrics[0].function_name == "decorated"
        assert pm.metrics[0].execution_time >= 0.005

    def test_decorator_uses_function_name_by_default(self):
        pm = PerformanceMonitor()

        @monitor_performance(monitor=pm)
        def my_special_function():
            return "ok"

        my_special_function()
        assert pm.metrics[0].function_name == "my_special_function"

    def test_decorator_preserves_function_metadata(self):
        pm = PerformanceMonitor()

        @monitor_performance(monitor=pm)
        def documented_func():
            """My docstring."""
            pass

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "My docstring."

    def test_decorator_records_even_on_exception(self):
        pm = PerformanceMonitor()

        @monitor_performance(function_name="failing", monitor=pm)
        def failing():
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            failing()
        assert len(pm.metrics) == 1
        assert pm.metrics[0].function_name == "failing"

    def test_profile_function_alias(self):
        """profile_function should be the same as monitor_performance."""
        assert profile_function is monitor_performance


@pytest.mark.unit
class TestProfileMemoryUsage:
    """Tests for the profile_memory_usage decorator."""

    @pytest.mark.skipif(not HAS_PSUTIL, reason="Requires psutil")
    def test_returns_function_result(self):
        @profile_memory_usage
        def compute():
            return list(range(100))

        result = compute()
        assert len(result) == 100

    @pytest.mark.skipif(not HAS_PSUTIL, reason="Requires psutil")
    def test_preserves_function_name(self):
        @profile_memory_usage
        def named_func():
            pass

        assert named_func.__name__ == "named_func"


# ---------------------------------------------------------------------------
# Context manager tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPerformanceContext:
    """Tests for the performance_context context manager."""

    def test_records_execution_time(self):
        # Use the global monitor, so clear first
        clear_performance_metrics()

        with performance_context("ctx_op"):
            time.sleep(0.01)

        stats = get_performance_stats("ctx_op")
        assert stats["total_calls"] == 1
        assert stats["execution_time"]["total"] >= 0.005

    def test_records_even_on_exception(self):
        clear_performance_metrics()
        with pytest.raises(RuntimeError):
            with performance_context("err_op"):
                raise RuntimeError("fail")

        stats = get_performance_stats("err_op")
        assert stats["total_calls"] == 1


@pytest.mark.unit
class TestTrackResourceUsage:
    """Tests for the track_resource_usage context manager."""

    @pytest.mark.skipif(not HAS_PSUTIL, reason="Requires psutil")
    def test_track_resource_usage_runs(self):
        with track_resource_usage("test_op"):
            time.sleep(0.05)
        # No assertion on values -- just confirm no errors

    def test_track_resource_usage_without_psutil(self):
        if HAS_PSUTIL:
            pytest.skip("psutil is installed; cannot test no-psutil path")
        with track_resource_usage("noop"):
            pass  # Should yield without error


# ---------------------------------------------------------------------------
# Module-level helper tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestModuleLevelHelpers:
    """Tests for clear_performance_metrics, get_performance_stats, get_system_metrics."""

    def test_clear_and_get_stats(self):
        clear_performance_metrics()
        assert get_performance_stats() == {}

    def test_get_system_metrics_returns_dict(self):
        result = get_system_metrics()
        assert isinstance(result, dict)
        expected_keys = {
            "cpu_percent",
            "memory_percent",
            "memory_used_mb",
            "memory_total_mb",
            "disk_usage_percent",
            "disk_free_gb",
            "network_bytes_sent",
            "network_bytes_recv",
            "timestamp",
        }
        assert expected_keys == set(result.keys())

    def test_get_performance_stats_with_data(self):
        clear_performance_metrics()

        @monitor_performance(function_name="helper_fn")
        def helper():
            return True

        helper()
        helper()

        stats = get_performance_stats("helper_fn")
        assert stats["total_calls"] == 2
        assert stats["function_name"] == "helper_fn"

        all_stats = get_performance_stats()
        assert all_stats["total_calls"] >= 2

        clear_performance_metrics()
