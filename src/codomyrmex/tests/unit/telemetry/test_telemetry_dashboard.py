"""
Tests for telemetry.dashboard module.

Covers enums, dataclass models, MetricCollector, AlertManager,
and DashboardManager from both the submodule files and the
__init__.py re-exports.
"""

from datetime import datetime, timedelta

import pytest

from codomyrmex.telemetry.dashboard import (
    Alert,
    AlertManager,
    AlertSeverity,
    Dashboard,
    DashboardManager,
    MetricCollector,
    MetricType,
    MetricValue,
    Panel,
    PanelType,
)

# ---------------------------------------------------------------
# Enum tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestMetricTypeEnum:
    """Tests for the MetricType enumeration."""

    def test_counter_value(self):
        assert MetricType.COUNTER.value == "counter"

    def test_gauge_value(self):
        assert MetricType.GAUGE.value == "gauge"

    def test_histogram_value(self):
        assert MetricType.HISTOGRAM.value == "histogram"

    def test_summary_value(self):
        assert MetricType.SUMMARY.value == "summary"

    def test_member_count(self):
        assert len(MetricType) == 4


@pytest.mark.unit
class TestAlertSeverityEnum:
    """Tests for the AlertSeverity enumeration."""

    def test_severity_ordering_values(self):
        expected = ["info", "warning", "error", "critical"]
        actual = [s.value for s in AlertSeverity]
        assert actual == expected

    def test_lookup_by_value(self):
        assert AlertSeverity("critical") is AlertSeverity.CRITICAL


@pytest.mark.unit
class TestPanelTypeEnum:
    """Tests for the PanelType enumeration."""

    def test_all_panel_types_present(self):
        names = {pt.name for pt in PanelType}
        assert names == {"GRAPH", "STAT", "TABLE", "HEATMAP", "GAUGE", "LOG"}

    def test_graph_is_default_string(self):
        assert PanelType.GRAPH.value == "graph"


# ---------------------------------------------------------------
# MetricValue dataclass tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestMetricValue:
    """Tests for the MetricValue dataclass."""

    def test_instantiation_minimal(self):
        mv = MetricValue(name="cpu", value=0.85)
        assert mv.name == "cpu"
        assert mv.value == 0.85
        assert isinstance(mv.timestamp, datetime)
        assert mv.labels == {}
        assert mv.metric_type is MetricType.GAUGE

    def test_instantiation_full(self):
        ts = datetime(2026, 1, 1, 12, 0, 0)
        mv = MetricValue(
            name="requests",
            value=42.0,
            labels={"method": "GET"},
            metric_type=MetricType.COUNTER,
            timestamp=ts,
        )
        assert mv.name == "requests"
        assert mv.value == 42.0
        assert mv.labels == {"method": "GET"}
        assert mv.metric_type is MetricType.COUNTER
        assert mv.timestamp == ts

    def test_to_dict_keys(self):
        mv = MetricValue(name="mem", value=1024.0)
        d = mv.to_dict()
        assert "name" in d
        assert "value" in d
        assert "timestamp" in d
        assert "labels" in d
        assert "type" in d

    def test_to_dict_values(self):
        ts = datetime(2026, 6, 15, 8, 30, 0)
        mv = MetricValue(
            name="latency",
            value=12.5,
            labels={"service": "api"},
            metric_type=MetricType.HISTOGRAM,
            timestamp=ts,
        )
        d = mv.to_dict()
        assert d["name"] == "latency"
        assert d["value"] == 12.5
        assert d["labels"] == {"service": "api"}
        assert d["type"] == "histogram"
        assert d["timestamp"] == ts.isoformat()

    def test_default_labels_are_independent(self):
        """Each instance should get its own labels dict."""
        mv1 = MetricValue(name="a", value=1.0)
        mv2 = MetricValue(name="b", value=2.0)
        mv1.labels["env"] = "prod"
        assert "env" not in mv2.labels


