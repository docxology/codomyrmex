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
]
