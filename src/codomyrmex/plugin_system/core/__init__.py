"""Core plugin management components for the plugin_system module.

Contains the plugin manager, loader, and registry that form the backbone
of the plugin architecture.
"""

from .plugin_loader import LoadResult, PluginLoader
from .plugin_loader import discover_plugins as loader_discover_plugins
from .plugin_loader import load_plugin as loader_load_plugin
from .plugin_loader import unload_plugin as loader_unload_plugin
from .plugin_manager import (
    PluginManager,
    discover_plugins,
    get_plugin_manager,
    load_plugin,
    unload_plugin,
)
from .plugin_registry import (
    Hook,
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
    create_plugin_info,
    get_registry,
)

__all__ = [
    "PluginManager",
    "PluginLoader",
    "PluginRegistry",
    "Plugin",
    "PluginInfo",
    "PluginType",
    "PluginState",
    "Hook",
    "LoadResult",
    "get_plugin_manager",
    "get_registry",
    "create_plugin_info",
    "discover_plugins",
    "load_plugin",
    "unload_plugin",
]