# ---------------------------------------------------------------
# Alert dataclass tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestAlert:
    """Tests for the Alert dataclass."""

    def test_instantiation_defaults(self):
        alert = Alert(id="a1", name="cpu_high", message="CPU is high")
        assert alert.id == "a1"
        assert alert.name == "cpu_high"
        assert alert.message == "CPU is high"
        assert alert.severity is AlertSeverity.WARNING
        assert alert.is_active is True
        assert alert.resolved_at is None

    def test_resolve_sets_inactive(self):
        alert = Alert(id="a2", name="mem", message="OOM")
        assert alert.is_active is True
        alert.resolve()
        assert alert.is_active is False
        assert alert.resolved_at is not None
        assert isinstance(alert.resolved_at, datetime)

    def test_duration_active_alert(self):
        alert = Alert(
            id="a3",
            name="test",
            message="test",
            created_at=datetime.now() - timedelta(seconds=5),
        )
        dur = alert.duration
        assert isinstance(dur, timedelta)
        assert dur.total_seconds() >= 4  # allow small margin

    def test_duration_resolved_alert(self):
        fired = datetime(2026, 1, 1, 12, 0, 0)
        resolved = datetime(2026, 1, 1, 12, 5, 0)
        alert = Alert(
            id="a4",
            name="test",
            message="test",
            created_at=fired,
            resolved_at=resolved,
            is_active=False,
        )
        assert alert.duration == timedelta(minutes=5)

    def test_to_dict_keys(self):
        alert = Alert(id="a5", name="disk", message="disk full")
        d = alert.to_dict()
        expected_keys = {"id", "name", "message", "severity", "is_active",
                         "created_at", "resolved_at"}
        assert expected_keys == set(d.keys())

    def test_to_dict_resolved_at_none_when_active(self):
        alert = Alert(id="a6", name="x", message="y")
        d = alert.to_dict()
        assert d["resolved_at"] is None
        assert d["is_active"] is True

    def test_to_dict_severity_is_string(self):
        alert = Alert(
            id="a7", name="x", message="y",
            severity=AlertSeverity.CRITICAL,
        )
        assert alert.to_dict()["severity"] == "critical"


# ---------------------------------------------------------------
# Panel dataclass tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestPanel:
    """Tests for the Panel dataclass."""

    def test_instantiation_minimal(self):
        panel = Panel(id="p1", title="CPU")
        assert panel.id == "p1"
        assert panel.title == "CPU"
        assert panel.panel_type is PanelType.GRAPH
        assert panel.metrics == []
        assert panel.config == {}

    def test_instantiation_with_metrics(self):
        panel = Panel(
            id="p2",
            title="Network",
            panel_type=PanelType.TABLE,
            metrics=["bytes_in", "bytes_out"],
        )
        assert panel.panel_type is PanelType.TABLE
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


# ---------------------------------------------------------------
# Dashboard class tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestDashboard:
    """Tests for the Dashboard class."""

    def test_instantiation(self):
        dash = Dashboard(id="d1", name="Overview")
        assert dash.id == "d1"
        assert dash.name == "Overview"
        assert dash.description == ""
        assert dash.tags == []
        assert dash.panels == []
        assert isinstance(dash.created_at, datetime)

    def test_add_panel_returns_self(self):
        dash = Dashboard(id="d2", name="Test")
        panel = Panel(id="p1", title="CPU")
        result = dash.add_panel(panel)
        assert result is dash
        assert len(dash.panels) == 1

    def test_add_panel_chaining(self):
        dash = Dashboard(id="d3", name="Chain")
        p1 = Panel(id="p1", title="A")
        p2 = Panel(id="p2", title="B")
        dash.add_panel(p1).add_panel(p2)
        assert len(dash.panels) == 2

    def test_get_panel_found(self):
        dash = Dashboard(id="d4", name="Find")
        panel = Panel(id="target", title="Target")
        dash.add_panel(panel)
        found = dash.get_panel("target")
        assert found is panel

    def test_get_panel_not_found(self):
        dash = Dashboard(id="d5", name="Miss")
        assert dash.get_panel("nonexistent") is None

    def test_to_dict_structure(self):
        dash = Dashboard(
            id="d6",
            name="Full",
            description="A full dashboard",
            tags=["prod", "infra"],
        )
        panel = Panel(id="p1", title="CPU", panel_type=PanelType.GAUGE)
        dash.add_panel(panel)
        d = dash.to_dict()
        assert d["id"] == "d6"
        assert d["name"] == "Full"
        assert d["description"] == "A full dashboard"
        assert d["tags"] == ["prod", "infra"]
        assert len(d["panels"]) == 1
        assert d["panels"][0]["id"] == "p1"
        assert "created_at" in d

    def test_tags_default_none_becomes_empty_list(self):
        dash = Dashboard(id="d7", name="No Tags")
        assert dash.tags == []


