# DEPRECATED(v0.2.0): Shim module. Import from plugin_system.core.plugin_loader instead. Will be removed in v0.3.0.
"""Backward-compatible re-export from plugin_system.core.plugin_loader."""
from .core.plugin_loader import *  # noqa: F401,F403
from .core.plugin_loader import (
    LoadResult,
    PluginLoader,
    discover_plugins,
    load_plugin,
    unload_plugin,
)
