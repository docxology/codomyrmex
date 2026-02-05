"""Tests for the Codomyrmex Validation module.

This module tests the Validator, ValidationResult, ValidationError, and related classes.
Comprehensive tests for validators, schema validation, input sanitization, and edge cases.
"""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from typing import Optional


@pytest.mark.unit
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

    def test_validation_module_exports(self):
        """Verify module exports key components."""
        from codomyrmex import validation
        assert hasattr(validation, "validate")
        assert hasattr(validation, "is_valid")
        assert hasattr(validation, "get_errors")


@pytest.mark.unit
class TestValidationError:
    """Tests for ValidationError class."""

    def test_create_validation_error(self):
        """Test creating a validation error."""
        from codomyrmex.validation.validator import ValidationError

        error = ValidationError("Field is required", field="name", code="required")

        assert "Field is required" in str(error)
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

    def test_validation_error_is_exception(self):
        """Test that ValidationError is an exception."""
        from codomyrmex.validation.validator import ValidationError

        error = ValidationError("Test error")
        assert isinstance(error, Exception)

    def test_validation_error_with_all_params(self):
        """Test validation error with all parameters."""
        from codomyrmex.validation.validator import ValidationError

        error = ValidationError(
            "Complex error",
            field="email",
            code="invalid_format",
            path=["user", "contact", "email"]
        )

        assert "Complex error" in str(error)
        assert error.field == "email"
        assert error.code == "invalid_format"
        assert error.path == ["user", "contact", "email"]


@pytest.mark.unit
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

    def test_validation_warning_default_code(self):
        """Test validation warning default code is None."""
        from codomyrmex.validation.validator import ValidationWarning

        warning = ValidationWarning(field="test", message="Test message")

        assert warning.code is None

    def test_validation_warning_with_path(self):
        """Test validation warning with path."""
        from codomyrmex.validation.validator import ValidationWarning

        warning = ValidationWarning(
            field="config",
            message="Config may be outdated",
            path=["settings", "config"]
        )

        assert warning.path == ["settings", "config"]


@pytest.mark.unit
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

    def test_result_with_multiple_errors(self):
        """Test result with multiple errors."""
        from codomyrmex.validation.validator import ValidationResult, ValidationError

        errors = [
            ValidationError("Missing name", field="name"),
            ValidationError("Invalid email", field="email"),
            ValidationError("Age required", field="age"),
        ]
        result = ValidationResult(is_valid=False, errors=errors)

        assert len(result.errors) == 3

    def test_result_mixed_errors_and_warnings(self):
        """Test result with both errors and warnings."""
        from codomyrmex.validation.validator import ValidationResult, ValidationError, ValidationWarning

        errors = [ValidationError("Missing field", field="name")]
        warnings = [ValidationWarning(field="age", message="Consider review")]
        result = ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.is_valid is False


@pytest.mark.unit
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

    def test_validate_nested_object(self):
        """Test JSON schema validation with nested objects."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            "required": ["user"]
        }
        data = {"user": {"name": "John", "email": "john@example.com"}}

        result = validator.validate(data, schema)

        assert result.is_valid is True

    def test_validate_array_schema(self):
        """Test JSON schema validation with array."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")
        schema = {
            "type": "array",
            "items": {"type": "integer"}
        }
        data = [1, 2, 3, 4, 5]

        result = validator.validate(data, schema)

        assert result.is_valid is True

    def test_validate_array_invalid_items(self):
        """Test JSON schema validation with invalid array items."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="json_schema")
        schema = {
            "type": "array",
            "items": {"type": "integer"}
        }
        data = [1, "two", 3]

        result = validator.validate(data, schema)

        assert result.is_valid is False


@pytest.mark.unit
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

    def test_basic_validation_all_required_fields_present(self):
        """Test basic validation passes when all required fields present."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        schema = {
            "type": "object",
            "required": ["name", "email"]
        }
        data = {"name": "John", "email": "john@example.com"}

        result = validator._basic_validation(data, schema)

        assert result.is_valid is True

    def test_basic_validation_empty_schema(self):
        """Test basic validation with empty schema."""
        from codomyrmex.validation.validator import Validator

        validator = Validator()
        result = validator._basic_validation({"any": "data"}, {})

        assert result.is_valid is True


