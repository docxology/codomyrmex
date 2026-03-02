"""Validation framework supporting JSON Schema, Pydantic, and custom validators.

Provides a unified interface for data validation with three strategies:
JSON Schema validation (default), Pydantic model validation, and custom
callable validators. All strategies return consistent ValidationResult objects.

Example:
    >>> from codomyrmex.validation.validator import Validator
    >>> v = Validator("json_schema")
    >>> result = v.validate({"name": "test"}, {"type": "object", "required": ["name"]})
    >>> result.is_valid
    True
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import jsonschema
from pydantic import ValidationError as PydanticValidationError

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class ValidationError(CodomyrmexError):
    """Raised when validation fails.

    Note:
        Inherits from CodomyrmexError, so str(error) returns
        '[ValidationError] message' with the error_code prefix.
    """

    def __init__(self, message: str, field: str | None = None, code: str | None = None, path: list[str] | None = None):
        """Initialize this instance."""

        super().__init__(message)
        self.field = field
        self.code = code
        self.path = path or []

@dataclass
class ValidationWarning:
    """Validation warning information."""

    field: str
    message: str
    code: str | None = None
    path: list[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)

    def __bool__(self) -> bool:
        """Allow ValidationResult to be used in boolean context.

        Returns:
            True if validation passed (is_valid is True), False otherwise.
        """
        return self.is_valid

class Validator:
    """Base validator with support for JSON Schema, Pydantic, and custom validation.

    Supports three validation strategies selected via validator_type:
        - "json_schema": Validates data against a JSON Schema dict using jsonschema.
        - "pydantic": Validates data against a Pydantic model class.
        - "custom": Validates data using a callable that returns bool or ValidationResult.
    """

    def __init__(self, validator_type: str = "json_schema"):
        """Initialize validator.

        Args:
            validator_type: Type of validator (json_schema, pydantic, custom)
        """
        self.validator_type = validator_type
        self._validators: dict[str, Callable] = {}

    def validate(self, data: Any, schema: Any) -> ValidationResult:
        """Validate data against a schema.

        Args:
            data: Data to validate
            schema: Validation schema

        Returns:
            ValidationResult with validation status and errors
        """
        try:
            if self.validator_type == "json_schema":
                return self._validate_json_schema(data, schema)
            elif self.validator_type == "pydantic":
                return self._validate_pydantic(data, schema)
            elif self.validator_type == "custom":
                return self._validate_custom(data, schema)
            else:
                raise ValueError(f"Unknown validator type: {self.validator_type}")
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"Validation failed: {str(e)}", code="validation_error")]
            )

    def _validate_json_schema(self, data: Any, schema: dict) -> ValidationResult:
        """Validate data against a JSON Schema dict using the jsonschema library.

        Falls back to _basic_validation if jsonschema is not importable.
        """
        try:
            jsonschema.validate(instance=data, schema=schema)
            return ValidationResult(is_valid=True)
        except ImportError:
            logger.warning("jsonschema not available, falling back to basic validation")
            return self._basic_validation(data, schema)
        except Exception as e:
            error = ValidationError(
                message=str(e),
                code="json_schema_error"
            )
            return ValidationResult(is_valid=False, errors=[error])

    def _validate_pydantic(self, data: Any, model: Any) -> ValidationResult:
        """Validate data by instantiating a Pydantic model class.

        If data is a dict, it is unpacked as keyword arguments.
        Pydantic validation errors are converted to ValidationError instances.
        """
        try:

            if isinstance(data, dict):
                model(**data)
            else:
                model(data)
            return ValidationResult(is_valid=True)
        except ImportError:
            logger.warning("pydantic not available")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("Pydantic not available", code="pydantic_not_available")]
            )
        except PydanticValidationError as e:
            errors = []
            for error in e.errors():
                errors.append(ValidationError(
                    message=error.get("msg", "Validation error"),
                    field=".".join(str(x) for x in error.get("loc", [])),
                    code=error.get("type", "validation_error"),
                    path=list(error.get("loc", []))
                ))
            return ValidationResult(is_valid=False, errors=errors)

    def _validate_custom(self, data: Any, validator_func: Callable) -> ValidationResult:
        """Validate data using a custom callable.

        The callable may return a bool, a ValidationResult, or any other value
        (treated as valid). Exceptions are caught and wrapped as errors.
        """
        try:
            result = validator_func(data)
            if isinstance(result, bool):
                return ValidationResult(is_valid=result)
            elif isinstance(result, ValidationResult):
                return result
            else:
                return ValidationResult(is_valid=True)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(f"Custom validation failed: {str(e)}", code="custom_validation_error")]
            )

    def _basic_validation(self, data: Any, schema: dict) -> ValidationResult:
        """Fallback validation without external libraries.

        Performs type checking and required-field validation using only
        built-in Python types. Used when jsonschema is not available.

        Args:
            data: Data to validate.
            schema: JSON Schema-like dict with optional "type" and "required" keys.

        Returns:
            ValidationResult with any type or required-field errors found.
        """
        errors = []
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                errors.append(ValidationError(f"Expected object, got {type(data).__name__}", code="type_error"))
            elif expected_type == "array" and not isinstance(data, list):
                errors.append(ValidationError(f"Expected array, got {type(data).__name__}", code="type_error"))
            elif expected_type == "string" and not isinstance(data, str):
                errors.append(ValidationError(f"Expected string, got {type(data).__name__}", code="type_error"))
            elif expected_type == "integer" and not isinstance(data, int):
                errors.append(ValidationError(f"Expected integer, got {type(data).__name__}", code="type_error"))
            elif expected_type == "number" and not isinstance(data, (int, float)):
                errors.append(ValidationError(f"Expected number, got {type(data).__name__}", code="type_error"))
            elif expected_type == "boolean" and not isinstance(data, bool):
                errors.append(ValidationError(f"Expected boolean, got {type(data).__name__}", code="type_error"))

        if "required" in schema and isinstance(schema.get("type"), str) and schema["type"] == "object":
            for field_name in schema["required"]:
                if field_name not in data:
                    errors.append(ValidationError(f"Required field '{field_name}' is missing", field=field_name, code="required_field_missing"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def is_valid(self, data: Any, schema: Any) -> bool:
        """Return True if data passes validation, False otherwise."""
        result = self.validate(data, schema)
        return result.is_valid

    def get_errors(self, data: Any, schema: Any) -> list[ValidationError]:
        """Return the list of ValidationError objects from validating data."""
        result = self.validate(data, schema)
        return result.errors
