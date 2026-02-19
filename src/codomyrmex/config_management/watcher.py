# DEPRECATED(v0.2.0): Shim module. Import from config_management.monitoring.watcher instead. Will be removed in v0.3.0.
"""Backward-compatible shim -- delegates to config_management.monitoring.watcher."""

from .monitoring.watcher import ConfigWatcher  # noqa: F401
