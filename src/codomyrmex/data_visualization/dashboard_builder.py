"""Programmatic dashboard builder.

Constructs dashboard definitions with panels, targets,
thresholds, and annotation support.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PanelTarget:
    """A data source target for a panel.

    Attributes:
        metric: Metric name or query.
        legend: Display legend.
        interval: Query interval.
    """

    metric: str
    legend: str = ""
    interval: str = "1m"


@dataclass
class ThresholdConfig:
    """Threshold line configuration.

    Attributes:
        value: Threshold value.
        color: Display color.
        label: Threshold label.
    """

    value: float
    color: str = "red"
    label: str = ""


@dataclass
class Panel:
    """A dashboard panel.

    Attributes:
        title: Panel title.
        panel_type: Panel type (graph, stat, table, gauge).
        targets: Data source targets.
        thresholds: Threshold lines.
        unit: Display unit.
        width: Panel width (1-24).
        height: Panel height.
    """

    title: str
    panel_type: str = "graph"
    targets: list[PanelTarget] = field(default_factory=list)
    thresholds: list[ThresholdConfig] = field(default_factory=list)
    unit: str = ""
    width: int = 12
    height: int = 8


@dataclass
class Annotation:
    """A dashboard annotation.

    Attributes:
        name: Annotation name.
        query: Query or event source.
        color: Display color.
    """

    name: str
    query: str = ""
    color: str = "blue"


class DashboardBuilder:
    """Programmatic dashboard constructor.

    Example::

        builder = DashboardBuilder(title="Agent Metrics")
        builder.add_panel(Panel(
            title="Latency",
            targets=[PanelTarget(metric="latency_ms")],
        ))
        config = builder.build()
    """

    def __init__(self, title: str = "Dashboard", uid: str = "") -> None:
        self._title = title
        self._uid = uid
        self._panels: list[Panel] = []
        self._annotations: list[Annotation] = []
        self._variables: dict[str, str] = {}
        self._refresh: str = "30s"

    @property
    def panel_count(self) -> int:
        return len(self._panels)

    def add_panel(self, panel: Panel) -> DashboardBuilder:
        """Add a panel to the dashboard."""
        self._panels.append(panel)
        return self

    def add_annotation(self, annotation: Annotation) -> DashboardBuilder:
        """Add an annotation."""
        self._annotations.append(annotation)
        return self

    def set_variable(self, name: str, query: str) -> DashboardBuilder:
        """Add a template variable."""
        self._variables[name] = query
        return self

    def set_refresh(self, interval: str) -> DashboardBuilder:
        """Set auto-refresh interval."""
        self._refresh = interval
        return self

    def build(self) -> dict[str, Any]:
        """Build the dashboard configuration dict.

        Returns:
            Grafana-compatible dashboard JSON structure.
        """
        panels = []
        for i, panel in enumerate(self._panels):
            panel_dict: dict[str, Any] = {
                "id": i + 1,
                "title": panel.title,
                "type": panel.panel_type,
                "gridPos": {
                    "w": panel.width,
                    "h": panel.height,
                    "x": 0,
                    "y": i * panel.height,
                },
                "targets": [
                    {
                        "expr": t.metric,
                        "legendFormat": t.legend,
                        "interval": t.interval,
                    }
                    for t in panel.targets
                ],
            }
            if panel.thresholds:
                panel_dict["thresholds"] = [
                    {"value": t.value, "colorMode": "custom", "fill": True, "line": True, "op": "gt"}
                    for t in panel.thresholds
                ]
            if panel.unit:
                panel_dict["fieldConfig"] = {"defaults": {"unit": panel.unit}}
            panels.append(panel_dict)

        return {
            "title": self._title,
            "uid": self._uid,
            "panels": panels,
            "annotations": {
                "list": [
                    {"name": a.name, "query": a.query, "iconColor": a.color}
                    for a in self._annotations
                ]
            },
            "templating": {
                "list": [
                    {"name": name, "query": query, "type": "query"}
                    for name, query in self._variables.items()
                ]
            },
            "refresh": self._refresh,
        }

    def to_json(self, indent: int = 2) -> str:
        """Export dashboard as JSON string."""
        return json.dumps(self.build(), indent=indent)


__all__ = ["Annotation", "DashboardBuilder", "Panel", "PanelTarget", "ThresholdConfig"]
