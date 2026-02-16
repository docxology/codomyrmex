"""Backward-compatible re-export from plugin_system.core.plugin_manager."""
from .core.plugin_manager import *  # noqa: F401,F403
from .core.plugin_manager import (
    PluginManager,
    discover_plugins,
    get_plugin_manager,
    load_plugin,
    unload_plugin,
)
