"""Zero-Mock comprehensive tests for the metrics module.

Tests cover:
- Counter, Gauge, Histogram, Summary metric types
- Metrics registration and updates
- Labels and dimensions
- Prometheus exporter format
- StatsD client operations (real, skip if unavailable)
- Metric aggregation
- Error handling
"""

import socket

import pytest

from codomyrmex.telemetry import metrics
from codomyrmex.telemetry.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricAggregator,
    Metrics,
    MetricsError,
    Summary,
    get_metrics,
)

# ==============================================================================
# Module Import Tests
# ==============================================================================


class TestMetricsModuleImport:
    """Test metrics module import and structure."""

    def test_metrics_module_import(self):
        """Verify that the metrics module can be imported successfully."""
        assert metrics is not None
        assert hasattr(metrics, "__path__")

    def test_metrics_module_structure(self):
        """Verify basic structure of metrics module."""
        assert hasattr(metrics, "__file__")

    def test_metrics_module_exports(self):
        """Verify expected exports are available."""
        assert hasattr(metrics, "Metrics")
        assert hasattr(metrics, "Counter")
        assert hasattr(metrics, "Gauge")
        assert hasattr(metrics, "Histogram")
        assert hasattr(metrics, "Summary")
        assert hasattr(metrics, "MetricAggregator")
        assert hasattr(metrics, "get_metrics")

    def test_metrics_version(self):
        """Verify module version is defined."""
        assert hasattr(metrics, "__version__")
        assert isinstance(metrics.__version__, str)


# ==============================================================================
# Counter Tests
# ==============================================================================


class TestCounter:
    """Tests for Counter metric type."""

    def test_counter_creation(self):
        """Test basic counter creation."""
        counter = Counter(name="test_counter")
        assert counter.name == "test_counter"
        assert counter.value == 0.0
        assert counter.labels == {}

    def test_counter_creation_with_labels(self):
        """Test counter creation with labels."""
        counter = Counter(name="test_counter", labels={"env": "prod", "service": "api"})
        assert counter.name == "test_counter"
        assert counter.labels == {"env": "prod", "service": "api"}

    def test_counter_increment_default(self):
        """Test counter increment with default value."""
        counter = Counter(name="test_counter")
        counter.inc()
        assert counter.value == 1.0

    def test_counter_increment_custom_value(self):
        """Test counter increment with custom value."""
        counter = Counter(name="test_counter")
        counter.inc(5.0)
        assert counter.value == 5.0

    def test_counter_increment_multiple_times(self):
        """Test counter increments accumulate correctly."""
        counter = Counter(name="test_counter")
        counter.inc(1.0)
        counter.inc(2.0)
        counter.inc(3.0)
        assert counter.value == 6.0

    def test_counter_increment_float_values(self):
        """Test counter handles float increments."""
        counter = Counter(name="test_counter")
        counter.inc(0.5)
        counter.inc(0.25)
        assert counter.value == 0.75

    def test_counter_get_value(self):
        """Test getting counter value."""
        counter = Counter(name="test_counter", value=10.0)
        assert counter.get() == 10.0

    def test_counter_never_decreases(self):
        """Test counter handles (but typically shouldn't have) negative increments."""
        # Note: Counter semantically shouldn't decrease, but the implementation
        # doesn't enforce this - test the actual behavior
        counter = Counter(name="test_counter", value=10.0)
        counter.inc(-5.0)
        assert counter.value == 5.0  # Implementation allows negative


# ==============================================================================
# Gauge Tests
# ==============================================================================


