"""Validation and enforcement components for the plugin_system module.

Contains plugin validation logic including metadata checks, dependency
verification, security scanning, and interface enforcement.
"""

from .enforcer import InterfaceEnforcer
from .plugin_validator import PluginValidator, ValidationResult, validate_plugin

__all__ = [
    "PluginValidator",
    "ValidationResult",
    "InterfaceEnforcer",
    "validate_plugin",
]
