"""
Observability Dashboard Module

Unified monitoring dashboards for system observability.
"""

__version__ = "0.1.0"

from .models import Alert, AlertSeverity, Dashboard, MetricType, MetricValue, Panel, PanelType
from .collector import MetricCollector
from .alerting import AlertManager
from .dashboard import DashboardManager

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
