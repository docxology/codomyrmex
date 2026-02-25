"""Tests for Sprint 36: Full Observability Stack.

Covers ObservabilityPipeline, MetricAggregator, AlertEvaluator,
and DashboardBuilder.
"""

import json

from codomyrmex.data_visualization.dashboard_builder import (
    DashboardBuilder,
    Panel,
    PanelTarget,
    ThresholdConfig,
)
from codomyrmex.telemetry.alerting.alert_evaluator import (
    AlertEvaluator,
    AlertRule,
    AlertSeverity,
)
from codomyrmex.telemetry.metric_aggregator import MetricAggregator
from codomyrmex.telemetry.pipeline import EventKind, ObservabilityPipeline

# ─── ObservabilityPipeline ────────────────────────────────────────────

class TestObservabilityPipeline:
    """Test suite for ObservabilityPipeline."""

    def test_correlation(self):
        """Test functionality: correlation."""
        pipe = ObservabilityPipeline()
        cid = pipe.start_correlation()
        pipe.record_span("api.call", cid, duration_ms=10)
        pipe.record_metric("latency", cid, value=10)
        pipe.record_log("info", cid, message="ok")
        events = pipe.get_correlated(cid)
        assert len(events) == 3
        kinds = {e.kind for e in events}
        assert kinds == {EventKind.SPAN, EventKind.METRIC, EventKind.LOG}

    def test_audit_event(self):
        """Test functionality: audit event."""
        pipe = ObservabilityPipeline()
        evt = pipe.record_audit("login", actor="user1")
        assert evt.kind == EventKind.AUDIT
        assert evt.data["actor"] == "user1"

    def test_get_by_kind(self):
        """Test functionality: get by kind."""
        pipe = ObservabilityPipeline()
        pipe.record_span("a", duration_ms=1)
        pipe.record_log("info", message="x")
        assert len(pipe.get_by_kind(EventKind.SPAN)) == 1


# ─── MetricAggregator ────────────────────────────────────────────────

class TestMetricAggregator:
    """Test suite for MetricAggregator."""

    def test_counter(self):
        """Test functionality: counter."""
        m = MetricAggregator()
        m.increment("req")
        m.increment("req", 2)
        assert m.counter_value("req") == 3

    def test_gauge(self):
        """Test functionality: gauge."""
        m = MetricAggregator()
        m.gauge("cpu", 65.0)
        assert m.gauge_value("cpu") == 65.0

    def test_histogram(self):
        """Test functionality: histogram."""
        m = MetricAggregator()
        for v in [10, 20, 30, 40, 50]:
            m.observe("latency", v)
        stats = m.histogram_stats("latency")
        assert stats["count"] == 5
        assert stats["mean"] == 30.0

    def test_snapshot(self):
        """Test functionality: snapshot."""
        m = MetricAggregator()
        m.increment("x")
        m.gauge("y", 1.0)
        snap = m.snapshot()
        assert "x" in snap.counters
        assert "y" in snap.gauges


# ─── AlertEvaluator ──────────────────────────────────────────────────

class TestAlertEvaluator:
    """Test suite for AlertEvaluator."""

    def test_fires_on_threshold(self):
        """Test functionality: fires on threshold."""
        m = MetricAggregator()
        m.gauge("cpu", 95.0)
        ev = AlertEvaluator(metrics=m)
        ev.add_rule(AlertRule(
            name="high_cpu", metric_name="cpu",
            threshold=80, operator="gt",
            severity=AlertSeverity.CRITICAL,
        ))
        alerts = ev.evaluate()
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_no_alert_below_threshold(self):
        """Test functionality: no alert below threshold."""
        m = MetricAggregator()
        m.gauge("cpu", 50.0)
        ev = AlertEvaluator(metrics=m)
        ev.add_rule(AlertRule(name="high_cpu", metric_name="cpu", threshold=80))
        alerts = ev.evaluate()
        assert len(alerts) == 0

    def test_resolves_alert(self):
        """Test functionality: resolves alert."""
        m = MetricAggregator()
        m.gauge("cpu", 95.0)
        ev = AlertEvaluator(metrics=m)
        ev.add_rule(AlertRule(name="high_cpu", metric_name="cpu", threshold=80))
        ev.evaluate()
        assert len(ev.active_alerts) == 1
        m.gauge("cpu", 50.0)
        ev.evaluate()
        assert len(ev.active_alerts) == 0

    def test_alert_history(self):
        """Test functionality: alert history."""
        m = MetricAggregator()
        m.increment("errors", 10)
        ev = AlertEvaluator(metrics=m)
        ev.add_rule(AlertRule(name="err", metric_name="errors", threshold=5))
        ev.evaluate()
        assert len(ev.alert_history()) == 1


# ─── DashboardBuilder ───────────────────────────────────────────────

class TestDashboardBuilder:
    """Test suite for DashboardBuilder."""

    def test_build_basic(self):
        """Test functionality: build basic."""
        builder = DashboardBuilder(title="Test")
        builder.add_panel(Panel(title="CPU", targets=[PanelTarget(metric="cpu")]))
        config = builder.build()
        assert config["title"] == "Test"
        assert len(config["panels"]) == 1

    def test_valid_json(self):
        """Test functionality: valid json."""
        builder = DashboardBuilder(title="Export")
        builder.add_panel(Panel(title="P1"))
        output = builder.to_json()
        parsed = json.loads(output)
        assert parsed["title"] == "Export"

    def test_thresholds(self):
        """Test functionality: thresholds."""
        builder = DashboardBuilder()
        builder.add_panel(Panel(
            title="Latency",
            thresholds=[ThresholdConfig(value=100, color="red")],
        ))
        config = builder.build()
        assert "thresholds" in config["panels"][0]
