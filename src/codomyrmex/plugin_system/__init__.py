"""
Plugin System for Codomyrmex

This module provides a plugin architecture that allows
extending Codomyrmex functionality through third-party plugins.
"""

from .exceptions import (
    DependencyError,
    HookError,
    LoadError,
    PluginConflictError,
    PluginError,
    PluginStateError,
    PluginValidationError,
)
from .plugin_loader import PluginLoader
from .plugin_manager import PluginManager
from .plugin_registry import Plugin, PluginInfo, PluginRegistry, PluginState, PluginType
from .plugin_validator import PluginValidator

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the plugin_system module."""
    def _list_plugins():
        registry = PluginRegistry()
        plugins = registry.list_plugins()
        if not plugins:
            print("No plugins installed.")
            return
        print("Installed Plugins:")
        for p in plugins:
            print(f"  - {p.name} (v{p.version}) [{p.state.value}]")

    def _plugin_info():
        print(
            "Plugin System Info\n"
            "  Plugin types: " + ", ".join(pt.value for pt in PluginType) + "\n"
            "  Plugin states: " + ", ".join(ps.value for ps in PluginState) + "\n"
            "  Use PluginManager to load, enable, and manage plugins."
        )

    return {
        "plugins": _list_plugins,
        "info": _plugin_info,
    }


__all__ = [
    'PluginManager',
    'PluginValidator',
    'PluginLoader',
    'PluginRegistry',
    'PluginInfo',
    'Plugin',
    'PluginType',
    'PluginState',
    # Exceptions
    'PluginError',
    'LoadError',
    'DependencyError',
    'HookError',
    'PluginValidationError',
    'PluginStateError',
    'PluginConflictError',
    # CLI
    'cli_commands',
]
