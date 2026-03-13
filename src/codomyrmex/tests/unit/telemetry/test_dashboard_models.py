"""Tests for telemetry.dashboard.models."""

import time
from datetime import datetime, timedelta

from codomyrmex.telemetry.dashboard.models import (
    Alert,
    AlertSeverity,
    Dashboard,
    MetricType,
    MetricValue,
    Panel,
    PanelType,
)


class TestMetricType:
    def test_all_values(self):
        values = {t.value for t in MetricType}
        assert "counter" in values
        assert "gauge" in values
        assert "histogram" in values
        assert "summary" in values


class TestAlertSeverity:
    def test_all_values(self):
        values = {s.value for s in AlertSeverity}
        assert "info" in values
        assert "warning" in values
        assert "error" in values
        assert "critical" in values


class TestPanelType:
    def test_all_values(self):
        values = {t.value for t in PanelType}
        assert "graph" in values
        assert "stat" in values
        assert "table" in values
        assert "gauge" in values


class TestMetricValue:
    def test_construction(self):
        mv = MetricValue(name="cpu_usage", value=45.2)
        assert mv.name == "cpu_usage"
        assert mv.value == 45.2
        assert mv.metric_type == MetricType.GAUGE

    def test_to_dict(self):
        mv = MetricValue(name="req_count", value=1000.0, metric_type=MetricType.COUNTER)
        d = mv.to_dict()
        assert d["name"] == "req_count"
        assert d["value"] == 1000.0
        assert d["type"] == "counter"
        assert "timestamp" in d
        assert "labels" in d

    def test_with_labels(self):
        mv = MetricValue(name="m", value=1.0, labels={"env": "prod", "service": "api"})
        d = mv.to_dict()
        assert d["labels"] == {"env": "prod", "service": "api"}

    def test_independent_default_labels(self):
        m1 = MetricValue(name="a", value=1.0)
        m2 = MetricValue(name="b", value=2.0)
        m1.labels["k"] = "v"
        assert m2.labels == {}


class TestAlert:
    def test_construction(self):
        a = Alert(id="a1", name="High CPU", message="CPU > 90%")
        assert a.id == "a1"
        assert a.severity == AlertSeverity.WARNING
        assert a.is_active is True

    def test_is_active_before_resolve(self):
        a = Alert(id="a1", name="t", message="m")
        assert a.is_active is True

    def test_is_active_after_resolve(self):
        a = Alert(id="a1", name="t", message="m")
        a.resolve()
        assert a.is_active is False

    def test_duration_active(self):
        a = Alert(id="a1", name="t", message="m")
        time.sleep(0.01)
        assert a.duration.total_seconds() > 0

    def test_duration_resolved(self):
        fired = datetime(2024, 1, 1, 12, 0, 0)
        resolved = datetime(2024, 1, 1, 12, 5, 0)
        a = Alert(id="a1", name="t", message="m", fired_at=fired, resolved_at=resolved)
        assert a.duration == timedelta(minutes=5)

    def test_to_dict(self):
        a = Alert(
            id="a1", name="Disk", message="Disk full", severity=AlertSeverity.CRITICAL
        )
        d = a.to_dict()
        assert d["id"] == "a1"
        assert d["severity"] == "critical"
        assert d["is_active"] is True
        assert d["resolved_at"] is None

    def test_to_dict_resolved(self):
        a = Alert(id="a1", name="t", message="m")
        a.resolve()
        d = a.to_dict()
        assert d["resolved_at"] is not None
        assert d["is_active"] is False


class TestPanel:
    def test_construction(self):
        p = Panel(id="p1", title="CPU Usage", panel_type=PanelType.GRAPH)
        assert p.id == "p1"
        assert p.panel_type == PanelType.GRAPH
        assert p.position == {"x": 0, "y": 0, "w": 6, "h": 4}

    def test_to_dict(self):
        p = Panel(
            id="p1", title="Requests", panel_type=PanelType.STAT, metrics=["req_count"]
        )
        d = p.to_dict()
        assert d["id"] == "p1"
        assert d["title"] == "Requests"
        assert d["type"] == "stat"
        assert d["metrics"] == ["req_count"]

    def test_independent_default_metrics(self):
        p1 = Panel(id="a", title="a", panel_type=PanelType.GRAPH)
        p2 = Panel(id="b", title="b", panel_type=PanelType.GRAPH)
        p1.metrics.append("m1")
        assert p2.metrics == []


class TestDashboard:
    def test_construction(self):
        d = Dashboard(id="d1", name="Ops Dashboard")
        assert d.id == "d1"
        assert d.panels == []
        assert d.refresh_interval_seconds == 30

    def test_add_panel_chainable(self):
        dash = Dashboard(id="d1", name="test")
        p = Panel(id="p1", title="p1", panel_type=PanelType.GRAPH)
        result = dash.add_panel(p)
        assert result is dash
        assert len(dash.panels) == 1

    def test_get_panel_found(self):
        dash = Dashboard(id="d1", name="test")
        p = Panel(id="p1", title="CPU", panel_type=PanelType.GAUGE)
        dash.add_panel(p)
        assert dash.get_panel("p1") is p

    def test_get_panel_not_found(self):
        dash = Dashboard(id="d1", name="test")
        assert dash.get_panel("missing") is None

    def test_to_dict(self):
        dash = Dashboard(
            id="d1", name="My Dashboard", description="desc", tags=["prod"]
        )
        d = dash.to_dict()
        assert d["id"] == "d1"
        assert d["name"] == "My Dashboard"
        assert d["description"] == "desc"
        assert d["tags"] == ["prod"]
        assert d["panels"] == []

    def test_to_dict_with_panels(self):
        dash = Dashboard(id="d1", name="test")
        dash.add_panel(Panel(id="p1", title="t", panel_type=PanelType.GRAPH))
        d = dash.to_dict()
        assert len(d["panels"]) == 1

    def test_independent_default_panels(self):
        d1 = Dashboard(id="a", name="a")
        d2 = Dashboard(id="b", name="b")
        d1.panels.append(Panel(id="p1", title="t", panel_type=PanelType.STAT))
        assert len(d2.panels) == 0
