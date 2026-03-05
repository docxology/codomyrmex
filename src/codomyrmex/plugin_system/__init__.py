"""
Plugin System for Codomyrmex

This module provides a plugin architecture that allows
extending Codomyrmex functionality through third-party plugins.
"""

from .core.plugin_loader import PluginLoader
from .core.plugin_manager import PluginManager
from .core.plugin_registry import (
    Plugin,
    PluginInfo,
    PluginRegistry,
    PluginState,
    PluginType,
)
from .exceptions import (
    DependencyError,
    HookError,
    LoadError,
    PluginConflictError,
    PluginError,
    PluginStateError,
    PluginValidationError,
)
from .validation.plugin_validator import PluginValidator

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
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
    "DependencyError",
    "HookError",
    "LoadError",
    "Plugin",
    "PluginConflictError",
    # Exceptions
    "PluginError",
    "PluginInfo",
    "PluginLoader",
    "PluginManager",
    "PluginRegistry",
    "PluginState",
    "PluginStateError",
    "PluginType",
    "PluginValidationError",
    "PluginValidator",
    # CLI
    "cli_commands",
]
