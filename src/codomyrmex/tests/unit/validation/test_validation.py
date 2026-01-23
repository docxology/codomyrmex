"""Tests for the Codomyrmex Validation module.

This module tests the Validator, ValidationResult, ValidationError, and related classes.
"""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel


class TestValidationModuleImport:
    """Tests for module import."""

    def test_validation_module_import(self):
        """Verify that the validation module can be imported successfully."""
        from codomyrmex import validation
        assert validation is not None
        assert hasattr(validation, "__path__")

    def test_validation_module_structure(self):
        """Verify basic structure of validation module."""
        from codomyrmex import validation
        assert hasattr(validation, "__file__")


class TestValidationError:
    """Tests for ValidationError class."""

    def test_create_validation_error(self):
        """Test creating a validation error."""
        from codomyrmex.validation.validator import ValidationError

        error = ValidationError("Field is required", field="name", code="required")

        assert str(error) == "Field is required"
        assert error.field == "name"
        assert error.code == "required"

    def test_validation_error_with_path(self):
        """Test validation error with path."""
        from codomyrmex.validation.validator import ValidationError

        error = ValidationError("Invalid value", path=["data", "items", "0"])

        assert error.path == ["data", "items", "0"]

    def test_validation_error_defaults(self):
        """Test validation error default values."""
        from codomyrmex.validation.validator import ValidationError

        error = ValidationError("Error message")

        assert error.field is None
        assert error.code is None
        assert error.path == []


class TestValidationWarning:
    """Tests for ValidationWarning class."""

    def test_create_validation_warning(self):
        """Test creating a validation warning."""
        from codomyrmex.validation.validator import ValidationWarning

        warning = ValidationWarning(field="age", message="Value seems unusually high")

        assert warning.field == "age"
        assert warning.message == "Value seems unusually high"

    def test_validation_warning_with_code(self):
        """Test validation warning with code."""
        from codomyrmex.validation.validator import ValidationWarning

        warning = ValidationWarning(
            field="email",
            message="Email format is deprecated",
            code="deprecated_format"
        )

        assert warning.code == "deprecated_format"


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_valid_result(self):
        """Test creating a valid result."""
        from codomyrmex.validation.validator import ValidationResult

        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result_with_errors(self):
        """Test creating invalid result with errors."""
        from codomyrmex.validation.validator import ValidationResult, ValidationError

        errors = [ValidationError("Field required", field="name")]
        result = ValidationResult(is_valid=False, errors=errors)

        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_result_bool_conversion(self):
        """Test ValidationResult converts to bool correctly."""
        from codomyrmex.validation.validator import ValidationResult

        valid = ValidationResult(is_valid=True)
        invalid = ValidationResult(is_valid=False)

        assert bool(valid) is True
        assert bool(invalid) is False

    def test_result_with_warnings(self):
        """Test result with warnings."""
        from codomyrmex.validation.validator import ValidationResult, ValidationWarning

        warnings = [ValidationWarning(field="age", message="Unusual value")]
        result = ValidationResult(is_valid=True, warnings=warnings)

        assert result.is_valid is True
        assert len(result.warnings) == 1