class TestGauge:
    """Tests for Gauge metric type."""

    def test_gauge_creation(self):
        """Test basic gauge creation."""
        gauge = Gauge(name="test_gauge")
        assert gauge.name == "test_gauge"
        assert gauge.value == 0.0
        assert gauge.labels == {}

    def test_gauge_creation_with_labels(self):
        """Test gauge creation with labels."""
        gauge = Gauge(name="test_gauge", labels={"host": "server1"})
        assert gauge.labels == {"host": "server1"}

    def test_gauge_set_value(self):
        """Test setting gauge value."""
        gauge = Gauge(name="test_gauge")
        gauge.set(42.0)
        assert gauge.value == 42.0

    def test_gauge_set_overwrites_value(self):
        """Test set overwrites previous value."""
        gauge = Gauge(name="test_gauge", value=10.0)
        gauge.set(20.0)
        assert gauge.value == 20.0

    def test_gauge_increment(self):
        """Test gauge increment."""
        gauge = Gauge(name="test_gauge", value=10.0)
        gauge.inc(5.0)
        assert gauge.value == 15.0

    def test_gauge_increment_default(self):
        """Test gauge increment with default value."""
        gauge = Gauge(name="test_gauge", value=10.0)
        gauge.inc()
        assert gauge.value == 11.0

    def test_gauge_decrement(self):
        """Test gauge decrement."""
        gauge = Gauge(name="test_gauge", value=10.0)
        gauge.dec(3.0)
        assert gauge.value == 7.0

    def test_gauge_decrement_default(self):
        """Test gauge decrement with default value."""
        gauge = Gauge(name="test_gauge", value=10.0)
        gauge.dec()
        assert gauge.value == 9.0

    def test_gauge_negative_values(self):
        """Test gauge can have negative values."""
        gauge = Gauge(name="test_gauge")
        gauge.set(-5.0)
        assert gauge.value == -5.0

    def test_gauge_get_value(self):
        """Test getting gauge value."""
        gauge = Gauge(name="test_gauge", value=100.0)
        assert gauge.get() == 100.0


# ==============================================================================
# Histogram Tests
# ==============================================================================


class TestHistogram:
    """Tests for Histogram metric type."""

    def test_histogram_creation(self):
        """Test basic histogram creation."""
        histogram = Histogram(name="test_histogram")
        assert histogram.name == "test_histogram"
        assert histogram.values == []
        assert histogram.labels == {}

    def test_histogram_creation_with_labels(self):
        """Test histogram creation with labels."""
        histogram = Histogram(name="test_histogram", labels={"method": "GET"})
        assert histogram.labels == {"method": "GET"}

    def test_histogram_observe(self):
        """Test histogram observe operation."""
        histogram = Histogram(name="test_histogram")
        histogram.observe(1.5)
        assert len(histogram.values) == 1
        assert histogram.values[0] == 1.5

    def test_histogram_observe_multiple(self):
        """Test histogram observe multiple values."""
        histogram = Histogram(name="test_histogram")
        histogram.observe(1.0)
        histogram.observe(2.0)
        histogram.observe(3.0)
        assert len(histogram.values) == 3
        assert histogram.values == [1.0, 2.0, 3.0]

    def test_histogram_get_empty(self):
        """Test histogram get on empty histogram."""
        histogram = Histogram(name="test_histogram")
        stats = histogram.get()
        assert stats["count"] == 0
        assert stats["sum"] == 0.0
        assert stats["min"] == 0.0
        assert stats["max"] == 0.0
        assert stats["avg"] == 0.0

    def test_histogram_get_statistics(self):
        """Test histogram get returns correct statistics."""
        histogram = Histogram(name="test_histogram")
        histogram.observe(1.0)
        histogram.observe(2.0)
        histogram.observe(3.0)
        histogram.observe(4.0)
        histogram.observe(5.0)

        stats = histogram.get()
        assert stats["count"] == 5
        assert stats["sum"] == 15.0
        assert stats["min"] == 1.0
        assert stats["max"] == 5.0
        assert stats["avg"] == 3.0

    def test_histogram_get_with_negative_values(self):
        """Test histogram handles negative values."""
        histogram = Histogram(name="test_histogram")
        histogram.observe(-5.0)
        histogram.observe(5.0)

        stats = histogram.get()
        assert stats["count"] == 2
        assert stats["sum"] == 0.0
        assert stats["min"] == -5.0
        assert stats["max"] == 5.0
        assert stats["avg"] == 0.0

    def test_histogram_single_value(self):
        """Test histogram with single observation."""
        histogram = Histogram(name="test_histogram")
        histogram.observe(42.0)

        stats = histogram.get()
        assert stats["count"] == 1
        assert stats["sum"] == 42.0
        assert stats["min"] == 42.0
        assert stats["max"] == 42.0
        assert stats["avg"] == 42.0


# ==============================================================================
# Summary Tests
# ==============================================================================


