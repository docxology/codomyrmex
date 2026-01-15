from typing import Any, Callable, Optional
import json

from dataclasses import dataclass, field
from pydantic import ValidationError as PydanticValidationError
import jsonschema

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

class ValidationError(CodomyrmexError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None, path: Optional[list[str]] = None):

        super().__init__(message)
        self.field = field
        self.code = code
        self.path = path or []

@dataclass
class ValidationWarning:
    """Validation warning information."""

    field: str
    message: str
    code: Optional[str] = None
    path: list[str] = field(default_factory=list)

@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)

    def __bool__(self) -> bool:

        return self.is_valid

class Validator:
    """Base validator interface."""

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
        """Validate using JSON Schema."""
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
        """Validate using Pydantic model."""
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
        """Validate using custom validator function."""
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
        """Basic validation without external libraries."""
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
        """Check if data is valid against a schema."""
        result = self.validate(data, schema)
        return result.is_valid

    def get_errors(self, data: Any, schema: Any) -> list[ValidationError]:
        """Get validation errors for data."""
        result = self.validate(data, schema)
        return result.errors
