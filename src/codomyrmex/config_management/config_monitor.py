"""Backward-compatible shim -- delegates to config_management.monitoring.config_monitor."""

from .monitoring.config_monitor import (  # noqa: F401
    ConfigAudit,
    ConfigChange,
    ConfigSnapshot,
    ConfigurationMonitor,
    monitor_config_changes,
)
