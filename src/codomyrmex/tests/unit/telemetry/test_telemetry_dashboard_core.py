"""
Unit tests for telemetry.dashboard submodule implementation files — Zero-Mock compliant.

Tests import DIRECTLY from the submodule implementation files (not __init__.py):
  - telemetry/dashboard/models.py   (enums + dataclasses)
  - telemetry/dashboard/collector.py  (MetricCollector)
  - telemetry/dashboard/alerting.py   (AlertManager)
  - telemetry/dashboard/dashboard.py  (DashboardManager)

These files are distinct implementations from the package __init__.py and require
direct imports to achieve coverage.
"""

import math
from datetime import datetime, timedelta

import pytest

from codomyrmex.telemetry.dashboard.alerting import AlertManager
from codomyrmex.telemetry.dashboard.collector import MetricCollector
from codomyrmex.telemetry.dashboard.dashboard import DashboardManager
from codomyrmex.telemetry.dashboard.models import (
    Alert,
    AlertSeverity,
    Dashboard,
    MetricType,
    MetricValue,
    Panel,
    PanelType,
)

# ── MetricType enum ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricTypeModels:
    """Tests for MetricType enum in models.py."""

    def test_counter(self):
        assert MetricType.COUNTER.value == "counter"

    def test_gauge(self):
        assert MetricType.GAUGE.value == "gauge"

    def test_histogram(self):
        assert MetricType.HISTOGRAM.value == "histogram"

    def test_summary(self):
        assert MetricType.SUMMARY.value == "summary"

    def test_enum_count(self):
        assert len(MetricType) == 4


# ── AlertSeverity enum ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlertSeverityModels:
    """Tests for AlertSeverity enum in models.py."""

    def test_info(self):
        assert AlertSeverity.INFO.value == "info"

    def test_warning(self):
        assert AlertSeverity.WARNING.value == "warning"

    def test_error(self):
        assert AlertSeverity.ERROR.value == "error"

    def test_critical(self):
        assert AlertSeverity.CRITICAL.value == "critical"


# ── PanelType enum ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPanelTypeModels:
    """Tests for PanelType enum in models.py."""

    def test_all_types_present(self):
        names = {pt.name for pt in PanelType}
        assert names == {"GRAPH", "STAT", "TABLE", "HEATMAP", "GAUGE", "LOG"}


# ── MetricValue dataclass ──────────────────────────────────────────────────


@pytest.mark.unit
class TestMetricValueModels:
    """Tests for MetricValue dataclass in models.py."""

    def test_basic_instantiation(self):
        mv = MetricValue(name="cpu", value=0.75)
        assert mv.name == "cpu"
        assert mv.value == 0.75
        assert mv.labels == {}
        assert mv.metric_type is MetricType.GAUGE
        assert isinstance(mv.timestamp, datetime)

    def test_custom_labels(self):
        mv = MetricValue(name="req", value=10.0, labels={"method": "GET"})
        assert mv.labels == {"method": "GET"}

    def test_custom_metric_type(self):
        mv = MetricValue(name="cnt", value=5.0, metric_type=MetricType.COUNTER)
        assert mv.metric_type is MetricType.COUNTER

    def test_to_dict_keys(self):
        mv = MetricValue(name="lat", value=12.5)
        d = mv.to_dict()
        assert {"name", "value", "timestamp", "labels", "type"} == set(d.keys())

    def test_to_dict_values(self):
        ts = datetime(2026, 1, 15, 10, 0, 0)
        mv = MetricValue(
            name="mem",
            value=1024.0,
            labels={"host": "srv1"},
            metric_type=MetricType.HISTOGRAM,
            timestamp=ts,
        )
        d = mv.to_dict()
        assert d["name"] == "mem"
        assert d["value"] == 1024.0
        assert d["labels"] == {"host": "srv1"}
        assert d["type"] == "histogram"
        assert d["timestamp"] == ts.isoformat()


