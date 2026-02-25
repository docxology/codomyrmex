"""Export metrics as Grafana-compatible dashboard JSON."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Panel:
    """A dashboard panel.

    Attributes:
        title: Panel title.
        panel_type: ``graph``, ``stat``, ``gauge``, ``table``.
        metric: Metric query.
        thresholds: Alert thresholds.
    """

    title: str
    panel_type: str = "graph"
    metric: str = ""
    thresholds: list[float] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "title": self.title,
            "type": self.panel_type,
            "targets": [{"expr": self.metric}],
            "fieldConfig": {
                "defaults": {
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            *[{"color": "red", "value": t} for t in self.thresholds],
                        ]
                    }
                }
            },
        }


@dataclass
class Dashboard:
    """A Grafana-compatible dashboard.

    Attributes:
        title: Dashboard title.
        panels: Dashboard panels.
        refresh: Refresh interval.
    """

    title: str = "Codomyrmex Agent Dashboard"
    panels: list[Panel] = field(default_factory=list)
    refresh: str = "30s"

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "dashboard": {
                "title": self.title,
                "refresh": self.refresh,
                "panels": [p.to_dict() for p in self.panels],
                "schemaVersion": 39,
            }
        }


class DashboardExporter:
    """Export agent metrics as Grafana dashboard JSON.

    Usage::

        exporter = DashboardExporter()
        exporter.add_panel(Panel("Request Rate", "graph", "rate(requests_total[5m])"))
        dashboard = exporter.export()
    """

    def __init__(self, title: str = "Codomyrmex Agent Dashboard") -> None:
        """Execute   Init   operations natively."""
        self._dashboard = Dashboard(title=title)

    def add_panel(self, panel: Panel) -> None:
        """Execute Add Panel operations natively."""
        self._dashboard.panels.append(panel)

    def export(self) -> dict[str, Any]:
        """Execute Export operations natively."""
        return self._dashboard.to_dict()

    @property
    def panel_count(self) -> int:
        """Execute Panel Count operations natively."""
        return len(self._dashboard.panels)

    @classmethod
    def agent_dashboard(cls) -> DashboardExporter:
        """Pre-configured dashboard for agent monitoring."""
        exp = cls("Agent Operations")
        exp.add_panel(Panel("Task Success Rate", "stat", "agent_task_success_rate", [0.9]))
        exp.add_panel(Panel("Error Rate", "graph", "rate(agent_errors_total[5m])", [0.05]))
        exp.add_panel(Panel("Latency P99", "graph", "histogram_quantile(0.99, agent_latency)", [1000]))
        exp.add_panel(Panel("Active Agents", "gauge", "agent_pool_active", [10]))
        return exp


__all__ = ["Dashboard", "DashboardExporter", "Panel"]
