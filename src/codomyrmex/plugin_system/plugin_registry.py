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
