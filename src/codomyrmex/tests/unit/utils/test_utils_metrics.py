"""Tests for utils.metrics - MetricsCollector, timed_metric, count_calls.

MetricsCollector is a singleton - each test resets via metrics.reset().
All tests use real implementations with no mocks.
"""

import time

import pytest

from codomyrmex.utils.metrics import (
    MetricsCollector,
    ModuleHealth,
    count_calls,
    export_prometheus,
    health,
    metrics,
    timed_metric,
)


@pytest.mark.unit
class TestMetricsCollectorSingleton:
    """Tests for MetricsCollector singleton behavior."""

    def setup_method(self):
        metrics.reset()

    def test_singleton_identity(self):
        a = MetricsCollector()
        b = MetricsCollector()
        assert a is b

    def test_global_instance_is_singleton(self):
        assert metrics is MetricsCollector()


@pytest.mark.unit
class TestMetricsCollectorCounters:
    """Tests for counter operations."""

    def setup_method(self):
        metrics.reset()

    def test_increment_creates_counter(self):
        metrics.increment("requests_total")
        all_m = metrics.get_all()
        assert all_m["counters"]["requests_total"] == 1.0

    def test_increment_multiple_times(self):
        metrics.increment("calls")
        metrics.increment("calls")
        metrics.increment("calls", value=2.0)
        all_m = metrics.get_all()
        assert all_m["counters"]["calls"] == 4.0

    def test_increment_with_labels(self):
        metrics.increment("requests", labels={"method": "GET"})
        metrics.increment("requests", labels={"method": "POST"})
        all_m = metrics.get_all()
        assert any("GET" in k for k in all_m["counters"])
        assert any("POST" in k for k in all_m["counters"])


@pytest.mark.unit
class TestMetricsCollectorGauges:
    """Tests for gauge operations."""

    def setup_method(self):
        metrics.reset()

    def test_set_gauge(self):
        metrics.set_gauge("cpu_usage", 75.5)
        all_m = metrics.get_all()
        assert all_m["gauges"]["cpu_usage"] == 75.5

    def test_set_gauge_overwrites(self):
        metrics.set_gauge("temp", 100.0)
        metrics.set_gauge("temp", 50.0)
        all_m = metrics.get_all()
        assert all_m["gauges"]["temp"] == 50.0


@pytest.mark.unit
class TestMetricsCollectorHistograms:
    """Tests for histogram operations."""

    def setup_method(self):
        metrics.reset()

    def test_observe_creates_histogram(self):
        metrics.observe("latency_ms", 10.0)
        all_m = metrics.get_all()
        assert "latency_ms" in all_m["histograms"]

    def test_observe_aggregates_correctly(self):
        metrics.observe("latency_ms", 10.0)
        metrics.observe("latency_ms", 20.0)
        metrics.observe("latency_ms", 30.0)
        h = metrics.get_all()["histograms"]["latency_ms"]
        assert h["count"] == 3
        assert h["sum"] == 60.0
        assert h["min"] == 10.0
        assert h["max"] == 30.0
        assert abs(h["avg"] - 20.0) < 0.01


@pytest.mark.unit
class TestMetricsCollectorReset:
    """Tests for reset operation."""

    def setup_method(self):
        metrics.reset()

    def test_reset_clears_all(self):
        metrics.increment("test_counter")
        metrics.set_gauge("test_gauge", 1.0)
        metrics.observe("test_hist", 5.0)
        metrics.reset()
        all_m = metrics.get_all()
        assert all_m["counters"] == {}
        assert all_m["gauges"] == {}
        assert all_m["histograms"] == {}


@pytest.mark.unit
class TestTimedMetric:
    """Tests for the timed_metric context manager."""

    def setup_method(self):
        metrics.reset()

    def test_records_histogram_with_duration_suffix(self):
        with timed_metric("operation"):
            time.sleep(0.01)
        all_m = metrics.get_all()
        assert "operation_duration_ms" in all_m["histograms"]
        assert all_m["histograms"]["operation_duration_ms"]["count"] == 1
        assert all_m["histograms"]["operation_duration_ms"]["min"] > 0

    def test_records_positive_duration(self):
        with timed_metric("fast_op"):
            pass
        h = metrics.get_all()["histograms"]["fast_op_duration_ms"]
        assert h["min"] >= 0


@pytest.mark.unit
class TestCountCalls:
    """Tests for the count_calls decorator."""

    def setup_method(self):
        metrics.reset()

    def test_increments_call_counter(self):
        @count_calls("my_func")
        def my_func():
            return 42

        my_func()
        my_func()
        all_m = metrics.get_all()
        assert all_m["counters"].get("my_func_calls_total", 0) == 2

    def test_increments_success_counter(self):
        @count_calls("ok_func")
        def ok_func():
            return "ok"

        ok_func()
        all_m = metrics.get_all()
        assert all_m["counters"].get("ok_func_success_total", 0) == 1

    def test_increments_error_counter_on_exception(self):
        @count_calls("failing_func")
        def failing_func():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            failing_func()

        all_m = metrics.get_all()
        assert all_m["counters"].get("failing_func_errors_total", 0) == 1

    def test_preserves_return_value(self):
        @count_calls("ret_func")
        def ret_func():
            return 99

        assert ret_func() == 99

    def test_preserves_exception(self):
        @count_calls("exc_func")
        def exc_func():
            raise ValueError("test")

        with pytest.raises(ValueError, match="test"):
            exc_func()


@pytest.mark.unit
class TestModuleHealth:
    """Tests for ModuleHealth."""

    def setup_method(self):
        self.mh = ModuleHealth()

    def test_register_and_check(self):
        self.mh.register("test_mod", lambda: True)
        assert self.mh.check("test_mod") is True

    def test_check_unregistered_returns_false(self):
        assert self.mh.check("unknown") is False

    def test_check_all_returns_dict(self):
        self.mh.register("mod_a", lambda: True)
        self.mh.register("mod_b", lambda: False)
        result = self.mh.check_all()
        assert result == {"mod_a": True, "mod_b": False}

    def test_is_healthy_all_pass(self):
        self.mh.register("mod_a", lambda: True)
        self.mh.register("mod_b", lambda: True)
        assert self.mh.is_healthy() is True

    def test_is_healthy_one_fails(self):
        self.mh.register("mod_a", lambda: True)
        self.mh.register("mod_b", lambda: False)
        assert self.mh.is_healthy() is False

    def test_check_handles_exception_as_unhealthy(self):
        def bad_check():
            raise RuntimeError("broken")

        self.mh.register("bad_mod", bad_check)
        assert self.mh.check("bad_mod") is False


@pytest.mark.unit
class TestExportPrometheus:
    """Tests for Prometheus-format metric export."""

    def setup_method(self):
        metrics.reset()

    def test_empty_metrics_returns_empty_string(self):
        result = export_prometheus()
        assert result == ""

    def test_counter_format(self):
        metrics.increment("http_requests")
        output = export_prometheus()
        assert "counter" in output.lower()
        assert "http_requests" in output
        assert "1" in output

    def test_gauge_format(self):
        metrics.set_gauge("temperature", 42.5)
        output = export_prometheus()
        assert "gauge" in output.lower()
        assert "temperature" in output

    def test_histogram_format(self):
        metrics.observe("latency", 10.0)
        output = export_prometheus()
        assert "histogram" in output.lower()
        assert "latency" in output
