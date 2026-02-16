"""Backward-compatible shim -- delegates to config_management.monitoring.watcher."""

from .monitoring.watcher import ConfigWatcher  # noqa: F401