# ── Alert dataclass ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAlertModels:
    """Tests for Alert dataclass in models.py."""

    def test_default_status_active(self):
        alert = Alert(id="a1", name="cpu_high", message="CPU over threshold")
        assert alert.is_active is True
        assert alert.resolved_at is None
        assert alert.severity is AlertSeverity.WARNING
        assert isinstance(alert.fired_at, datetime)

    def test_resolve_deactivates(self):
        alert = Alert(id="a2", name="mem_low", message="Low memory")
        alert.resolve()
        assert alert.is_active is False
        assert alert.resolved_at is not None

    def test_duration_active_alert_is_positive(self):
        alert = Alert(id="a3", name="x", message="test")
        dur = alert.duration
        assert isinstance(dur, timedelta)
        assert dur.total_seconds() >= 0.0

    def test_duration_resolved_alert(self):
        fired = datetime(2026, 3, 1, 12, 0, 0)
        resolved = datetime(2026, 3, 1, 12, 5, 0)
        alert = Alert(id="a4", name="disk", message="Full", fired_at=fired)
        alert.resolved_at = resolved
        assert math.isclose(alert.duration.total_seconds(), 300.0)

    def test_to_dict_structure(self):
        alert = Alert(id="a5", name="err", message="Error")
        d = alert.to_dict()
        assert "id" in d
        assert "name" in d
        assert "message" in d
        assert "severity" in d
        assert "fired_at" in d
        assert "resolved_at" in d
        assert "is_active" in d

    def test_to_dict_resolved_at_none_when_active(self):
        alert = Alert(id="a6", name="x", message="y")
        assert alert.to_dict()["resolved_at"] is None
        assert alert.to_dict()["is_active"] is True

    def test_to_dict_severity_is_string(self):
        alert = Alert(id="a7", name="x", message="y", severity=AlertSeverity.CRITICAL)
        assert alert.to_dict()["severity"] == "critical"

    def test_labels_defaults_empty(self):
        alert = Alert(id="a8", name="x", message="y")
        assert alert.labels == {}

    def test_custom_labels(self):
        alert = Alert(id="a9", name="x", message="y", labels={"env": "prod"})
        assert alert.labels["env"] == "prod"


# ── Panel dataclass ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestPanelModels:
    """Tests for Panel dataclass in models.py."""

    def test_basic_instantiation(self):
        panel = Panel(id="p1", title="CPU", panel_type=PanelType.GRAPH)
        assert panel.id == "p1"
        assert panel.title == "CPU"
        assert panel.panel_type is PanelType.GRAPH
        assert panel.metrics == []
        assert panel.query == ""
        assert panel.options == {}

    def test_custom_metrics_list(self):
        panel = Panel(
            id="p2",
            title="Net",
            panel_type=PanelType.TABLE,
            metrics=["bytes_in", "bytes_out"],
        )
        assert len(panel.metrics) == 2

    def test_to_dict(self):
        panel = Panel(
            id="p3",
            title="Errors",
            panel_type=PanelType.STAT,
            metrics=["error_count"],
        )
        d = panel.to_dict()
        assert d["id"] == "p3"
        assert d["title"] == "Errors"
        assert d["type"] == "stat"
        assert d["metrics"] == ["error_count"]

    def test_position_default(self):
        panel = Panel(id="p4", title="T", panel_type=PanelType.GAUGE)
        assert panel.position == {"x": 0, "y": 0, "w": 6, "h": 4}


# ── Dashboard dataclass ────────────────────────────────────────────────────


@pytest.mark.unit
class TestDashboardModels:
    """Tests for Dashboard dataclass in models.py."""

    def test_instantiation(self):
        dash = Dashboard(
            id="d1",
            name="Overview",
            description="Main dash",
        )
        assert dash.id == "d1"
        assert dash.name == "Overview"
        assert dash.description == "Main dash"
        assert dash.panels == []
        assert dash.tags == []

    def test_add_panel(self):
        dash = Dashboard(id="d2", name="Test")
        panel = Panel(id="p1", title="CPU", panel_type=PanelType.GRAPH)
        result = dash.add_panel(panel)
        assert result is dash  # chaining
        assert len(dash.panels) == 1

    def test_get_panel_found(self):
        dash = Dashboard(id="d3", name="Find")
        panel = Panel(id="target", title="X", panel_type=PanelType.STAT)
        dash.add_panel(panel)
        assert dash.get_panel("target") is panel

    def test_get_panel_not_found(self):
        dash = Dashboard(id="d4", name="Miss")
        assert dash.get_panel("nope") is None

    def test_to_dict(self):
        dash = Dashboard(id="d5", name="Full", tags=["prod"])
        panel = Panel(id="p1", title="C", panel_type=PanelType.GAUGE)
        dash.add_panel(panel)
        d = dash.to_dict()
        assert d["id"] == "d5"
        assert d["name"] == "Full"
        assert d["tags"] == ["prod"]
        assert len(d["panels"]) == 1

    def test_refresh_interval_default(self):
        dash = Dashboard(id="d6", name="RI")
        assert dash.refresh_interval_seconds == 30


# ── MetricCollector (collector.py) ─────────────────────────────────────────


