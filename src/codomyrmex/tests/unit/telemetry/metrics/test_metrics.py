"""
Tests for Telemetry Metrics Module
"""

import time

import pytest

from codomyrmex.telemetry.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsRegistry,
    Summary,
    Timer,
)


class TestCounter:
    """Tests for Counter."""

    def test_inc(self):
        """Should increment counter."""
        counter = Counter("requests")
        counter.inc()
        counter.inc(5)

        assert counter.get_value() == 6

    def test_labels(self):
        """Should track by labels."""
        counter = Counter("requests", labels=["method"])
        counter.inc(labels={"method": "GET"})
        counter.inc(labels={"method": "POST"})
        counter.inc(labels={"method": "GET"})

        assert counter.get_value({"method": "GET"}) == 2
        assert counter.get_value({"method": "POST"}) == 1


class TestGauge:
    """Tests for Gauge."""

    def test_set(self):
        """Should set gauge value."""
        gauge = Gauge("temperature")
        gauge.set(72.5)

        assert gauge.get_value() == 72.5

    def test_inc_dec(self):
        """Should increment and decrement."""
        gauge = Gauge("connections")
        gauge.set(10)
        gauge.inc(5)
        gauge.dec(3)

        assert gauge.get_value() == 12


class TestHistogram:
    """Tests for Histogram."""

    def test_observe(self):
        """Should observe values."""
        hist = Histogram("latency")
        hist.observe(0.1)
        hist.observe(0.2)
        hist.observe(0.3)

        stats = hist.get_value()

        assert stats["count"] == 3
        assert stats["min"] == 0.1
        assert stats["max"] == 0.3

    def test_buckets(self):
        """Should track buckets."""
        hist = Histogram("latency", buckets=[0.1, 0.5, 1.0])
        hist.observe(0.05)  # <= 0.1
        hist.observe(0.3)   # <= 0.5
        hist.observe(0.8)   # <= 1.0

        stats = hist.get_value()

        assert stats["buckets"][0.1] == 1
        assert stats["buckets"][0.5] == 2
        assert stats["buckets"][1.0] == 3


class TestSummary:
    """Tests for Summary."""

    def test_quantiles(self):
        """Should calculate quantiles."""
        summary = Summary("response_time")

        for i in range(100):
            summary.observe(float(i))

        stats = summary.get_value()

        assert stats["count"] == 100
        assert 49 <= stats["quantiles"][0.5] <= 50  # median approx


class TestTimer:
    """Tests for Timer."""

    def test_context(self):
        """Should time context."""
        hist = Histogram("duration")

        with Timer(hist):
            time.sleep(0.01)

        stats = hist.get_value()

        assert stats["count"] == 1
        assert stats["min"] >= 0.01


class TestMetricsRegistry:
    """Tests for MetricsRegistry."""

    def test_counter(self):
        """Should create counter."""
        registry = MetricsRegistry()

        c = registry.counter("requests")
        c.inc()

        assert registry.get("requests").get_value() == 1

    def test_gauge(self):
        """Should create gauge."""
        registry = MetricsRegistry()

        g = registry.gauge("temp")
        g.set(100)

        assert registry.get("temp").get_value() == 100

    def test_histogram(self):
        """Should create histogram."""
        registry = MetricsRegistry()

        h = registry.histogram("latency")
        h.observe(1.0)

        assert registry.get("latency").get_value()["count"] == 1

    def test_collect(self):
        """Should collect all metrics."""
        registry = MetricsRegistry()
        registry.counter("a").inc()
        registry.gauge("b").set(5)

        collected = registry.collect()

        assert len(collected) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
