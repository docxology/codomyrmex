"""Validation Exception Classes.

This module defines exceptions specific to data validation operations
including schema validation, constraint checking, and input validation.
All exceptions inherit from CodomyrmexError for consistent error handling.
"""

from typing import Any

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.exceptions import ValidationError as BaseValidationError


class ValidationError(BaseValidationError):
    """Base exception for validation-related errors.

    This extends the base ValidationError with additional context support
    for field-level validation errors.

    Attributes:
        message: Error description.
        field: The field that failed validation.
        value: The invalid value (truncated for large values).
        rule: The validation rule that was violated.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        rule: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if field:
            self.context["field"] = field
        if value is not None:
            # Truncate large values to avoid huge context
            str_value = str(value)
            self.context["value"] = (
                str_value[:100] + "..." if len(str_value) > 100 else str_value
            )
        if rule:
            self.context["rule"] = rule


class SchemaError(CodomyrmexError):
    """Raised when schema definition or loading fails.

    Attributes:
        message: Error description.
        schema_name: Name of the schema.
        schema_path: Path to the schema file if applicable.
        schema_type: Type of schema (JSON Schema, Pydantic, etc.).
    """

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        schema_path: str | None = None,
        schema_type: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if schema_name:
            self.context["schema_name"] = schema_name
        if schema_path:
            self.context["schema_path"] = schema_path
        if schema_type:
            self.context["schema_type"] = schema_type


class ConstraintViolationError(ValidationError):
    """Raised when a data constraint is violated.

    Attributes:
        message: Error description.
        constraint_name: Name of the violated constraint.
        constraint_type: Type of constraint (unique, foreign_key, range, etc.).
        expected: The expected constraint condition.
        actual: The actual value that violated the constraint.
    """

    def __init__(
        self,
        message: str,
        constraint_name: str | None = None,
        constraint_type: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        if constraint_name:
            self.context["constraint_name"] = constraint_name
        if constraint_type:
            self.context["constraint_type"] = constraint_type
        if expected:
            self.context["expected"] = expected
        if actual:
            self.context["actual"] = actual


class TypeValidationError(ValidationError):
    """Raised when type validation fails.

    Attributes:
        message: Error description.
        expected_type: The expected type.
        actual_type: The actual type received.
        field: The field with type mismatch.
    """

    def __init__(
        self,
        message: str,
        expected_type: str | None = None,
        actual_type: str | None = None,
        field: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, field=field, **kwargs)
        if expected_type:
            self.context["expected_type"] = expected_type
        if actual_type:
            self.context["actual_type"] = actual_type


class RequiredFieldError(ValidationError):
    """Raised when a required field is missing.

    Attributes:
        message: Error description.
        field: The missing required field.
        parent: Parent object or path containing the field.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        parent: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, field=field, **kwargs)
        if parent:
            self.context["parent"] = parent


class RangeValidationError(ValidationError):
    """Raised when a value is outside the valid range.

    Attributes:
        message: Error description.
        field: The field with range violation.
        value: The actual value.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        min_value: Any = None,
        max_value: Any = None,
        **kwargs: Any
    ):
        super().__init__(message, field=field, value=value, **kwargs)
        if min_value is not None:
            self.context["min_value"] = min_value
        if max_value is not None:
            self.context["max_value"] = max_value


class FormatValidationError(ValidationError):
    """Raised when format validation fails (e.g., email, URL, date).

    Attributes:
        message: Error description.
        field: The field with format violation.
        expected_format: The expected format (email, url, date, etc.).
        pattern: The regex pattern if applicable.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        expected_format: str | None = None,
        pattern: str | None = None,
        **kwargs: Any
    ):
        super().__init__(message, field=field, **kwargs)
        if expected_format:
            self.context["expected_format"] = expected_format
        if pattern:
            self.context["pattern"] = pattern


class LengthValidationError(ValidationError):
    """Raised when length validation fails.

    Attributes:
        message: Error description.
        field: The field with length violation.
        actual_length: The actual length.
        min_length: Minimum required length.
        max_length: Maximum allowed length.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        actual_length: int | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        **kwargs: Any
    ):
        super().__init__(message, field=field, **kwargs)
        if actual_length is not None:
            self.context["actual_length"] = actual_length
        if min_length is not None:
            self.context["min_length"] = min_length
        if max_length is not None:
            self.context["max_length"] = max_length


class CustomValidationError(ValidationError):
    """Raised when a custom validation rule fails.

    Attributes:
        message: Error description.
        validator_name: Name of the custom validator.
        field: The field that failed validation.
        details: Additional details about the validation failure.
    """

    def __init__(
        self,
        message: str,
        validator_name: str | None = None,
        field: str | None = None,
        details: dict[str, Any] | None = None,
        **kwargs: Any
    ):
        super().__init__(message, field=field, **kwargs)
        if validator_name:
            self.context["validator_name"] = validator_name
        if details:
            self.context["details"] = details
