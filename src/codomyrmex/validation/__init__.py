"""
Validation module for Codomyrmex.

This module provides unified input validation framework with support for
JSON Schema, Pydantic models, and custom validators.


Submodules:
    schemas: Consolidated schemas capabilities."""

from typing import Any, Optional

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

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

def cli_commands():
    """Return CLI commands for the validation module."""
    def _validators(**kwargs):
        """List available validators."""
        print("=== Available Validators ===")
        print("  json_schema  - JSON Schema validation (RFC draft)")
        print("  pydantic     - Pydantic model validation")
        print("  custom       - Custom validator functions")
        print("  contextual   - Context-aware validation (ContextualValidator)")
        print("  type_safe    - TypeSafeParser for strict type coercion")

    def _check(**kwargs):
        """Validate a target with --path arg."""
        path = kwargs.get("path")
        if not path:
            print("Usage: validate check --path <file_or_data>")
            return
        import json
        try:
            with open(path) as f:
                data = json.load(f)
            print(f"Loaded {path}: valid JSON with {len(data)} top-level keys")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Validation failed for {path}: {e}")

    return {
        "validators": {"handler": _validators, "help": "List available validators"},
        "check": {"handler": _check, "help": "Validate with --path argument"},
    }


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
    "cli_commands",
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