# ---------------------------------------------------------------
# MetricCollector tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestMetricCollector:
    """Tests for the MetricCollector class."""

    def test_instantiation_default_retention(self):
        c = MetricCollector()
        assert c.retention_minutes == 1440

    def test_instantiation_custom_retention(self):
        c = MetricCollector(retention_minutes=30)
        assert c.retention_minutes == 30

    def test_record_and_get_metrics(self):
        c = MetricCollector()
        c.record("cpu", 0.5)
        c.record("cpu", 0.6)
        metrics = c.get_metrics("cpu")
        assert len(metrics) == 2
        assert metrics[0].value == 0.5
        assert metrics[1].value == 0.6

    def test_get_metrics_unknown_name(self):
        c = MetricCollector()
        assert c.get_metrics("nonexistent") == []

    def test_record_with_labels(self):
        c = MetricCollector()
        c.record("http", 1.0, labels={"method": "POST"})
        mv = c.get_metrics("http")[0]
        assert mv.labels == {"method": "POST"}

    def test_record_with_metric_type(self):
        c = MetricCollector()
        c.record("counter", 10.0, metric_type=MetricType.COUNTER)
        mv = c.get_metrics("counter")[0]
        assert mv.metric_type is MetricType.COUNTER

    def test_get_latest(self):
        c = MetricCollector()
        c.record("mem", 100.0)
        c.record("mem", 200.0)
        latest = c.get_latest("mem")
        assert latest is not None
        assert latest.value == 200.0

    def test_get_latest_unknown(self):
        c = MetricCollector()
        assert c.get_latest("nope") is None

    def test_list_metric_names(self):
        c = MetricCollector()
        c.record("alpha", 1.0)
        c.record("beta", 2.0)
        c.record("alpha", 3.0)
        names = c.list_metric_names()
        assert set(names) == {"alpha", "beta"}

    def test_list_metric_names_empty(self):
        c = MetricCollector()
        assert c.list_metric_names() == []

    def test_get_metrics_with_time_filter(self):
        c = MetricCollector()
        old_ts = datetime(2020, 1, 1)
        recent_ts = datetime(2026, 1, 1)
        # Record manually to control timestamps
        c._metrics["x"] = [
            MetricValue(name="x", value=1.0, timestamp=old_ts),
            MetricValue(name="x", value=2.0, timestamp=recent_ts),
        ]
        # Filter with start
        result = c.get_metrics("x", start=datetime(2025, 1, 1))
        assert len(result) == 1
        assert result[0].value == 2.0

    def test_cleanup_old_removes_expired(self):
        c = MetricCollector(retention_minutes=1)
        old_ts = datetime.now() - timedelta(minutes=10)
        c._metrics["stale"] = [
            MetricValue(name="stale", value=1.0, timestamp=old_ts),
        ]
        c.record("fresh", 2.0)
        removed = c.cleanup_old()
        assert removed == 1
        assert c.get_metrics("stale") == []
        assert len(c.get_metrics("fresh")) == 1

    def test_cleanup_old_nothing_to_remove(self):
        c = MetricCollector(retention_minutes=60)
        c.record("recent", 1.0)
        removed = c.cleanup_old()
        assert removed == 0