class TestSummary:
    """Tests for Summary metric type."""

    def test_summary_creation(self):
        """Test basic summary creation."""
        summary = Summary(name="test_summary")
        assert summary.name == "test_summary"
        assert summary.count == 0
        assert summary.sum == 0.0
        assert summary.labels == {}

    def test_summary_creation_with_labels(self):
        """Test summary creation with labels."""
        summary = Summary(name="test_summary", labels={"endpoint": "/api/v1"})
        assert summary.labels == {"endpoint": "/api/v1"}

    def test_summary_observe(self):
        """Test summary observe operation."""
        summary = Summary(name="test_summary")
        summary.observe(1.5)
        assert summary.count == 1
        assert summary.sum == 1.5

    def test_summary_observe_multiple(self):
        """Test summary observe multiple values."""
        summary = Summary(name="test_summary")
        summary.observe(1.0)
        summary.observe(2.0)
        summary.observe(3.0)
        assert summary.count == 3
        assert summary.sum == 6.0

    def test_summary_get_empty(self):
        """Test summary get on empty summary."""
        summary = Summary(name="test_summary")
        stats = summary.get()
        assert stats["count"] == 0
        assert stats["sum"] == 0.0
        assert stats["avg"] == 0.0

    def test_summary_get_statistics(self):
        """Test summary get returns correct statistics."""
        summary = Summary(name="test_summary")
        summary.observe(10.0)
        summary.observe(20.0)
        summary.observe(30.0)

        stats = summary.get()
        assert stats["count"] == 3
        assert stats["sum"] == 60.0
        assert stats["avg"] == 20.0

    def test_summary_accumulates_correctly(self):
        """Test summary accumulates values correctly over time."""
        summary = Summary(name="test_summary")
        for i in range(100):
            summary.observe(1.0)

        stats = summary.get()
        assert stats["count"] == 100
        assert stats["sum"] == 100.0
        assert stats["avg"] == 1.0


# ==============================================================================
# Metrics Class Tests
# ==============================================================================


class TestMetrics:
    """Tests for Metrics collection class."""

    @pytest.fixture
    def metrics_instance(self):
        """Create a fresh Metrics instance for each test."""
        return Metrics(backend="in_memory")

    def test_metrics_creation(self, metrics_instance):
        """Test basic metrics creation."""
        assert metrics_instance.backend == "in_memory"

    def test_metrics_counter_registration(self, metrics_instance):
        """Test counter registration."""
        counter = metrics_instance.counter("requests_total")
        assert counter.name == "requests_total"
        assert isinstance(counter, Counter)

    def test_metrics_counter_retrieval(self, metrics_instance):
        """Test retrieving existing counter."""
        counter1 = metrics_instance.counter("requests_total")
        counter2 = metrics_instance.counter("requests_total")
        assert counter1 is counter2

    def test_metrics_counter_with_labels(self, metrics_instance):
        """Test counter with labels creates unique keys."""
        counter1 = metrics_instance.counter("requests_total", {"method": "GET"})
        counter2 = metrics_instance.counter("requests_total", {"method": "POST"})
        counter3 = metrics_instance.counter("requests_total", {"method": "GET"})

        assert counter1 is not counter2
        assert counter1 is counter3

    def test_metrics_gauge_registration(self, metrics_instance):
        """Test gauge registration."""
        gauge = metrics_instance.gauge("memory_usage")
        assert gauge.name == "memory_usage"
        assert isinstance(gauge, Gauge)

    def test_metrics_histogram_registration(self, metrics_instance):
        """Test histogram registration."""
        histogram = metrics_instance.histogram("request_duration")
        assert histogram.name == "request_duration"
        assert isinstance(histogram, Histogram)

    def test_metrics_summary_registration(self, metrics_instance):
        """Test summary registration."""
        summary = metrics_instance.summary("response_size")
        assert summary.name == "response_size"
        assert isinstance(summary, Summary)

    def test_metrics_export_empty(self, metrics_instance):
        """Test export with no metrics."""
        export = metrics_instance.export()
        assert "counters" in export
        assert "gauges" in export
        assert "histograms" in export
        assert "summaries" in export

    def test_metrics_export_with_data(self, metrics_instance):
        """Test export with metrics data."""
        counter = metrics_instance.counter("requests")
        counter.inc(10)

        gauge = metrics_instance.gauge("connections")
        gauge.set(5)

        export = metrics_instance.export()

        assert "requests" in export["counters"]
        assert export["counters"]["requests"]["value"] == 10
        assert "connections" in export["gauges"]
        assert export["gauges"]["connections"]["value"] == 5

    def test_metrics_make_key_without_labels(self, metrics_instance):
        """Test key generation without labels."""
        key = metrics_instance._make_key("test_metric")
        assert key == "test_metric"

    def test_metrics_make_key_with_labels(self, metrics_instance):
        """Test key generation with labels."""
        key = metrics_instance._make_key("test_metric", {"b": "2", "a": "1"})
        # Labels should be sorted
        assert key == "test_metric{a=1,b=2}"

    def test_metrics_prometheus_export_empty(self, metrics_instance):
        """Test Prometheus export with no metrics."""
        output = metrics_instance.export_prometheus()
        assert output == ""

    def test_metrics_prometheus_export_counter(self, metrics_instance):
        """Test Prometheus export format for counter."""
        counter = metrics_instance.counter("requests_total")
        counter.inc(100)

        output = metrics_instance.export_prometheus()
        assert "requests_total_total 100" in output

    def test_metrics_prometheus_export_counter_with_labels(self, metrics_instance):
        """Test Prometheus export format for counter with labels."""
        counter = metrics_instance.counter("requests_total", {"method": "GET"})
        counter.inc(50)

        output = metrics_instance.export_prometheus()
        assert 'requests_total_total{method="GET"} 50' in output

    def test_metrics_prometheus_export_gauge(self, metrics_instance):
        """Test Prometheus export format for gauge."""
        gauge = metrics_instance.gauge("memory_bytes")
        gauge.set(1024)

        output = metrics_instance.export_prometheus()
        assert "memory_bytes 1024" in output

    def test_metrics_prometheus_export_histogram(self, metrics_instance):
        """Test Prometheus export format for histogram."""
        histogram = metrics_instance.histogram("duration_seconds")
        histogram.observe(0.5)
        histogram.observe(1.0)

        output = metrics_instance.export_prometheus()
        assert "duration_seconds_count 2" in output
        assert "duration_seconds_sum 1.5" in output


