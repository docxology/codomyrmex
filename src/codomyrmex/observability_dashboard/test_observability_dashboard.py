"""
Tests for Observability Dashboard Module
"""

import pytest
from datetime import datetime, timedelta
from codomyrmex.observability_dashboard import (
    MetricType,
    AlertSeverity,
    PanelType,
    MetricValue,
    Alert,
    Panel,
    Dashboard,
    MetricCollector,
    AlertManager,
    DashboardManager,
)


class TestMetricValue:
    """Tests for MetricValue."""
    
    def test_create(self):
        """Should create metric value."""
        m = MetricValue(name="cpu_usage", value=0.75)
        assert m.name == "cpu_usage"
        assert m.value == 0.75
    
    def test_to_dict(self):
        """Should convert to dict."""
        m = MetricValue(name="requests", value=100, labels={"method": "GET"})
        d = m.to_dict()
        assert d["name"] == "requests"
        assert d["labels"]["method"] == "GET"


class TestAlert:
    """Tests for Alert."""
    
    def test_create(self):
        """Should create alert."""
        a = Alert(id="a1", name="high_cpu", message="CPU high")
        assert a.is_active
    
    def test_resolve(self):
        """Should resolve alert."""
        a = Alert(id="a1", name="test", message="test")
        a.resolve()
        assert not a.is_active
    
    def test_duration(self):
        """Should calculate duration."""
        a = Alert(id="a1", name="test", message="test")
        assert a.duration.total_seconds() >= 0


class TestDashboard:
    """Tests for Dashboard."""
    
    def test_add_panel(self):
        """Should add panel."""
        dash = Dashboard(id="d1", name="Test Dashboard")
        dash.add_panel(Panel(id="p1", title="CPU", panel_type=PanelType.GRAPH))
        
        assert len(dash.panels) == 1
    
    def test_get_panel(self):
        """Should get panel by ID."""
        dash = Dashboard(id="d1", name="Test")
        dash.add_panel(Panel(id="p1", title="Test", panel_type=PanelType.STAT))
        
        assert dash.get_panel("p1").title == "Test"
        assert dash.get_panel("missing") is None


class TestMetricCollector:
    """Tests for MetricCollector."""
    
    def test_record(self):
        """Should record metrics."""
        collector = MetricCollector()
        collector.record("cpu", 0.5)
        collector.record("cpu", 0.6)
        
        metrics = collector.get_metrics("cpu")
        assert len(metrics) == 2
    
    def test_get_latest(self):
        """Should get latest metric."""
        collector = MetricCollector()
        collector.record("test", 1)
        collector.record("test", 2)
        
        latest = collector.get_latest("test")
        assert latest.value == 2
    
    def test_list_names(self):
        """Should list metric names."""
        collector = MetricCollector()
        collector.record("a", 1)
        collector.record("b", 2)
        
        names = collector.list_metric_names()
        assert "a" in names
        assert "b" in names


class TestAlertManager:
    """Tests for AlertManager."""
    
    def test_add_rule(self):
        """Should add alert rule."""
        manager = AlertManager()
        manager.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU high",
        )
        
        assert "high_cpu" in manager._rules
    
    def test_check_fires_alert(self):
        """Should fire alert when condition met."""
        manager = AlertManager()
        manager.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU high",
        )
        
        alerts = manager.check({"cpu": 0.95})
        assert len(alerts) == 1
        assert alerts[0].name == "high_cpu"
    
    def test_check_no_duplicate(self):
        """Should not fire duplicate alerts."""
        manager = AlertManager()
        manager.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu", 0) > 0.9,
            message="CPU high",
        )
        
        manager.check({"cpu": 0.95})
        alerts2 = manager.check({"cpu": 0.95})
        
        assert len(alerts2) == 0
    
    def test_get_active_alerts(self):
        """Should get active alerts."""
        manager = AlertManager()
        manager.add_rule(
            name="test",
            condition=lambda m: True,
            message="Test",
        )
        
        manager.check({})
        active = manager.get_active_alerts()
        
        assert len(active) == 1


class TestDashboardManager:
    """Tests for DashboardManager."""
    
    def test_create(self):
        """Should create dashboard."""
        manager = DashboardManager()
        dash = manager.create("Test Dashboard")
        
        assert dash.name == "Test Dashboard"
    
    def test_get(self):
        """Should get dashboard."""
        manager = DashboardManager()
        manager.create("Test")
        
        assert manager.get("test").name == "Test"
    
    def test_delete(self):
        """Should delete dashboard."""
        manager = DashboardManager()
        manager.create("Test")
        
        assert manager.delete("test") is True
        assert manager.get("test") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
