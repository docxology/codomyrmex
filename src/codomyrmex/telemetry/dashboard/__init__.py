"""Observability Dashboard Module.

Provides metric collection, alerting, and dashboard management for
telemetry observability.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import uuid4


# ------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------

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


# ------------------------------------------------------------------
# Data classes
# ------------------------------------------------------------------

@dataclass
class MetricValue:
    """A single metric measurement."""
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Alert:
    """An alert instance."""
    id: str
    name: str
    message: str
    severity: AlertSeverity = AlertSeverity.WARNING
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    def resolve(self) -> None:
        """Resolve this alert."""
        self.is_active = False
        self.resolved_at = datetime.now()

    @property
    def duration(self) -> timedelta:
        """Duration since creation."""
        end = self.resolved_at or datetime.now()
        return end - self.created_at

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "message": self.message,
            "severity": self.severity.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class Panel:
    """A dashboard panel."""
    id: str
    title: str
    panel_type: PanelType = PanelType.GRAPH
    metrics: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "title": self.title,
            "type": self.panel_type.value,
            "metrics": self.metrics,
            "config": self.config,
        }


class Dashboard:
    """An observability dashboard."""

    def __init__(
        self,
        id: str,
        name: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags or []
        self.panels: list[Panel] = []
        self.created_at = datetime.now()

    def add_panel(self, panel: Panel) -> "Dashboard":
        """Add a panel. Returns self for chaining."""
        self.panels.append(panel)
        return self

    def get_panel(self, panel_id: str) -> Optional[Panel]:
        """Get a panel by ID."""
        for p in self.panels:
            if p.id == panel_id:
                return p
        return None

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "panels": [p.to_dict() for p in self.panels],
            "created_at": self.created_at.isoformat(),
        }


# ------------------------------------------------------------------
# Collectors and Managers
# ------------------------------------------------------------------

class MetricCollector:
    """Collects and stores metric values."""

    def __init__(self, retention_minutes: int = 1440) -> None:
        """Execute   Init   operations natively."""
        self.retention_minutes = retention_minutes
        self._metrics: dict[str, list[MetricValue]] = {}

    def record(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
        metric_type: MetricType = MetricType.GAUGE,
    ) -> None:
        """Record a metric value."""
        mv = MetricValue(
            name=name,
            value=value,
            labels=labels or {},
            metric_type=metric_type,
        )
        self._metrics.setdefault(name, []).append(mv)

    def get_metrics(
        self,
        name: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[MetricValue]:
        """Get metrics by name, optionally filtered by time range."""
        metrics = self._metrics.get(name, [])
        if start:
            metrics = [m for m in metrics if m.timestamp >= start]
        if end:
            metrics = [m for m in metrics if m.timestamp <= end]
        return metrics

    def get_latest(self, name: str) -> Optional[MetricValue]:
        """Get the most recent value for a metric."""
        metrics = self._metrics.get(name, [])
        return metrics[-1] if metrics else None

    def list_metric_names(self) -> list[str]:
        """List all recorded metric names."""
        return list(self._metrics.keys())

    def cleanup_old(self) -> int:
        """Remove metrics older than retention period. Returns count removed."""
        cutoff = datetime.now() - timedelta(minutes=self.retention_minutes)
        removed = 0
        for name in list(self._metrics.keys()):
            before = len(self._metrics[name])
            self._metrics[name] = [
                m for m in self._metrics[name] if m.timestamp >= cutoff
            ]
            removed += before - len(self._metrics[name])
            if not self._metrics[name]:
                del self._metrics[name]
        return removed


class AlertManager:
    """Manages alert rules and active alerts."""

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._rules: dict[str, dict[str, Any]] = {}
        self._active_alerts: dict[str, Alert] = {}
        self._history: list[Alert] = []

    def add_rule(
        self,
        name: str,
        condition: Callable[[dict[str, Any]], bool],
        message: str,
        severity: AlertSeverity = AlertSeverity.WARNING,
    ) -> None:
        """Add an alert rule."""
        self._rules[name] = {
            "condition": condition,
            "message": message,
            "severity": severity,
        }

    def check(self, metrics: dict[str, Any]) -> list[Alert]:
        """Check all rules against metrics, fire/resolve alerts."""
        fired: list[Alert] = []
        active_rule_names = set()

        for name, rule in self._rules.items():
            try:
                triggered = rule["condition"](metrics)
            except Exception:
                triggered = False

            if triggered:
                active_rule_names.add(name)
                if name not in self._active_alerts:
                    alert = Alert(
                        id=f"{name}_{uuid4().hex[:8]}",
                        name=name,
                        message=rule["message"],
                        severity=rule["severity"],
                    )
                    self._active_alerts[name] = alert
                    self._history.append(alert)
                    fired.append(alert)

        # Auto-resolve alerts whose rules no longer trigger
        for name in list(self._active_alerts.keys()):
            if name not in active_rule_names:
                self._active_alerts[name].resolve()
                del self._active_alerts[name]

        return fired

    def get_active_alerts(self) -> list[Alert]:
        """Return all currently active alerts."""
        return [a for a in self._active_alerts.values() if a.is_active]

    def acknowledge(self, alert_id: str) -> bool:
        """Acknowledge and resolve an alert by ID."""
        for name, alert in list(self._active_alerts.items()):
            if alert.id == alert_id:
                alert.resolve()
                del self._active_alerts[name]
                return True
        return False

    def get_alert_history(self, limit: int = 100) -> list[Alert]:
        """Return alert history."""
        return self._history[-limit:]


class DashboardManager:
    """Manages dashboard CRUD and data retrieval."""

    def __init__(self, collector: MetricCollector | None = None) -> None:
        """Execute   Init   operations natively."""
        self.collector = collector or MetricCollector()
        self._dashboards: dict[str, Dashboard] = {}

    @staticmethod
    def _slug(name: str) -> str:
        """Generate a URL-safe slug from name."""
        return name.lower().replace(" ", "_")

    def create(
        self,
        name: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Dashboard:
        """Create a new dashboard."""
        dashboard_id = self._slug(name)
        dashboard = Dashboard(
            id=dashboard_id,
            name=name,
            description=description,
            tags=tags,
        )
        self._dashboards[dashboard_id] = dashboard
        return dashboard

    def get(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID."""
        return self._dashboards.get(dashboard_id)

    def list(self) -> list[Dashboard]:
        """List all dashboards."""
        return list(self._dashboards.values())

    def delete(self, dashboard_id: str) -> bool:
        """Delete a dashboard by ID. Returns True if deleted."""
        if dashboard_id in self._dashboards:
            del self._dashboards[dashboard_id]
            return True
        return False

    def get_panel_data(
        self, dashboard_id: str, panel_id: str
    ) -> list[MetricValue]:
        """Get metric data for a panel."""
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return []
        panel = dashboard.get_panel(panel_id)
        if not panel:
            return []
        result: list[MetricValue] = []
        for metric_name in panel.metrics:
            result.extend(self.collector.get_metrics(metric_name))
        return result


__all__ = [
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
