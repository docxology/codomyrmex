"""
Observability Dashboard Module

Unified monitoring dashboards for system observability.
"""

__version__ = "0.1.0"

import json
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from collections.abc import Callable
import builtins


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PanelType(Enum):
    """Dashboard panel types."""
    GRAPH = "graph"
    STAT = "stat"
    TABLE = "table"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    LOG = "log"


@dataclass
class MetricValue:
    """A single metric value."""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "type": self.metric_type.value,
        }


@dataclass
class Alert:
    """An alert notification."""
    id: str
    name: str
    message: str
    severity: AlertSeverity = AlertSeverity.WARNING
    fired_at: datetime = field(default_factory=datetime.now)
    resolved_at: datetime | None = None
    labels: dict[str, str] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if alert is still active."""
        return self.resolved_at is None

    @property
    def duration(self) -> timedelta:
        """Get alert duration."""
        end = self.resolved_at or datetime.now()
        return end - self.fired_at

    def resolve(self) -> None:
        """Resolve the alert."""
        self.resolved_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "message": self.message,
            "severity": self.severity.value,
            "fired_at": self.fired_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "is_active": self.is_active,
        }


@dataclass
class Panel:
    """A dashboard panel."""
    id: str
    title: str
    panel_type: PanelType
    metrics: list[str] = field(default_factory=list)
    query: str = ""
    options: dict[str, Any] = field(default_factory=dict)
    position: dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.panel_type.value,
            "metrics": self.metrics,
            "position": self.position,
        }


@dataclass
class Dashboard:
    """A complete dashboard."""
    id: str
    name: str
    panels: list[Panel] = field(default_factory=list)
    description: str = ""
    refresh_interval_seconds: int = 30
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_panel(self, panel: Panel) -> "Dashboard":
        """Add a panel to dashboard."""
        self.panels.append(panel)
        return self

    def get_panel(self, panel_id: str) -> Panel | None:
        """Get panel by ID."""
        for p in self.panels:
            if p.id == panel_id:
                return p
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "panels": [p.to_dict() for p in self.panels],
            "tags": self.tags,
        }


class MetricCollector:
    """
    Collects and stores metrics.

    Usage:
        collector = MetricCollector()

        collector.record("http_requests_total", 1, labels={"method": "GET"})
        collector.record("cpu_usage", 0.75)

        metrics = collector.get_metrics("http_requests_total")
    """

    def __init__(self, retention_minutes: int = 60):
        self.retention_minutes = retention_minutes
        self._metrics: dict[str, list[MetricValue]] = {}
        self._lock = threading.Lock()

    def record(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        metric_type: MetricType = MetricType.GAUGE,
    ) -> None:
        """Record a metric value."""
        metric = MetricValue(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=metric_type,
        )

        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = []
            self._metrics[name].append(metric)

    def get_metrics(
        self,
        name: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[MetricValue]:
        """Get metrics by name."""
        if name not in self._metrics:
            return []

        metrics = self._metrics[name]

        if start:
            metrics = [m for m in metrics if m.timestamp >= start]
        if end:
            metrics = [m for m in metrics if m.timestamp <= end]

        return metrics

    def get_latest(self, name: str) -> MetricValue | None:
        """Get latest metric value."""
        metrics = self._metrics.get(name, [])
        return metrics[-1] if metrics else None

    def list_metric_names(self) -> list[str]:
        """List all metric names."""
        return list(self._metrics.keys())

    def cleanup_old(self) -> int:
        """Remove old metrics beyond retention."""
        cutoff = datetime.now() - timedelta(minutes=self.retention_minutes)
        removed = 0

        with self._lock:
            for name in self._metrics:
                before = len(self._metrics[name])
                self._metrics[name] = [m for m in self._metrics[name] if m.timestamp > cutoff]
                removed += before - len(self._metrics[name])

        return removed


class AlertManager:
    """
    Manages alerts and notifications.

    Usage:
        alerts = AlertManager()

        # Define alert rule
        alerts.add_rule(
            name="high_cpu",
            condition=lambda m: m.get("cpu_usage", 0) > 0.9,
            message="CPU usage is high",
        )

        # Check metrics
        alerts.check({"cpu_usage": 0.95})
    """

    def __init__(self):
        self._alerts: dict[str, Alert] = {}
        self._rules: dict[str, dict[str, Any]] = {}
        self._counter = 0
        self._lock = threading.Lock()

    def add_rule(
        self,
        name: str,
        condition: Callable[[dict[str, float]], bool],
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        """Add an alert rule."""
        self._rules[name] = {
            "condition": condition,
            "message": message,
            "severity": severity,
        }

    def check(self, metrics: dict[str, float]) -> list[Alert]:
        """Check metrics against rules and fire alerts."""
        new_alerts = []

        for rule_name, rule in self._rules.items():
            try:
                if rule["condition"](metrics):
                    if rule_name not in self._alerts or not self._alerts[rule_name].is_active:
                        with self._lock:
                            self._counter += 1
                            alert = Alert(
                                id=f"alert_{self._counter}",
                                name=rule_name,
                                message=rule["message"],
                                severity=rule["severity"],
                            )
                            self._alerts[rule_name] = alert
                            new_alerts.append(alert)
                else:
                    if rule_name in self._alerts and self._alerts[rule_name].is_active:
                        self._alerts[rule_name].resolve()
            except Exception:
                pass

        return new_alerts

    def get_active_alerts(self) -> list[Alert]:
        """Get all active alerts."""
        return [a for a in self._alerts.values() if a.is_active]

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """Get alert history."""
        alerts = list(self._alerts.values())
        alerts.sort(key=lambda a: a.fired_at, reverse=True)
        return alerts[:limit]

    def acknowledge(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self._alerts.values():
            if alert.id == alert_id:
                alert.resolve()
                return True
        return False


class DashboardManager:
    """
    Manages dashboards.

    Usage:
        dashboards = DashboardManager(collector)

        # Create dashboard
        dash = dashboards.create("System Overview")

        # Add panels
        dash.add_panel(Panel(
            id="cpu",
            title="CPU Usage",
            panel_type=PanelType.GRAPH,
            metrics=["cpu_usage"],
        ))
    """

    def __init__(self, collector: MetricCollector | None = None):
        self.collector = collector or MetricCollector()
        self._dashboards: dict[str, Dashboard] = {}
        self._lock = threading.Lock()

    def create(
        self,
        name: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Dashboard:
        """Create a new dashboard."""
        dashboard_id = name.lower().replace(" ", "_")

        dashboard = Dashboard(
            id=dashboard_id,
            name=name,
            description=description,
            tags=tags or [],
        )

        with self._lock:
            self._dashboards[dashboard_id] = dashboard

        return dashboard

    def get(self, dashboard_id: str) -> Dashboard | None:
        """Get dashboard by ID."""
        return self._dashboards.get(dashboard_id)

    def list(self) -> list[Dashboard]:
        """List all dashboards."""
        return list(self._dashboards.values())

    def delete(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        with self._lock:
            if dashboard_id in self._dashboards:
                del self._dashboards[dashboard_id]
                return True
        return False

    def get_panel_data(
        self,
        dashboard_id: str,
        panel_id: str,
        duration_minutes: int = 60,
    ) -> builtins.list[MetricValue]:
        """Get data for a panel."""
        dashboard = self.get(dashboard_id)
        if not dashboard:
            return []

        panel = dashboard.get_panel(panel_id)
        if not panel:
            return []

        start = datetime.now() - timedelta(minutes=duration_minutes)

        all_metrics = []
        for metric_name in panel.metrics:
            all_metrics.extend(
                self.collector.get_metrics(metric_name, start=start)
            )

        return all_metrics


__all__ = [
    # Enums
    "MetricType",
    "AlertSeverity",
    "PanelType",
    # Data classes
    "MetricValue",
    "Alert",
    "Panel",
    "Dashboard",
    # Components
    "MetricCollector",
    "AlertManager",
    "DashboardManager",
]