@pytest.mark.unit
class TestMetricCollectorCore:
    """Tests for MetricCollector in collector.py (default retention=60)."""

    def test_default_retention(self):
        c = MetricCollector()
        assert c.retention_minutes == 60

    def test_custom_retention(self):
        c = MetricCollector(retention_minutes=10)
        assert c.retention_minutes == 10

    def test_record_and_get(self):
        c = MetricCollector()
        c.record("cpu", 0.5)
        c.record("cpu", 0.8)
        metrics = c.get_metrics("cpu")
        assert len(metrics) == 2

    def test_get_unknown_name_returns_empty(self):
        c = MetricCollector()
        assert c.get_metrics("no_such") == []

    def test_record_with_labels(self):
        c = MetricCollector()
        c.record("http", 1.0, labels={"method": "POST"})
        mv = c.get_metrics("http")[0]
        assert mv.labels == {"method": "POST"}

    def test_record_with_counter_type(self):
        c = MetricCollector()
        c.record("cnt", 5.0, metric_type=MetricType.COUNTER)
        assert c.get_metrics("cnt")[0].metric_type is MetricType.COUNTER

    def test_get_latest_returns_last(self):
        c = MetricCollector()
        c.record("m", 10.0)
        c.record("m", 20.0)
        assert c.get_latest("m").value == 20.0

    def test_get_latest_unknown_returns_none(self):
        c = MetricCollector()
        assert c.get_latest("nope") is None

    def test_list_metric_names(self):
        c = MetricCollector()
        c.record("alpha", 1.0)
        c.record("beta", 2.0)
        assert set(c.list_metric_names()) == {"alpha", "beta"}

    def test_list_metric_names_empty(self):
        c = MetricCollector()
        assert c.list_metric_names() == []

    def test_get_metrics_time_filter(self):
        c = MetricCollector()
        old_ts = datetime(2020, 1, 1)
        new_ts = datetime(2026, 1, 1)
        from codomyrmex.telemetry.dashboard.models import MetricValue as MV
        c._metrics["z"] = [
            MV(name="z", value=1.0, timestamp=old_ts),
            MV(name="z", value=2.0, timestamp=new_ts),
        ]
        result = c.get_metrics("z", start=datetime(2025, 1, 1))
        assert len(result) == 1
        assert result[0].value == 2.0

    def test_cleanup_removes_old(self):
        c = MetricCollector(retention_minutes=1)
        from codomyrmex.telemetry.dashboard.models import MetricValue as MV
        old_ts = datetime.now() - timedelta(minutes=10)
        c._metrics["stale"] = [MV(name="stale", value=1.0, timestamp=old_ts)]
        c.record("fresh", 5.0)
        removed = c.cleanup_old()
        assert removed == 1
        assert c.get_metrics("stale") == []
        assert len(c.get_metrics("fresh")) == 1

    def test_cleanup_nothing_to_remove(self):
        c = MetricCollector(retention_minutes=60)
        c.record("recent", 1.0)
        assert c.cleanup_old() == 0


# ── AlertManager (alerting.py) ─────────────────────────────────────────────


