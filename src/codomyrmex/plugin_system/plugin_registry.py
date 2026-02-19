# DEPRECATED(v0.2.0): Shim module. Import from plugin_system.core.plugin_registry instead. Will be removed in v0.3.0.
"""Backward-compatible re-export from plugin_system.core.plugin_registry."""
from .core.plugin_registry import *  # noqa: F401,F403
from .core.plugin_registry import (
    Hook,
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
    create_plugin_info,
    get_registry,
)
