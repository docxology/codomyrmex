"""
Plugin System for Codomyrmex

This module provides a plugin architecture that allows
extending Codomyrmex functionality through third-party plugins.
"""

from .plugin_manager import PluginManager
from .plugin_validator import PluginValidator
from .plugin_loader import PluginLoader
from .plugin_registry import PluginRegistry, PluginInfo, Plugin, PluginType, PluginState
from .exceptions import (
    PluginError,
    LoadError,
    DependencyError,
    HookError,
    PluginValidationError,
    PluginStateError,
    PluginConflictError,
)

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