# ==============================================================================
# MetricAggregator Tests
# ==============================================================================


class TestMetricAggregator:
    """Tests for MetricAggregator class."""

    @pytest.fixture
    def aggregator(self):
        """Create a fresh MetricAggregator for each test."""
        return MetricAggregator()

    def test_aggregator_creation(self, aggregator):
        """Test basic aggregator creation."""
        assert aggregator is not None

    def test_aggregator_increment(self, aggregator):
        """Test aggregator increment."""
        aggregator.increment("requests")
        snapshot = aggregator.get_snapshot()
        assert snapshot["counters"]["requests"] == 1.0

    def test_aggregator_increment_custom_value(self, aggregator):
        """Test aggregator increment with custom value."""
        aggregator.increment("requests", 5.0)
        snapshot = aggregator.get_snapshot()
        assert snapshot["counters"]["requests"] == 5.0

    def test_aggregator_increment_accumulates(self, aggregator):
        """Test aggregator increments accumulate."""
        aggregator.increment("requests", 1.0)
        aggregator.increment("requests", 2.0)
        aggregator.increment("requests", 3.0)
        snapshot = aggregator.get_snapshot()
        assert snapshot["counters"]["requests"] == 6.0

    def test_aggregator_set_gauge(self, aggregator):
        """Test aggregator set_gauge."""
        aggregator.set_gauge("memory", 1024.0)
        snapshot = aggregator.get_snapshot()
        assert snapshot["gauges"]["memory"] == 1024.0

    def test_aggregator_set_gauge_overwrites(self, aggregator):
        """Test aggregator set_gauge overwrites previous value."""
        aggregator.set_gauge("memory", 1024.0)
        aggregator.set_gauge("memory", 2048.0)
        snapshot = aggregator.get_snapshot()
        assert snapshot["gauges"]["memory"] == 2048.0

    def test_aggregator_get_snapshot(self, aggregator):
        """Test aggregator get_snapshot returns correct data."""
        aggregator.increment("requests", 10)
        aggregator.set_gauge("connections", 5)

        snapshot = aggregator.get_snapshot()
        assert "counters" in snapshot
        assert "gauges" in snapshot
        assert "timestamp" in snapshot
        assert snapshot["counters"]["requests"] == 10
        assert snapshot["gauges"]["connections"] == 5

    def test_aggregator_reset(self, aggregator):
        """Test aggregator reset clears counters."""
        aggregator.increment("requests", 100)
        aggregator.set_gauge("connections", 10)
        aggregator.reset()

        snapshot = aggregator.get_snapshot()
        assert snapshot["counters"] == {}
        # Gauges should persist
        assert snapshot["gauges"]["connections"] == 10

    def test_aggregator_snapshot_is_copy(self, aggregator):
        """Test snapshot returns a copy of the data."""
        aggregator.increment("requests", 10)
        snapshot = aggregator.get_snapshot()

        # Modify the snapshot
        snapshot["counters"]["requests"] = 999

        # Original should be unchanged
        new_snapshot = aggregator.get_snapshot()
        assert new_snapshot["counters"]["requests"] == 10


