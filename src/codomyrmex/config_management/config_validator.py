# DEPRECATED(v0.2.0): Shim module. Import from config_management.validation.config_validator instead. Will be removed in v0.3.0.
"""Backward-compatible shim -- delegates to config_management.validation.config_validator."""

from .validation.config_validator import (  # noqa: F401
    ConfigSchema,
    ConfigValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    get_ai_model_config_schema,
    get_database_config_schema,
    get_logging_config_schema,
    validate_config_schema,
)