@pytest.mark.unit
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

    def test_custom_validator_complex_logic(self):
        """Test custom validator with complex validation logic."""
        from codomyrmex.validation.validator import Validator, ValidationResult, ValidationError

        validator = Validator(validator_type="custom")

        def custom_validator(data):
            errors = []
            if not isinstance(data, dict):
                errors.append(ValidationError("Must be a dictionary"))
            elif "username" not in data:
                errors.append(ValidationError("Missing username", field="username"))
            elif len(data.get("username", "")) < 3:
                errors.append(ValidationError("Username too short", field="username"))
            return ValidationResult(is_valid=len(errors) == 0, errors=errors)

        result = validator.validate({"username": "ab"}, custom_validator)
        assert result.is_valid is False

    def test_custom_validator_returns_none(self):
        """Test custom validator returning None."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="custom")

        def custom_validator(data):
            return None

        result = validator.validate("data", custom_validator)
        assert result.is_valid is True


@pytest.mark.unit
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

    def test_pydantic_validation_optional_field(self):
        """Test Pydantic validation with optional field."""
        from codomyrmex.validation.validator import Validator

        class UserModel(BaseModel):
            name: str
            nickname: Optional[str] = None

        validator = Validator(validator_type="pydantic")
        data = {"name": "John"}

        result = validator.validate(data, UserModel)

        assert result.is_valid is True

    def test_pydantic_validation_nested_model(self):
        """Test Pydantic validation with nested model."""
        from codomyrmex.validation.validator import Validator

        class AddressModel(BaseModel):
            street: str
            city: str

        class UserModel(BaseModel):
            name: str
            address: AddressModel

        validator = Validator(validator_type="pydantic")
        data = {
            "name": "John",
            "address": {"street": "123 Main St", "city": "Boston"}
        }

        result = validator.validate(data, UserModel)

        assert result.is_valid is True

    def test_pydantic_validation_invalid_nested(self):
        """Test Pydantic validation with invalid nested data."""
        from codomyrmex.validation.validator import Validator

        class AddressModel(BaseModel):
            street: str
            city: str

        class UserModel(BaseModel):
            name: str
            address: AddressModel

        validator = Validator(validator_type="pydantic")
        data = {
            "name": "John",
            "address": {"street": "123 Main St"}  # Missing city
        }

        result = validator.validate(data, UserModel)

        assert result.is_valid is False


@pytest.mark.unit
class TestUnknownValidatorType:
    """Tests for unknown validator type handling."""

    def test_unknown_validator_type(self):
        """Test validator with unknown type."""
        from codomyrmex.validation.validator import Validator

        validator = Validator(validator_type="unknown")
        result = validator.validate({}, {})

        assert result.is_valid is False


@pytest.mark.unit
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

    def test_validate_with_pydantic_type(self):
        """Test validate convenience function with pydantic type."""
        from codomyrmex.validation import validate

        class TestModel(BaseModel):
            value: int

        result = validate({"value": 42}, TestModel, validator_type="pydantic")

        assert result.is_valid is True


@pytest.mark.unit
class TestContextualValidator:
    """Tests for ContextualValidator class."""

    def test_contextual_validator_create(self):
        """Test creating a contextual validator."""
        from codomyrmex.validation.contextual import ContextualValidator

        validator = ContextualValidator()
        assert validator is not None

    def test_contextual_validator_add_rule(self):
        """Test adding a rule to contextual validator."""
        from codomyrmex.validation.contextual import ContextualValidator, ValidationIssue

        validator = ContextualValidator()

        def rule(data):
            if data.get("age", 0) < 0:
                return ValidationIssue(field="age", message="Age cannot be negative")
            return None

        validator.add_rule(rule)
        assert len(validator._rules) == 1

    def test_contextual_validator_validate_no_issues(self):
        """Test contextual validation with no issues."""
        from codomyrmex.validation.contextual import ContextualValidator

        validator = ContextualValidator()

        def rule(data):
            return None

        validator.add_rule(rule)
        issues = validator.validate({"name": "test"})

        assert len(issues) == 0

    def test_contextual_validator_validate_with_issues(self):
        """Test contextual validation with issues."""
        from codomyrmex.validation.contextual import ContextualValidator, ValidationIssue

        validator = ContextualValidator()

        def rule(data):
            if "name" not in data:
                return ValidationIssue(field="name", message="Name is required")
            return None

        validator.add_rule(rule)
        issues = validator.validate({})

        assert len(issues) == 1
        assert issues[0].field == "name"

    def test_contextual_validator_multiple_rules(self):
        """Test contextual validation with multiple rules."""
        from codomyrmex.validation.contextual import ContextualValidator, ValidationIssue

        validator = ContextualValidator()

        def rule1(data):
            if "name" not in data:
                return ValidationIssue(field="name", message="Name required")
            return None

        def rule2(data):
            if "email" not in data:
                return ValidationIssue(field="email", message="Email required")
            return None

        validator.add_rule(rule1)
        validator.add_rule(rule2)
        issues = validator.validate({})

        assert len(issues) == 2

    def test_contextual_validator_cross_field_validation(self):
        """Test contextual validation with cross-field rules."""
        from codomyrmex.validation.contextual import ContextualValidator, ValidationIssue

        validator = ContextualValidator()

        def password_match_rule(data):
            if data.get("password") != data.get("confirm_password"):
                return ValidationIssue(
                    field="confirm_password",
                    message="Passwords do not match"
                )
            return None

        validator.add_rule(password_match_rule)
        issues = validator.validate({
            "password": "secret",
            "confirm_password": "different"
        })

        assert len(issues) == 1


@pytest.mark.unit
class TestValidationIssue:
    """Tests for ValidationIssue class."""

    def test_validation_issue_create(self):
        """Test creating a validation issue."""
        from codomyrmex.validation.contextual import ValidationIssue

        issue = ValidationIssue(field="test", message="Test message")

        assert issue.field == "test"
        assert issue.message == "Test message"

    def test_validation_issue_default_severity(self):
        """Test validation issue default severity."""
        from codomyrmex.validation.contextual import ValidationIssue

        issue = ValidationIssue(field="test", message="Test message")

        assert issue.severity == "error"

    def test_validation_issue_custom_severity(self):
        """Test validation issue with custom severity."""
        from codomyrmex.validation.contextual import ValidationIssue

        issue = ValidationIssue(
            field="test",
            message="Test warning",
            severity="warning"
        )

        assert issue.severity == "warning"


@pytest.mark.unit
class TestTypeSafeParser:
    """Tests for TypeSafeParser class."""

    def test_parse_as_valid(self):
        """Test parse_as with valid data."""
        from codomyrmex.validation.parser import TypeSafeParser

        class UserModel(BaseModel):
            name: str
            age: int

        result = TypeSafeParser.parse_as(UserModel, {"name": "John", "age": 30})

        assert result is not None
        assert result.name == "John"
        assert result.age == 30

    def test_parse_as_invalid(self):
        """Test parse_as with invalid data returns None."""
        from codomyrmex.validation.parser import TypeSafeParser

        class UserModel(BaseModel):
            name: str
            age: int

        result = TypeSafeParser.parse_as(UserModel, {"name": "John"})

        assert result is None

    def test_parse_dict_valid(self):
        """Test parse_dict with valid data."""
        from codomyrmex.validation.parser import TypeSafeParser

        class UserModel(BaseModel):
            name: str

        result = TypeSafeParser.parse_dict(UserModel, {"name": "John"})

        assert result.name == "John"

    def test_parse_dict_invalid_raises(self):
        """Test parse_dict with invalid data raises error."""
        from codomyrmex.validation.parser import TypeSafeParser
        from pydantic import ValidationError as PydanticValidationError

        class UserModel(BaseModel):
            name: str
            age: int

        with pytest.raises(PydanticValidationError):
            TypeSafeParser.parse_dict(UserModel, {"name": "John"})


@pytest.mark.unit
class TestValidationManager:
    """Tests for ValidationManager class."""

    def test_validation_manager_create(self):
        """Test creating a validation manager."""
        from codomyrmex.validation.validation_manager import ValidationManager

        manager = ValidationManager()
        assert manager is not None

    def test_validation_manager_register_validator(self):
        """Test registering a custom validator."""
        from codomyrmex.validation.validation_manager import ValidationManager

        manager = ValidationManager()

        def custom_validator(data, schema):
            return True

        manager.register_validator("custom_test", custom_validator)

        assert manager.get_validator("custom_test") is not None

    def test_validation_manager_get_validator_not_found(self):
        """Test getting a non-existent validator."""
        from codomyrmex.validation.validation_manager import ValidationManager

        manager = ValidationManager()

        assert manager.get_validator("nonexistent") is None

    def test_validation_manager_validate_default(self):
        """Test validation with default validator."""
        from codomyrmex.validation.validation_manager import ValidationManager

        manager = ValidationManager()
        schema = {"type": "string"}

        result = manager.validate("test", schema)

        assert result.is_valid is True

    def test_validation_manager_validate_custom(self):
        """Test validation with custom validator."""
        from codomyrmex.validation.validation_manager import ValidationManager

        manager = ValidationManager()

        def custom_validator(data, schema):
            return len(data) > schema.get("min_length", 0)

        manager.register_validator("length_check", custom_validator)

        result = manager.validate("test", {"min_length": 3}, "length_check")

        assert result.is_valid is True


@pytest.mark.unit
class TestValidationSummary:
    """Tests for ValidationSummary class."""

    def test_validation_summary_create(self):
        """Test creating a validation summary."""
        from codomyrmex.validation.summary import ValidationSummary
        from codomyrmex.validation.contextual import ValidationIssue

        issues = [ValidationIssue(field="test", message="Test error")]
        summary = ValidationSummary(issues)

        assert summary is not None
        assert len(summary.issues) == 1

    def test_validation_summary_is_valid_no_errors(self):
        """Test summary is valid when no errors."""
        from codomyrmex.validation.summary import ValidationSummary
        from codomyrmex.validation.contextual import ValidationIssue

        issues = [ValidationIssue(field="test", message="Warning", severity="warning")]
        summary = ValidationSummary(issues)

        assert summary.is_valid is True

    def test_validation_summary_is_valid_with_errors(self):
        """Test summary is invalid when errors exist."""
        from codomyrmex.validation.summary import ValidationSummary
        from codomyrmex.validation.contextual import ValidationIssue

        issues = [ValidationIssue(field="test", message="Error", severity="error")]
        summary = ValidationSummary(issues)

        assert summary.is_valid is False

    def test_validation_summary_error_count(self):
        """Test error count in summary."""
        from codomyrmex.validation.summary import ValidationSummary
        from codomyrmex.validation.contextual import ValidationIssue

        issues = [
            ValidationIssue(field="a", message="Error 1", severity="error"),
            ValidationIssue(field="b", message="Error 2", severity="error"),
            ValidationIssue(field="c", message="Warning", severity="warning"),
        ]
        summary = ValidationSummary(issues)

        assert summary.error_count == 2

    def test_validation_summary_warning_count(self):
        """Test warning count in summary."""
        from codomyrmex.validation.summary import ValidationSummary
        from codomyrmex.validation.contextual import ValidationIssue

        issues = [
            ValidationIssue(field="a", message="Error", severity="error"),
            ValidationIssue(field="b", message="Warning 1", severity="warning"),
            ValidationIssue(field="c", message="Warning 2", severity="warning"),
        ]
        summary = ValidationSummary(issues)

        assert summary.warning_count == 2

    def test_validation_summary_to_dict(self):
        """Test converting summary to dictionary."""
        from codomyrmex.validation.summary import ValidationSummary
        from codomyrmex.validation.contextual import ValidationIssue

        issues = [ValidationIssue(field="test", message="Error", severity="error")]
        summary = ValidationSummary(issues)

        result = summary.to_dict()

        assert "is_valid" in result
        assert "error_count" in result
        assert "warning_count" in result
        assert "issues" in result
        assert len(result["issues"]) == 1

    def test_validation_summary_empty_issues(self):
        """Test summary with no issues."""
        from codomyrmex.validation.summary import ValidationSummary

        summary = ValidationSummary([])

        assert summary.is_valid is True
        assert summary.error_count == 0
        assert summary.warning_count == 0