@pytest.mark.unit
class TestAlertManagerCore:
    """Tests for AlertManager in alerting.py."""

    def test_initial_state_empty(self):
        am = AlertManager()
        assert am.get_active_alerts() == []
        assert am.get_alert_history() == []

    def test_add_rule_and_fires(self):
        am = AlertManager()
        am.add_rule(
            name="cpu_high",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU too high",
        )
        fired = am.check({"cpu": 0.95})
        assert len(fired) == 1
        assert fired[0].name == "cpu_high"

    def test_no_fire_when_condition_false(self):
        am = AlertManager()
        am.add_rule(
            name="low_mem",
            condition=lambda m: m.get("mem", 100) < 5,
            message="Low memory",
        )
        fired = am.check({"mem": 50})
        assert fired == []

    def test_no_duplicate_active_alert(self):
        am = AlertManager()
        am.add_rule(name="always", condition=lambda m: True, message="Always")
        first = am.check({})
        second = am.check({})
        assert len(first) == 1
        assert second == []  # already active
        assert len(am.get_active_alerts()) == 1

    def test_auto_resolves_when_condition_clears(self):
        am = AlertManager()
        am.add_rule(
            name="flap",
            condition=lambda m: m.get("v", 0) > 10,
            message="High",
        )
        am.check({"v": 20})
        assert len(am.get_active_alerts()) == 1
        am.check({"v": 0})
        assert len(am.get_active_alerts()) == 0

    def test_condition_exception_does_not_fire(self):
        am = AlertManager()
        am.add_rule(
            name="broken",
            condition=lambda m: 1 / 0,
            message="Should not fire",
        )
        fired = am.check({})
        assert fired == []

    def test_acknowledge_resolves_alert(self):
        am = AlertManager()
        am.add_rule(name="ack_me", condition=lambda m: True, message="Ack")
        fired = am.check({})
        alert_id = fired[0].id
        result = am.acknowledge(alert_id)
        assert result is True
        assert len(am.get_active_alerts()) == 0

    def test_acknowledge_unknown_id_returns_false(self):
        am = AlertManager()
        assert am.acknowledge("fake_id") is False

    def test_alert_history_returns_latest(self):
        am = AlertManager()
        am.add_rule(name="h", condition=lambda m: m.get("x", 0) > 0, message="H")
        am.check({"x": 1})  # fires
        am.check({"x": 0})  # resolves
        am.check({"x": 1})  # fires again (new alert)
        history = am.get_alert_history()
        # alerting.py stores one entry per rule_name; history = current _alerts
        assert len(history) >= 1

    def test_custom_severity_propagated(self):
        am = AlertManager()
        am.add_rule(
            name="crit",
            condition=lambda m: True,
            message="Critical alert",
            severity=AlertSeverity.CRITICAL,
        )
        fired = am.check({})
        assert fired[0].severity is AlertSeverity.CRITICAL

    def test_get_active_alerts_after_acknowledge(self):
        am = AlertManager()
        am.add_rule(name="r1", condition=lambda m: True, message="R1")
        am.add_rule(name="r2", condition=lambda m: True, message="R2")
        am.check({})
        active = am.get_active_alerts()
        assert len(active) == 2
        am.acknowledge(active[0].id)
        assert len(am.get_active_alerts()) == 1


# ── DashboardManager (dashboard.py) ───────────────────────────────────────


@pytest.mark.unit
class TestDashboardManagerCore:
    """Tests for DashboardManager in dashboard.py."""

    def test_default_collector(self):
        dm = DashboardManager()
        assert isinstance(dm.collector, MetricCollector)

    def test_custom_collector(self):
        c = MetricCollector(retention_minutes=5)
        dm = DashboardManager(collector=c)
        assert dm.collector is c

    def test_create_generates_id(self):
        dm = DashboardManager()
        dash = dm.create("System Overview")
        assert dash.id == "system_overview"
        assert dash.name == "System Overview"

    def test_create_with_description_and_tags(self):
        dm = DashboardManager()
        dash = dm.create("Net", description="Network dash", tags=["net", "infra"])
        assert dash.description == "Network dash"
        assert dash.tags == ["net", "infra"]

    def test_get_existing(self):
        dm = DashboardManager()
        created = dm.create("MyDash")
        fetched = dm.get("mydash")
        assert fetched is created

    def test_get_nonexistent_returns_none(self):
        dm = DashboardManager()
        assert dm.get("no_such") is None

    def test_list_all(self):
        dm = DashboardManager()
        dm.create("A")
        dm.create("B")
        assert len(dm.list()) == 2

    def test_list_empty(self):
        dm = DashboardManager()
        assert dm.list() == []

    def test_delete_existing(self):
        dm = DashboardManager()
        dm.create("ToDelete")
        assert dm.delete("todelete") is True
        assert dm.get("todelete") is None

    def test_delete_nonexistent_returns_false(self):
        dm = DashboardManager()
        assert dm.delete("nope") is False

    def test_get_panel_data_returns_metrics(self):
        c = MetricCollector()
        c.record("cpu_usage", 0.7)
        c.record("cpu_usage", 0.9)
        dm = DashboardManager(collector=c)
        dash = dm.create("PanelTest")
        panel = Panel(id="cpu_panel", title="CPU", panel_type=PanelType.GRAPH, metrics=["cpu_usage"])
        dash.add_panel(panel)
        data = dm.get_panel_data("paneltest", "cpu_panel")
        assert len(data) == 2

    def test_get_panel_data_unknown_dashboard(self):
        dm = DashboardManager()
        assert dm.get_panel_data("unknown", "p1") == []

    def test_get_panel_data_unknown_panel(self):
        dm = DashboardManager()
        dm.create("Known")
        assert dm.get_panel_data("known", "no_panel") == []

    def test_get_panel_data_with_duration(self):
        c = MetricCollector()
        c.record("mem", 512.0)
        dm = DashboardManager(collector=c)
        dash = dm.create("DurTest")
        panel = Panel(id="mem_panel", title="Mem", panel_type=PanelType.STAT, metrics=["mem"])
        dash.add_panel(panel)
        data = dm.get_panel_data("durtest", "mem_panel", duration_minutes=30)
        assert len(data) == 1