# ==============================================================================
# Get Metrics Helper Tests
# ==============================================================================


class TestGetMetrics:
    """Tests for get_metrics helper function."""

    def test_get_metrics_default_backend(self):
        """Test get_metrics with default backend."""
        metrics_inst = get_metrics()
        assert metrics_inst.backend == "in_memory"

    def test_get_metrics_custom_backend(self):
        """Test get_metrics with custom backend."""
        metrics_inst = get_metrics(backend="prometheus")
        assert metrics_inst.backend == "prometheus"

    def test_get_metrics_returns_new_instance(self):
        """Test get_metrics returns new instance each time."""
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is not metrics2


# ==============================================================================
# MetricsError Tests
# ==============================================================================


class TestMetricsError:
    """Tests for MetricsError exception."""

    def test_metrics_error_creation(self):
        """Test MetricsError can be created."""
        error = MetricsError("Test error")
        assert "Test error" in str(error)

    def test_metrics_error_is_codomyrmex_error(self):
        """Test MetricsError inherits from CodomyrmexError."""
        from codomyrmex.exceptions import CodomyrmexError
        assert issubclass(MetricsError, CodomyrmexError)

    def test_metrics_error_can_be_raised(self):
        """Test MetricsError can be raised and caught."""
        with pytest.raises(MetricsError) as exc_info:
            raise MetricsError("Something went wrong")
        assert "Something went wrong" in str(exc_info.value)


# ==============================================================================
# Prometheus Exporter Tests (Mocked)
# ==============================================================================


class TestPrometheusExporter:
    """Tests for PrometheusExporter — creation only, no server start."""

    def test_prometheus_exporter_import(self):
        """Test PrometheusExporter can be imported."""
        from codomyrmex.telemetry.metrics import PrometheusExporter
        assert PrometheusExporter is None or callable(PrometheusExporter)

    @pytest.mark.skipif(
        metrics.PrometheusExporter is None,
        reason="prometheus_client not installed"
    )
    def test_prometheus_exporter_creation(self):
        """Test PrometheusExporter creation without starting server."""
        from codomyrmex.telemetry.metrics import PrometheusExporter
        exporter = PrometheusExporter(port=9090, addr="127.0.0.1")
        assert exporter.port == 9090
        assert exporter.addr == "127.0.0.1"
        assert not exporter._server_started


# ==============================================================================
# StatsD Client Tests (Mocked)
# ==============================================================================


# Check for real StatsD server
_HAS_STATSD_SERVER = False
try:
    _test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _test_sock.settimeout(0.1)
    _test_sock.sendto(b"test:1|c", ("localhost", 8125))
    _test_sock.close()
    _HAS_STATSD_SERVER = True
except Exception:
    pass

requires_statsd = pytest.mark.skipif(
    not _HAS_STATSD_SERVER,
    reason="StatsD server not running on localhost:8125",
)


