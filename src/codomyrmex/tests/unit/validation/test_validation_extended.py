"""Extended validation tests: custom, pydantic, contextual, TypeSafeParser, ValidationManager."""


import pytest
from pydantic import BaseModel


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
        from codomyrmex.validation.validator import ValidationResult, Validator

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
        from codomyrmex.validation.validator import (
            ValidationError,
            ValidationResult,
            Validator,
        )

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
            nickname: str | None = None

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
class TestContextualValidator:
    """Tests for ContextualValidator class."""

    def test_contextual_validator_create(self):
        """Test creating a contextual validator."""
        from codomyrmex.validation.contextual import ContextualValidator

        validator = ContextualValidator()
        assert validator is not None

    def test_contextual_validator_add_rule(self):
        """Test adding a rule to contextual validator."""
        from codomyrmex.validation.contextual import (
            ContextualValidator,
            ValidationIssue,
        )

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
        from codomyrmex.validation.contextual import (
            ContextualValidator,
            ValidationIssue,
        )

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
        from codomyrmex.validation.contextual import (
            ContextualValidator,
            ValidationIssue,
        )

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
        from codomyrmex.validation.contextual import (
            ContextualValidator,
            ValidationIssue,
        )

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
        from pydantic import ValidationError as PydanticValidationError

        from codomyrmex.validation.parser import TypeSafeParser

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
        from codomyrmex.validation.contextual import ValidationIssue
        from codomyrmex.validation.summary import ValidationSummary

        issues = [ValidationIssue(field="test", message="Test error")]
        summary = ValidationSummary(issues)

        assert summary is not None
        assert len(summary.issues) == 1

    def test_validation_summary_is_valid_no_errors(self):
        """Test summary is valid when no errors."""
        from codomyrmex.validation.contextual import ValidationIssue
        from codomyrmex.validation.summary import ValidationSummary

        issues = [ValidationIssue(field="test", message="Warning", severity="warning")]
        summary = ValidationSummary(issues)

        assert summary.is_valid is True

    def test_validation_summary_is_valid_with_errors(self):
        """Test summary is invalid when errors exist."""
        from codomyrmex.validation.contextual import ValidationIssue
        from codomyrmex.validation.summary import ValidationSummary

        issues = [ValidationIssue(field="test", message="Error", severity="error")]
        summary = ValidationSummary(issues)

        assert summary.is_valid is False

    def test_validation_summary_error_count(self):
        """Test error count in summary."""
        from codomyrmex.validation.contextual import ValidationIssue
        from codomyrmex.validation.summary import ValidationSummary

        issues = [
            ValidationIssue(field="a", message="Error 1", severity="error"),
            ValidationIssue(field="b", message="Error 2", severity="error"),
            ValidationIssue(field="c", message="Warning", severity="warning"),
        ]
        summary = ValidationSummary(issues)

        assert summary.error_count == 2

    def test_validation_summary_warning_count(self):
        """Test warning count in summary."""
        from codomyrmex.validation.contextual import ValidationIssue
        from codomyrmex.validation.summary import ValidationSummary

        issues = [
            ValidationIssue(field="a", message="Error", severity="error"),
            ValidationIssue(field="b", message="Warning 1", severity="warning"),
            ValidationIssue(field="c", message="Warning 2", severity="warning"),
        ]
        summary = ValidationSummary(issues)

        assert summary.warning_count == 2

    def test_validation_summary_to_dict(self):
        """Test converting summary to dictionary."""
        from codomyrmex.validation.contextual import ValidationIssue
        from codomyrmex.validation.summary import ValidationSummary

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


# From test_coverage_boost_r7.py
class TestExamplesValidator:
    def test_validation_severity(self):
        from codomyrmex.validation.examples_validator import ValidationSeverity
        assert len(list(ValidationSeverity)) > 0

    def test_validation_type(self):
        from codomyrmex.validation.examples_validator import ValidationType
        assert len(list(ValidationType)) > 0

    def test_validation_issue(self):
        from codomyrmex.validation.examples_validator import (
            ValidationIssue,
            ValidationSeverity,
            ValidationType,
        )
        issue = ValidationIssue(module="test", validation_type=list(ValidationType)[0], severity=list(ValidationSeverity)[0], message="test issue", file_path="test.py")
        assert issue.message == "test issue"

    def test_examples_validator(self):
        from pathlib import Path

        from codomyrmex.validation.examples_validator import ExamplesValidator
        v = ExamplesValidator(root_dir=Path("."), output_dir=Path("/tmp/ev_test"))
        assert v is not None


# Phase 2b — validation/examples_validator
class TestValidationDataclasses:
    """Tests for validation dataclasses and enums."""

    def test_validation_type_enum(self):
        from codomyrmex.validation.examples_validator import ValidationType
        assert len(list(ValidationType)) > 0

    def test_validation_severity_enum(self):
        from codomyrmex.validation.examples_validator import ValidationSeverity
        assert len(list(ValidationSeverity)) > 0

    def test_validation_issue(self):
        from codomyrmex.validation.examples_validator import (
            ValidationIssue,
            ValidationSeverity,
            ValidationType,
        )
        issue = ValidationIssue(
            module="test",
            validation_type=list(ValidationType)[0],
            severity=list(ValidationSeverity)[0],
            message="Test issue",
            file_path="test.py",
            line_number=42,
        )
        assert issue.module == "test"
        assert issue.line_number == 42

    def test_module_validation_result(self):
        from codomyrmex.validation.examples_validator import ModuleValidationResult
        result = ModuleValidationResult(module="utils", success=True, duration=1.5)
        assert result.success is True
        assert result.duration == 1.5

    def test_module_validation_result_with_issues(self):
        from codomyrmex.validation.examples_validator import (
            ModuleValidationResult,
            ValidationIssue,
            ValidationSeverity,
            ValidationType,
        )
        issue = ValidationIssue(
            module="utils", validation_type=list(ValidationType)[0],
            severity=list(ValidationSeverity)[0], message="warning",
        )
        result = ModuleValidationResult(module="utils", success=False, issues=[issue])
        assert len(result.issues) == 1
