# DEPRECATED(v0.2.0): Shim module. Import from config_management.core.config_loader instead. Will be removed in v0.3.0.
"""Backward-compatible shim -- delegates to config_management.core.config_loader."""

from .core.config_loader import (  # noqa: F401
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    load_configuration,
    validate_configuration,
)
