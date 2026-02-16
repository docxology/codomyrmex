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
