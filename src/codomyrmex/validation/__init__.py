"""
Validation module for Codomyrmex.

This module provides unified input validation framework with support for
JSON Schema, Pydantic models, and custom validators.
"""

from typing import Any, Optional

from . import rules, sanitizers, schemas
from .contextual import ContextualValidator, ValidationIssue
from .exceptions import (
    ConstraintViolationError,
    CustomValidationError,
    FormatValidationError,
    LengthValidationError,
    RangeValidationError,
    RequiredFieldError,
    SchemaError,
    TypeValidationError,
    ValidationError,
)
from .parser import TypeSafeParser
from .summary import ValidationSummary
from .validation_manager import ValidationManager
from .validator import ValidationResult, ValidationWarning, Validator

__all__ = [
    'rules',
    'sanitizers',
    'schemas',
    # Core classes
    "Validator",
    "ValidationManager",
    "ValidationResult",
    "ValidationWarning",
    "ContextualValidator",
    "ValidationIssue",
    "TypeSafeParser",
    "ValidationSummary",
    # Functions
    "validate",
    "is_valid",
    "get_errors",
    # Exceptions
    "ValidationError",
    "SchemaError",
    "ConstraintViolationError",
    "TypeValidationError",
    "RequiredFieldError",
    "RangeValidationError",
    "FormatValidationError",
    "LengthValidationError",
    "CustomValidationError",
]

__version__ = "0.1.0"


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