class TestValidator:
    """Tests for Validator class."""

    def test_create_validator(self):
        """Test creating a validator."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")

        assert validator.validator_type == "json_schema"

    def test_create_validator_default_type(self):
        """Test validator default type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()

        assert validator.validator_type == "json_schema"

    def test_validate_json_schema_valid(self):
        """Test JSON schema validation with valid data."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }
        data = {"name": "John", "age": 30}

        result = validator.validate(data, schema)

        assert result.is_valid is True

    def test_validate_json_schema_invalid(self):
        """Test JSON schema validation with invalid data."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "required": ["name"]
        }
        data = {}

        result = validator.validate(data, schema)

        assert result.is_valid is False

    def test_validate_json_schema_type_mismatch(self):
        """Test JSON schema validation with type mismatch."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")
        schema = {"type": "object"}
        data = "not an object"

        result = validator.validate(data, schema)

        assert result.is_valid is False

    def test_is_valid_method(self):
        """Test is_valid convenience method."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        schema = {"type": "string"}

        assert validator.is_valid("test", schema) is True
        assert validator.is_valid(123, schema) is False

    def test_get_errors_method(self):
        """Test get_errors convenience method."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        schema = {"type": "object", "required": ["name"]}
        data = {}

        errors = validator.get_errors(data, schema)

        assert len(errors) > 0


class TestBasicValidation:
    """Tests for basic validation without external libraries."""

    def test_basic_validation_type_object(self):
        """Test basic validation for object type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation({"key": "value"}, {"type": "object"})

        assert result.is_valid is True

    def test_basic_validation_type_object_invalid(self):
        """Test basic validation for object type with invalid data."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation("not an object", {"type": "object"})

        assert result.is_valid is False

    def test_basic_validation_type_array(self):
        """Test basic validation for array type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation([1, 2, 3], {"type": "array"})

        assert result.is_valid is True

    def test_basic_validation_type_array_invalid(self):
        """Test basic validation for array type with invalid data."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation("not an array", {"type": "array"})

        assert result.is_valid is False

    def test_basic_validation_type_string(self):
        """Test basic validation for string type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation("test", {"type": "string"})

        assert result.is_valid is True

    def test_basic_validation_type_string_invalid(self):
        """Test basic validation for string type with invalid data."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation(123, {"type": "string"})

        assert result.is_valid is False

    def test_basic_validation_type_integer(self):
        """Test basic validation for integer type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation(42, {"type": "integer"})

        assert result.is_valid is True

    def test_basic_validation_type_integer_invalid(self):
        """Test basic validation for integer type with invalid data."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation("42", {"type": "integer"})

        assert result.is_valid is False

    def test_basic_validation_type_number_int(self):
        """Test basic validation for number type with integer."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation(42, {"type": "number"})

        assert result.is_valid is True

    def test_basic_validation_type_number_float(self):
        """Test basic validation for number type with float."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation(3.14, {"type": "number"})

        assert result.is_valid is True

    def test_basic_validation_type_boolean(self):
        """Test basic validation for boolean type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result_true = validator._basic_validation(True, {"type": "boolean"})
        result_false = validator._basic_validation(False, {"type": "boolean"})

        assert result_true.is_valid is True
        assert result_false.is_valid is True

    def test_basic_validation_required_fields(self):
        """Test basic validation for required fields."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        schema = {
            "type": "object",
            "required": ["name", "email"]
        }
        data = {"name": "John"}

        result = validator._basic_validation(data, schema)

        assert result.is_valid is False
        assert any("email" in str(e) for e in result.errors)


class TestCustomValidation:
    """Tests for custom validator support."""

    def test_custom_validator_bool_result_true(self):
        """Test custom validator returning True."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="custom")

        def custom_validator(data):
            return data > 0

        result = validator.validate(5, custom_validator)
        assert result.is_valid is True

    def test_custom_validator_bool_result_false(self):
        """Test custom validator returning False."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="custom")

        def custom_validator(data):
            return data > 0

        result = validator.validate(-5, custom_validator)
        assert result.is_valid is False

    def test_custom_validator_validation_result(self):
        """Test custom validator returning ValidationResult."""
        from codomyrmex.validation.validator import Validator, ValidationResult

        validator = Validator(validator_type="custom")

        def custom_validator(data):
            return ValidationResult(is_valid=data is not None)

        result = validator.validate("data", custom_validator)
        assert result.is_valid is True

    def test_custom_validator_exception(self):
        """Test custom validator that raises exception."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="custom")

        def custom_validator(data):
            raise ValueError("Custom validation error")

        result = validator.validate("data", custom_validator)
        assert result.is_valid is False


class TestPydanticValidation:
    """Tests for Pydantic model validation."""

    def test_pydantic_validation_valid(self):
        """Test Pydantic validation with valid data."""
        from codomyrmex.validation.validator import Validator

        class UserModel(BaseModel):
            name: str
            age: int

        validator = Validator(validator_type="pydantic")
        data = {"name": "John", "age": 30}

        result = validator.validate(data, UserModel)

        assert result.is_valid is True

    def test_pydantic_validation_invalid(self):
        """Test Pydantic validation with invalid data."""
        from codomyrmex.validation.validator import Validator

        class UserModel(BaseModel):
            name: str
            age: int

        validator = Validator(validator_type="pydantic")
        data = {"name": "John", "age": "not_a_number"}

        result = validator.validate(data, UserModel)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_pydantic_validation_missing_field(self):
        """Test Pydantic validation with missing required field."""
        from codomyrmex.validation.validator import Validator

        class UserModel(BaseModel):
            name: str
            email: str

        validator = Validator(validator_type="pydantic")
        data = {"name": "John"}

        result = validator.validate(data, UserModel)

        assert result.is_valid is False


class TestUnknownValidatorType:
    """Tests for unknown validator type handling."""

    def test_unknown_validator_type(self):
        """Test validator with unknown type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="unknown")
        result = validator.validate({}, {})

        assert result.is_valid is False


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_validate_function(self):
        """Test validate convenience function."""
        from codomyrmex.validation import validate

        schema = {"type": "string"}
        result = validate("test", schema)

        assert result.is_valid is True

    def test_is_valid_function_true(self):
        """Test is_valid convenience function returns True."""
        from codomyrmex.validation import is_valid

        schema = {"type": "integer"}

        assert is_valid(42, schema) is True

    def test_is_valid_function_false(self):
        """Test is_valid convenience function returns False."""
        from codomyrmex.validation import is_valid

        schema = {"type": "integer"}

        assert is_valid("not_int", schema) is False

    def test_get_errors_function(self):
        """Test get_errors convenience function."""
        from codomyrmex.validation import get_errors

        schema = {"type": "object", "required": ["id"]}
        errors = get_errors({}, schema)

        assert len(errors) > 0
