"""
Dashboard Manager

Dashboard creation and management for observability.
"""

import builtins
import threading
from datetime import datetime, timedelta

from .collector import MetricCollector
from .models import Dashboard, MetricValue


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
        """Initialize this instance."""
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
