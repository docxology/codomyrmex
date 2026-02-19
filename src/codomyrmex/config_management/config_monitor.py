# DEPRECATED(v0.2.0): Shim module. Import from config_management.monitoring.config_monitor instead. Will be removed in v0.3.0.
"""Backward-compatible shim -- delegates to config_management.monitoring.config_monitor."""

from .monitoring.config_monitor import (  # noqa: F401
    ConfigAudit,
    ConfigChange,
    ConfigSnapshot,
    ConfigurationMonitor,
    monitor_config_changes,
)
