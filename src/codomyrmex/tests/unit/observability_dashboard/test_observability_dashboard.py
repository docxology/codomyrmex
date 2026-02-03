"""Unit tests for observability_dashboard module."""
import pytest
from datetime import datetime, timedelta


@pytest.mark.unit
class TestObservabilityDashboardImports:
    """Test suite for observability_dashboard module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import observability_dashboard
        assert observability_dashboard is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.observability_dashboard import __all__
        expected_exports = [
            "MetricType",
            "AlertSeverity",
            "PanelType",
            "MetricValue",
            "Alert",
            "Panel",
            "Dashboard",
            "MetricCollector",
            "AlertManager",
            "DashboardManager",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestMetricType:
    """Test suite for MetricType enum."""

    def test_metric_type_values(self):
        """Verify all metric types are available."""
        from codomyrmex.observability_dashboard import MetricType

        assert MetricType.COUNTER.value == "counter"
        assert MetricType.GAUGE.value == "gauge"
        assert MetricType.HISTOGRAM.value == "histogram"
        assert MetricType.SUMMARY.value == "summary"


@pytest.mark.unit
class TestAlertSeverity:
    """Test suite for AlertSeverity enum."""

    def test_alert_severity_values(self):
        """Verify all alert severities are available."""
        from codomyrmex.observability_dashboard import AlertSeverity

        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


@pytest.mark.unit
class TestPanelType:
    """Test suite for PanelType enum."""

    def test_panel_type_values(self):
        """Verify all panel types are available."""
        from codomyrmex.observability_dashboard import PanelType

        assert PanelType.GRAPH.value == "graph"
        assert PanelType.STAT.value == "stat"
        assert PanelType.TABLE.value == "table"
        assert PanelType.HEATMAP.value == "heatmap"
        assert PanelType.GAUGE.value == "gauge"
        assert PanelType.LOG.value == "log"


@pytest.mark.unit
class TestMetricValue:
    """Test suite for MetricValue dataclass."""

    def test_metric_value_creation(self):
        """Verify MetricValue can be created."""
        from codomyrmex.observability_dashboard import MetricValue, MetricType

        metric = MetricValue(
            name="cpu_usage",
            value=0.75,
            labels={"host": "server1"},
            metric_type=MetricType.GAUGE,
        )

        assert metric.name == "cpu_usage"
        assert metric.value == 0.75
        assert metric.labels["host"] == "server1"

    def test_metric_value_to_dict(self):
        """Verify metric serialization."""
        from codomyrmex.observability_dashboard import MetricValue

        metric = MetricValue(name="test", value=42.0)
        result = metric.to_dict()

        assert result["name"] == "test"
        assert result["value"] == 42.0


@pytest.mark.unit
class TestAlert:
    """Test suite for Alert dataclass."""

    def test_alert_creation(self):
        """Verify Alert can be created."""
        from codomyrmex.observability_dashboard import Alert, AlertSeverity

        alert = Alert(
            id="alert_1",
            name="high_cpu",
            message="CPU usage exceeded 90%",
            severity=AlertSeverity.WARNING,
        )

        assert alert.id == "alert_1"
        assert alert.name == "high_cpu"
        assert alert.is_active is True

    def test_alert_resolve(self):
        """Verify alert resolution."""
        from codomyrmex.observability_dashboard import Alert

        alert = Alert(id="test", name="test", message="Test alert")

        assert alert.is_active is True
        alert.resolve()
        assert alert.is_active is False
        assert alert.resolved_at is not None

    def test_alert_duration(self):
        """Verify duration calculation."""
        from codomyrmex.observability_dashboard import Alert

        alert = Alert(id="test", name="test", message="Test")

        # Active alert - duration should be positive
        assert alert.duration.total_seconds() >= 0

    def test_alert_to_dict(self):
        """Verify alert serialization."""
        from codomyrmex.observability_dashboard import Alert, AlertSeverity

        alert = Alert(
            id="test",
            name="test_alert",
            message="Test message",
            severity=AlertSeverity.ERROR,
        )

        result = alert.to_dict()
        assert result["id"] == "test"
        assert result["severity"] == "error"
        assert result["is_active"] is True


@pytest.mark.unit
class TestPanel:
    """Test suite for Panel dataclass."""

    def test_panel_creation(self):
        """Verify Panel can be created."""
        from codomyrmex.observability_dashboard import Panel, PanelType

        panel = Panel(
            id="cpu_panel",
            title="CPU Usage",
            panel_type=PanelType.GRAPH,
            metrics=["cpu_usage", "cpu_system"],
        )

        assert panel.id == "cpu_panel"
        assert panel.panel_type == PanelType.GRAPH
        assert len(panel.metrics) == 2

    def test_panel_to_dict(self):
        """Verify panel serialization."""
        from codomyrmex.observability_dashboard import Panel, PanelType

        panel = Panel(
            id="test",
            title="Test Panel",
            panel_type=PanelType.STAT,
        )

        result = panel.to_dict()
        assert result["id"] == "test"
        assert result["type"] == "stat"


@pytest.mark.unit
class TestDashboard:
    """Test suite for Dashboard dataclass."""

    def test_dashboard_creation(self):
        """Verify Dashboard can be created."""
        from codomyrmex.observability_dashboard import Dashboard

        dashboard = Dashboard(
            id="system_overview",
            name="System Overview",
            description="Main system monitoring dashboard",
            tags=["production", "system"],
        )

        assert dashboard.id == "system_overview"
        assert len(dashboard.panels) == 0

    def test_dashboard_add_panel(self):
        """Verify panel addition."""
        from codomyrmex.observability_dashboard import Dashboard, Panel, PanelType

        dashboard = Dashboard(id="test", name="Test")
        panel = Panel(id="p1", title="Panel 1", panel_type=PanelType.GRAPH)

        dashboard.add_panel(panel)

        assert len(dashboard.panels) == 1

    def test_dashboard_get_panel(self):
        """Verify panel retrieval."""
        from codomyrmex.observability_dashboard import Dashboard, Panel, PanelType

        dashboard = Dashboard(id="test", name="Test")
        dashboard.add_panel(Panel(id="p1", title="P1", panel_type=PanelType.GRAPH))
        dashboard.add_panel(Panel(id="p2", title="P2", panel_type=PanelType.STAT))

        panel = dashboard.get_panel("p1")
        assert panel is not None
        assert panel.id == "p1"

        missing = dashboard.get_panel("nonexistent")
        assert missing is None

    def test_dashboard_chaining(self):
        """Verify method chaining."""
        from codomyrmex.observability_dashboard import Dashboard, Panel, PanelType

        dashboard = (
            Dashboard(id="test", name="Test")
            .add_panel(Panel(id="p1", title="P1", panel_type=PanelType.GRAPH))
            .add_panel(Panel(id="p2", title="P2", panel_type=PanelType.STAT))
        )

        assert len(dashboard.panels) == 2

    def test_dashboard_to_dict(self):
        """Verify dashboard serialization."""
        from codomyrmex.observability_dashboard import Dashboard

        dashboard = Dashboard(
            id="test",
            name="Test Dashboard",
            tags=["test"],
        )

        result = dashboard.to_dict()
        assert result["id"] == "test"
        assert "test" in result["tags"]


@pytest.mark.unit
class TestMetricCollector:
    """Test suite for MetricCollector."""

    def test_collector_record(self):
        """Verify metric recording."""
        from codomyrmex.observability_dashboard import MetricCollector

        collector = MetricCollector()
        collector.record("cpu_usage", 0.75, labels={"host": "server1"})

        metrics = collector.get_metrics("cpu_usage")
        assert len(metrics) == 1
        assert metrics[0].value == 0.75

    def test_collector_get_latest(self):
        """Verify latest metric retrieval."""
        from codomyrmex.observability_dashboard import MetricCollector

        collector = MetricCollector()
        collector.record("cpu_usage", 0.5)
        collector.record("cpu_usage", 0.6)
        collector.record("cpu_usage", 0.7)

        latest = collector.get_latest("cpu_usage")
        assert latest is not None
        assert latest.value == 0.7

    def test_collector_get_latest_missing(self):
        """Verify get_latest returns None for missing metric."""
        from codomyrmex.observability_dashboard import MetricCollector

        collector = MetricCollector()
        latest = collector.get_latest("nonexistent")

        assert latest is None

    def test_collector_list_metric_names(self):
        """Verify metric names listing."""
        from codomyrmex.observability_dashboard import MetricCollector

        collector = MetricCollector()
        collector.record("cpu", 0.5)
        collector.record("memory", 0.6)
        collector.record("disk", 0.7)

        names = collector.list_metric_names()
        assert "cpu" in names
        assert "memory" in names
        assert "disk" in names

    def test_collector_get_metrics_with_time_range(self):
        """Verify time-filtered metric retrieval."""
        from codomyrmex.observability_dashboard import MetricCollector

        collector = MetricCollector()
        now = datetime.now()

        collector.record("test", 1.0)

        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        metrics = collector.get_metrics("test", start=start, end=end)
        assert len(metrics) == 1

    def test_collector_cleanup_old(self):
        """Verify old metrics cleanup."""
        from codomyrmex.observability_dashboard import MetricCollector, MetricValue

        collector = MetricCollector(retention_minutes=60)

        # Add old metric manually
        old_metric = MetricValue(
            name="old_metric",
            value=1.0,
            timestamp=datetime.now() - timedelta(hours=2),
        )
        collector._metrics["old_metric"] = [old_metric]

        removed = collector.cleanup_old()
        assert removed >= 1


@pytest.mark.unit
class TestAlertManager:
    """Test suite for AlertManager."""

    def test_manager_add_rule(self):
        """Verify rule addition."""
        from codomyrmex.observability_dashboard import AlertManager, AlertSeverity

        manager = AlertManager()
        manager.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="High CPU usage",
            severity=AlertSeverity.WARNING,
        )

        assert "high_cpu" in manager._rules

    def test_manager_check_fires_alert(self):
        """Verify alert firing."""
        from codomyrmex.observability_dashboard import AlertManager

        manager = AlertManager()
        manager.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU too high",
        )

        alerts = manager.check({"cpu": 0.95})

        assert len(alerts) == 1
        assert alerts[0].name == "high_cpu"

    def test_manager_check_no_alert_below_threshold(self):
        """Verify no alert when below threshold."""
        from codomyrmex.observability_dashboard import AlertManager

        manager = AlertManager()
        manager.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU too high",
        )

        alerts = manager.check({"cpu": 0.5})

        assert len(alerts) == 0

    def test_manager_get_active_alerts(self):
        """Verify active alerts retrieval."""
        from codomyrmex.observability_dashboard import AlertManager

        manager = AlertManager()
        manager.add_rule(
            name="test",
            condition=lambda m: m.get("value", 0) > 0,
            message="Test alert",
        )

        manager.check({"value": 1})

        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].is_active is True

    def test_manager_auto_resolve(self):
        """Verify automatic alert resolution."""
        from codomyrmex.observability_dashboard import AlertManager

        manager = AlertManager()
        manager.add_rule(
            name="test",
            condition=lambda m: m.get("value", 0) > 0.5,
            message="Test alert",
        )

        # Fire alert
        manager.check({"value": 0.8})
        assert len(manager.get_active_alerts()) == 1

        # Auto-resolve when below threshold
        manager.check({"value": 0.3})
        assert len(manager.get_active_alerts()) == 0

    def test_manager_acknowledge(self):
        """Verify alert acknowledgment."""
        from codomyrmex.observability_dashboard import AlertManager

        manager = AlertManager()
        manager.add_rule(
            name="test",
            condition=lambda m: True,
            message="Test",
        )

        alerts = manager.check({})
        alert_id = alerts[0].id

        result = manager.acknowledge(alert_id)
        assert result is True
        assert len(manager.get_active_alerts()) == 0

    def test_manager_get_alert_history(self):
        """Verify alert history retrieval."""
        from codomyrmex.observability_dashboard import AlertManager

        manager = AlertManager()
        manager.add_rule(name="test", condition=lambda m: True, message="Test")

        manager.check({})

        history = manager.get_alert_history(limit=10)
        assert len(history) >= 1


@pytest.mark.unit
class TestDashboardManager:
    """Test suite for DashboardManager."""

    def test_manager_create_dashboard(self):
        """Verify dashboard creation."""
        from codomyrmex.observability_dashboard import DashboardManager

        manager = DashboardManager()
        dashboard = manager.create(
            name="System Overview",
            description="Main monitoring dashboard",
            tags=["production"],
        )

        assert dashboard.name == "System Overview"
        assert dashboard.id == "system_overview"

    def test_manager_get_dashboard(self):
        """Verify dashboard retrieval."""
        from codomyrmex.observability_dashboard import DashboardManager

        manager = DashboardManager()
        manager.create(name="Test Dashboard")

        dashboard = manager.get("test_dashboard")
        assert dashboard is not None
        assert dashboard.name == "Test Dashboard"

    def test_manager_list_dashboards(self):
        """Verify dashboard listing."""
        from codomyrmex.observability_dashboard import DashboardManager

        manager = DashboardManager()
        manager.create(name="Dashboard A")
        manager.create(name="Dashboard B")

        dashboards = manager.list()
        assert len(dashboards) == 2

    def test_manager_delete_dashboard(self):
        """Verify dashboard deletion."""
        from codomyrmex.observability_dashboard import DashboardManager

        manager = DashboardManager()
        manager.create(name="To Delete")

        deleted = manager.delete("to_delete")
        assert deleted is True

        dashboard = manager.get("to_delete")
        assert dashboard is None

    def test_manager_get_panel_data(self):
        """Verify panel data retrieval."""
        from codomyrmex.observability_dashboard import (
            DashboardManager, MetricCollector, Panel, PanelType
        )

        collector = MetricCollector()
        collector.record("cpu_usage", 0.5)
        collector.record("cpu_usage", 0.6)

        manager = DashboardManager(collector=collector)
        dashboard = manager.create(name="Test")
        dashboard.add_panel(Panel(
            id="cpu_panel",
            title="CPU",
            panel_type=PanelType.GRAPH,
            metrics=["cpu_usage"],
        ))

        data = manager.get_panel_data("test", "cpu_panel")
        assert len(data) == 2

    def test_manager_get_panel_data_missing_dashboard(self):
        """Verify empty data for missing dashboard."""
        from codomyrmex.observability_dashboard import DashboardManager

        manager = DashboardManager()
        data = manager.get_panel_data("nonexistent", "panel")

        assert data == []
