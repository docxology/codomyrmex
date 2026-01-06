"""
Validation module for Codomyrmex.

This module provides unified input validation framework with support for
JSON Schema, Pydantic models, and custom validators.
"""

from typing import Any, Optional

from codomyrmex.exceptions import CodomyrmexError

from .validator import ValidationError, ValidationResult, ValidationWarning, Validator
from .validation_manager import ValidationManager

__all__ = [
    "Validator",
    "ValidationManager",
    "ValidationResult",
    "ValidationError",
    "ValidationWarning",
    "validate",
    "is_valid",
    "get_errors",
]

__version__ = "0.1.0"


class ValidationError(CodomyrmexError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        super().__init__(message)
        self.field = field
        self.code = code


def validate(data: Any, schema: Any, validator_type: str = "json_schema") -> "ValidationResult":
    """Validate data against a schema."""
    validator = Validator(validator_type=validator_type)
    return validator.validate(data, schema)


def is_valid(data: Any, schema: Any, validator_type: str = "json_schema") -> bool:
    """Check if data is valid against a schema."""
    result = validate(data, schema, validator_type)
    return result.is_valid


def get_errors(data: Any, schema: Any, validator_type: str = "json_schema") -> list["ValidationError"]:
    """Get validation errors for data."""
    result = validate(data, schema, validator_type)
    return result.errors

