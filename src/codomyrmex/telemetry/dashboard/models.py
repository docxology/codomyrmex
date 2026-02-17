"""
Observability Dashboard Models

Data classes and enums for the observability system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


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