# ---------------------------------------------------------------
# AlertManager tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestAlertManager:
    """Tests for the AlertManager class."""

    def test_instantiation(self):
        am = AlertManager()
        assert am.get_active_alerts() == []
        assert am.get_alert_history() == []

    def test_add_rule_and_check_fires(self):
        am = AlertManager()
        am.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU too high",
        )
        fired = am.check({"cpu": 0.95})
        assert len(fired) == 1
        assert fired[0].name == "high_cpu"
        assert fired[0].is_active is True

    def test_check_does_not_fire_when_condition_false(self):
        am = AlertManager()
        am.add_rule(
            name="low_mem",
            condition=lambda m: m.get("mem", 100) < 10,
            message="Low memory",
        )
        fired = am.check({"mem": 50})
        assert fired == []

    def test_check_does_not_duplicate_active_alert(self):
        am = AlertManager()
        am.add_rule(
            name="dup",
            condition=lambda m: True,
            message="Always fires",
        )
        first = am.check({})
        assert len(first) == 1
        second = am.check({})
        assert second == []  # should not fire again
        assert len(am.get_active_alerts()) == 1

    def test_check_auto_resolves_when_condition_clears(self):
        am = AlertManager()
        am.add_rule(
            name="flaky",
            condition=lambda m: m.get("val", 0) > 50,
            message="Too high",
        )
        am.check({"val": 100})
        assert len(am.get_active_alerts()) == 1
        am.check({"val": 10})
        assert len(am.get_active_alerts()) == 0

    def test_check_handles_exception_in_condition(self):
        am = AlertManager()
        am.add_rule(
            name="broken",
            condition=lambda m: 1 / 0,  # ZeroDivisionError
            message="Should not fire",
        )
        fired = am.check({})
        assert fired == []

    def test_acknowledge_existing_alert(self):
        am = AlertManager()
        am.add_rule(
            name="ack_test",
            condition=lambda m: True,
            message="Ack me",
        )
        fired = am.check({})
        alert_id = fired[0].id
        result = am.acknowledge(alert_id)
        assert result is True
        assert len(am.get_active_alerts()) == 0

    def test_acknowledge_nonexistent_alert(self):
        am = AlertManager()
        assert am.acknowledge("fake_id") is False

    def test_get_alert_history_returns_all(self):
        am = AlertManager()
        am.add_rule(
            name="hist",
            condition=lambda m: m.get("x", 0) > 0,
            message="History test",
        )
        am.check({"x": 1})
        am.check({"x": 0})  # resolves
        am.check({"x": 1})  # fires again
        history = am.get_alert_history()
        assert len(history) == 2

    def test_get_alert_history_with_limit(self):
        am = AlertManager()
        am.add_rule(name="r", condition=lambda m: m.get("x", 0) > 0, message="m")
        for _ in range(5):
            am.check({"x": 1})
            am.check({"x": 0})
        history = am.get_alert_history(limit=3)
        assert len(history) == 3

    def test_custom_severity(self):
        am = AlertManager()
        am.add_rule(
            name="crit",
            condition=lambda m: True,
            message="Critical",
            severity=AlertSeverity.CRITICAL,
        )
        fired = am.check({})
        assert fired[0].severity is AlertSeverity.CRITICAL


# ---------------------------------------------------------------
# DashboardManager tests
# ---------------------------------------------------------------

@pytest.mark.unit
class TestDashboardManager:
    """Tests for the DashboardManager class."""

    def test_instantiation_default_collector(self):
        dm = DashboardManager()
        assert isinstance(dm.collector, MetricCollector)

    def test_instantiation_custom_collector(self):
        c = MetricCollector(retention_minutes=5)
        dm = DashboardManager(collector=c)
        assert dm.collector is c

    def test_create_dashboard(self):
        dm = DashboardManager()
        dash = dm.create("System Overview", description="Main dashboard")
        assert dash.name == "System Overview"
        assert dash.id == "system_overview"
        assert dash.description == "Main dashboard"

    def test_create_dashboard_with_tags(self):
        dm = DashboardManager()
        dash = dm.create("Net", tags=["network", "infra"])
        assert dash.tags == ["network", "infra"]

    def test_get_existing_dashboard(self):
        dm = DashboardManager()
        created = dm.create("Test")
        fetched = dm.get("test")
        assert fetched is created

    def test_get_nonexistent_dashboard(self):
        dm = DashboardManager()
        assert dm.get("no_such") is None

    def test_list_dashboards(self):
        dm = DashboardManager()
        dm.create("A")
        dm.create("B")
        dashboards = dm.list()
        assert len(dashboards) == 2

    def test_list_dashboards_empty(self):
        dm = DashboardManager()
        assert dm.list() == []

    def test_delete_dashboard(self):
        dm = DashboardManager()
        dm.create("Delete Me")
        assert dm.delete("delete_me") is True
        assert dm.get("delete_me") is None

    def test_delete_nonexistent_dashboard(self):
        dm = DashboardManager()
        assert dm.delete("nope") is False

    def test_get_panel_data_with_metrics(self):
        c = MetricCollector()
        c.record("cpu_usage", 0.8)
        c.record("cpu_usage", 0.9)
        dm = DashboardManager(collector=c)
        dash = dm.create("Metrics")
        panel = Panel(id="cpu_panel", title="CPU", metrics=["cpu_usage"])
        dash.add_panel(panel)
        data = dm.get_panel_data("metrics", "cpu_panel")
        assert len(data) == 2
        assert data[0].value == 0.8

    def test_get_panel_data_unknown_dashboard(self):
        dm = DashboardManager()
        assert dm.get_panel_data("unknown", "p1") == []

    def test_get_panel_data_unknown_panel(self):
        dm = DashboardManager()
        dm.create("Exists")
        assert dm.get_panel_data("exists", "no_panel") == []

    def test_slug_generation(self):
        assert DashboardManager._slug("Hello World") == "hello_world"
        assert DashboardManager._slug("single") == "single"
        assert DashboardManager._slug("A B C") == "a_b_c"
