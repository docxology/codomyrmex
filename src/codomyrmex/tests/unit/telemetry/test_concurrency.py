
import threading
import pytest
from codomyrmex.telemetry.dashboard.slo import SLOTracker, SLIType

def test_slo_tracker_recoding_concurrency():
    """Verify thread safety of SLOTracker.record_event."""
    tracker = SLOTracker()
    tracker.create_slo("concurrent_slo", "Concurrent SLO", SLIType.AVAILABILITY, 99.0)
    
    def worker():
        for _ in range(100):
            tracker.record_event("concurrent_slo", is_good=True)
            tracker.record_event("concurrent_slo", is_good=False)

    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    status = tracker.get_status("concurrent_slo")
    assert status["total_events"] == 2000  # 10 threads * 100 iterations * 2 events
    assert status["good_events"] == 1000   # 10 threads * 100 iterations * 1 good event

def test_slo_creation_concurrency():
    """Verify thread safety of SLOTracker.create_slo."""
    tracker = SLOTracker()
    
    def worker(i):
        tracker.create_slo(f"slo_{i}", f"SLO {i}", SLIType.LATENCY, 95.0)

    threads = []
    for i in range(100):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify all SLOs were created
    assert len(tracker._slos) == 100


# From test_coverage_boost_r3.py
class TestCounter:
    """Tests for Counter metric."""

    def test_increment(self):
        from codomyrmex.telemetry.metrics import Counter

        c = Counter("requests_total", "Total requests")
        c.inc()
        c.inc(5)
        assert c.value == 6

    def test_increment_with_labels(self):
        from codomyrmex.telemetry.metrics import Counter

        c = Counter("req", labels=["method"])
        c.inc(1, labels={"method": "GET"})
        c.inc(1, labels={"method": "POST"})
        assert c.get(labels={"method": "GET"}) == 1
        assert c.get(labels={"method": "POST"}) == 1

    def test_metric_type(self):
        from codomyrmex.telemetry.metrics import Counter, MetricType

        c = Counter("test")
        assert c.metric_type == MetricType.COUNTER


# From test_coverage_boost_r3.py
class TestGauge:
    """Tests for Gauge metric."""

    def test_set_and_get(self):
        from codomyrmex.telemetry.metrics import Gauge

        g = Gauge("temperature")
        g.set(72.5)
        assert g.value == 72.5

    def test_inc_dec(self):
        from codomyrmex.telemetry.metrics import Gauge

        g = Gauge("connections", value=10.0)
        g.inc(5)
        assert g.value == 15.0
        g.dec(3)
        assert g.value == 12.0

    def test_with_labels(self):
        from codomyrmex.telemetry.metrics import Gauge

        g = Gauge("cpu", labels=["core"])
        g.set(80.0, labels={"core": "0"})
        g.set(60.0, labels={"core": "1"})
        assert g.get(labels={"core": "0"}) == 80.0

    def test_metric_type(self):
        from codomyrmex.telemetry.metrics import Gauge, MetricType

        g = Gauge("test")
        assert g.metric_type == MetricType.GAUGE


# From test_coverage_boost_r3.py
class TestHistogram:
    """Tests for Histogram metric."""

    def test_observe(self):
        from codomyrmex.telemetry.metrics import Histogram

        h = Histogram("latency", "Request latency")
        h.observe(0.1)
        h.observe(0.5)
        h.observe(1.5)
        stats = h.get()
        assert stats["count"] == 3
        assert stats["sum"] > 0

    def test_custom_buckets(self):
        from codomyrmex.telemetry.metrics import Histogram

        h = Histogram("custom", buckets=[1.0, 5.0, 10.0])
        h.observe(0.5)
        h.observe(3.0)
        h.observe(7.0)
        stats = h.get()
        assert stats["count"] == 3

    def test_metric_type(self):
        from codomyrmex.telemetry.metrics import Histogram, MetricType

        h = Histogram("test")
        assert h.metric_type == MetricType.HISTOGRAM


# From test_coverage_boost_r3.py
class TestMetricRegistry:
    """Tests for MetricsRegistry (if available)."""

    def test_registry_basics(self):
        try:
            from codomyrmex.telemetry.metrics import MetricsRegistry
        except ImportError:
            pytest.skip("MetricsRegistry not available")

        reg = MetricsRegistry()
        c = reg.counter("test_counter", "A test counter")
        c.inc(10)
        assert c.value == 10

        g = reg.gauge("test_gauge", "A test gauge")
        g.set(42)
        assert g.value == 42
