# DEPRECATED(v0.2.0): Shim module. Import from plugin_system.validation.plugin_validator instead. Will be removed in v0.3.0.
"""Backward-compatible re-export from plugin_system.validation.plugin_validator."""
from .validation.plugin_validator import *  # noqa: F401,F403
from .validation.plugin_validator import (
    PluginValidator,
    ValidationResult,
    validate_plugin,
)