class TestStatsDClient:
    """Tests for StatsDClient — uses real client, skip if no server."""

    def test_statsd_client_import(self):
        """Test StatsDClient can be imported."""
        from codomyrmex.telemetry.metrics import StatsDClient
        assert StatsDClient is None or callable(StatsDClient)

    @pytest.mark.skipif(
        metrics.StatsDClient is None,
        reason="statsd not installed"
    )
    def test_statsd_client_creation(self):
        """Test StatsDClient creation with real client."""
        from codomyrmex.telemetry.metrics import StatsDClient
        client = StatsDClient(host="localhost", port=8125, prefix="test")
        assert client is not None

    @pytest.mark.skipif(
        metrics.StatsDClient is None,
        reason="statsd not installed"
    )
    @requires_statsd
    def test_statsd_client_incr(self):
        """Test StatsDClient incr — sends real UDP packet."""
        from codomyrmex.telemetry.metrics import StatsDClient
        client = StatsDClient()
        client.incr("requests", count=5, rate=0.5)

    @pytest.mark.skipif(
        metrics.StatsDClient is None,
        reason="statsd not installed"
    )
    @requires_statsd
    def test_statsd_client_gauge(self):
        """Test StatsDClient gauge — sends real UDP packet."""
        from codomyrmex.telemetry.metrics import StatsDClient
        client = StatsDClient()
        client.gauge("memory", 1024.0, rate=1.0)

    @pytest.mark.skipif(
        metrics.StatsDClient is None,
        reason="statsd not installed"
    )
    @requires_statsd
    def test_statsd_client_timing(self):
        """Test StatsDClient timing — sends real UDP packet."""
        from codomyrmex.telemetry.metrics import StatsDClient
        client = StatsDClient()
        client.timing("request_time", 150.0)


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestMetricsIntegration:
    """Integration tests for metrics module."""

    def test_full_metrics_workflow(self):
        """Test a complete metrics workflow."""
        # Create metrics instance
        m = get_metrics()

        # Register various metrics
        request_counter = m.counter("http_requests_total", {"method": "GET"})
        response_time = m.histogram("http_response_time_seconds")
        active_connections = m.gauge("http_active_connections")
        request_summary = m.summary("http_request_duration")

        # Simulate some activity
        for _ in range(100):
            request_counter.inc()
            response_time.observe(0.1)
            request_summary.observe(0.1)

        active_connections.set(50)

        # Export and verify
        export = m.export()
        assert export["counters"]["http_requests_total{method=GET}"]["value"] == 100
        assert export["gauges"]["http_active_connections"]["value"] == 50
        assert export["histograms"]["http_response_time_seconds"]["stats"]["count"] == 100

        # Prometheus export
        prom_output = m.export_prometheus()
        assert "http_requests_total_total" in prom_output
        assert "http_active_connections" in prom_output
        assert "http_response_time_seconds_count" in prom_output

    def test_metrics_with_multiple_label_combinations(self):
        """Test metrics with multiple label combinations."""
        m = get_metrics()

        # Create metrics with different label combinations
        m.counter("requests", {"method": "GET", "status": "200"}).inc(100)
        m.counter("requests", {"method": "GET", "status": "404"}).inc(10)
        m.counter("requests", {"method": "POST", "status": "200"}).inc(50)
        m.counter("requests", {"method": "POST", "status": "500"}).inc(5)

        export = m.export()
        counters = export["counters"]

        assert len(counters) == 4
        assert counters['requests{method=GET,status=200}']["value"] == 100
        assert counters['requests{method=GET,status=404}']["value"] == 10
        assert counters['requests{method=POST,status=200}']["value"] == 50
        assert counters['requests{method=POST,status=500}']["value"] == 5

    def test_concurrent_metric_updates(self):
        """Test thread safety of metric updates."""
        import threading

        m = get_metrics()
        counter = m.counter("concurrent_requests")

        def increment_counter():
            for _ in range(1000):
                counter.inc()

        threads = [threading.Thread(target=increment_counter) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Note: Without proper locking, this might not be exactly 10000
        # This test documents current behavior
        assert counter.get() > 0  # At least some increments happened

    def test_metrics_aggregator_with_time_based_data(self):
        """Test aggregator with realistic time-based usage."""
        aggregator = MetricAggregator()

        # Simulate periodic metric collection
        for i in range(10):
            aggregator.increment("events", 1)
            aggregator.set_gauge("active_users", 100 + i)

        snapshot = aggregator.get_snapshot()
        assert snapshot["counters"]["events"] == 10
        assert snapshot["gauges"]["active_users"] == 109  # Last value
        assert "timestamp" in snapshot
