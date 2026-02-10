"""
Observability Dashboard Module

Unified monitoring dashboards for system observability.
"""

__version__ = "0.1.0"

from .models import Alert, AlertSeverity, Dashboard, MetricType, MetricValue, Panel, PanelType
from .collector import MetricCollector
from .alerting import AlertManager
from .dashboard import DashboardManager

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the observability_dashboard module."""
    return {
        "dashboard": lambda: print(
            "Observability Dashboard\n"
            "  Use DashboardManager to create and manage monitoring dashboards.\n"
            "  Available panel types: " + ", ".join(pt.value for pt in PanelType)
        ),
        "metrics": lambda: print(
            "Key Metrics\n"
            "  Metric types: " + ", ".join(mt.value for mt in MetricType) + "\n"
            "  Use MetricCollector to gather and query metrics.\n"
            "  Use AlertManager to configure alerting on metric thresholds."
        ),
    }


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
    # CLI
    "cli_commands",
]
