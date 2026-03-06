"""Zero-mock tests for the telemetry tracing framework."""

import pytest

from codomyrmex.telemetry.metric_aggregator import MetricAggregator
from codomyrmex.telemetry.otel import MetricCounter, Span, Tracer


@pytest.mark.unit
class TestTracingFramework:
    """Tests for the lightweight OTEL-compatible tracing framework."""

    def test_span_creation_and_nesting(self):
        tracer = Tracer(service_name="test-service")

        with tracer.start_as_current_span("root") as root:
            assert root.name == "root"
            assert len(root.trace_id) == 32
            assert len(root.span_id) == 16

            with tracer.start_span("child") as child:
                assert child.name == "child"
                assert child.trace_id == root.trace_id
                assert child.parent_id == root.span_id

                child.set_attribute("app.version", "1.0.0")
                child.add_event("data_processed", {"items": 10})

        export = tracer.export()
        assert len(export) == 2

        root_data = next(s for s in export if s["name"] == "root")
        child_data = next(s for s in export if s["name"] == "child")

        assert child_data["context"]["trace_id"] == root_data["context"]["trace_id"]
        assert child_data["parent_id"] == root_data["context"]["span_id"]
        assert child_data["attributes"]["app.version"] == "1.0.0"
        assert any(e["name"] == "data_processed" for e in child_data["events"])
        assert child_data["status"]["code"] == "OK"

    def test_context_propagation_async_safety(self):
        """Verify contextvars-based propagation."""
        tracer = Tracer()

        with tracer.start_as_current_span("parent"):
            # The child should pick up parent from ContextVar
            child = tracer.start_span("implicit_child")
            assert child.parent_id != ""

    def test_error_handling_in_span(self):
        tracer = Tracer()

        try:
            with tracer.start_as_current_span("faulty_op"):
                raise ValueError("something went wrong")
        except ValueError:
            pass

        export = tracer.export()
        span_data = export[0]
        assert span_data["status"]["code"] == "ERROR"
        assert any(e["name"] == "exception" for e in span_data["events"])

@pytest.mark.unit
class TestMetricAggregatorLabels:
    """Tests for the improved MetricAggregator with label support."""

    def test_counter_with_labels(self):
        agg = MetricAggregator()
        agg.increment("http_requests", labels={"method": "GET", "status": "200"})
        agg.increment("http_requests", labels={"method": "GET", "status": "200"})
        agg.increment("http_requests", labels={"method": "POST", "status": "201"})

        assert agg.counter_value("http_requests", labels={"method": "GET", "status": "200"}) == 2.0
        assert agg.counter_value("http_requests", labels={"method": "POST", "status": "201"}) == 1.0

        snap = agg.snapshot()
        assert "http_requests{method=GET,status=200}" in snap.counters
        assert "http_requests{method=POST,status=201}" in snap.counters

    def test_histogram_stats(self):
        agg = MetricAggregator()
        for v in [10, 20, 30, 40, 50]:
            agg.observe("latency", v)

        stats = agg.histogram_stats("latency")
        assert stats["count"] == 5
        assert stats["mean"] == 30.0
        assert stats["p50"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0

@pytest.mark.unit
class TestMetricCounterLightweight:
    """Tests for the lightweight MetricCounter in otel.py."""

    def test_lightweight_metrics(self):
        mc = MetricCounter()
        mc.increment("test_counter", labels={"color": "red"})
        mc.gauge("test_gauge", 100.0)
        mc.observe("test_hist", 0.5)

        export = mc.export()
        assert export["counters"]["test_counter{color=red}"] == 1.0
        assert export["gauges"]["test_gauge"] == 100.0
        assert "test_hist" in export["histograms"]
        assert export["histograms"]["test_hist"]["count"] == 1
