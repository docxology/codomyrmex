"""Backward-compatible shim -- delegates to config_management.core.config_loader."""

from .core.config_loader import (  # noqa: F401
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    load_configuration,
    validate_configuration,
)
