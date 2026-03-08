"""Comprehensive tests for ConfigValidator — zero-mock, all real validation.

Covers: ValidationSeverity, ValidationIssue, ValidationResult, ConfigSchema,
ConfigValidator with schema validation, required fields, type checking,
constraint validation, and custom validators.
"""

import pytest

from codomyrmex.config_management.validation.config_validator import (
    ConfigSchema,
    ConfigValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)


# ---------------------------------------------------------------------------
# ValidationSeverity
# ---------------------------------------------------------------------------


class TestValidationSeverity:
    def test_enum_values(self):
        assert ValidationSeverity.ERROR.value == "error"
        assert ValidationSeverity.WARNING.value == "warning"
        assert ValidationSeverity.INFO.value == "info"


# ---------------------------------------------------------------------------
# ValidationIssue
# ---------------------------------------------------------------------------


class TestValidationIssue:
    def test_create_simple_issue(self):
        issue = ValidationIssue(
            field_path="database.host",
            message="Missing required field",
            severity=ValidationSeverity.ERROR,
        )
        assert issue.field_path == "database.host"
        assert issue.severity == ValidationSeverity.ERROR

    def test_create_issue_with_suggestion(self):
        issue = ValidationIssue(
            field_path="port",
            message="Invalid port",
            severity=ValidationSeverity.WARNING,
            suggestion="Use a port between 1024 and 65535",
            actual_value=99999,
            expected_value="1024-65535",
        )
        assert issue.suggestion is not None
        assert issue.actual_value == 99999

    def test_to_dict(self):
        issue = ValidationIssue(
            field_path="key",
            message="bad",
            severity=ValidationSeverity.ERROR,
        )
        d = issue.to_dict()
        assert isinstance(d, dict)
        assert "field_path" in d
        assert d["field_path"] == "key"
        assert "severity" in d


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_valid_result(self):
        result = ValidationResult(is_valid=True)
        assert result.is_valid
        assert len(result.issues) == 0
        assert len(result.errors) == 0

    def test_add_error_issue(self):
        result = ValidationResult(is_valid=True)
        issue = ValidationIssue(
            field_path="x", message="missing", severity=ValidationSeverity.ERROR
        )
        result.add_issue(issue)
        assert len(result.errors) == 1
        assert not result.is_valid  # Adding an error should invalidate

    def test_add_warning_issue(self):
        result = ValidationResult(is_valid=True)
        issue = ValidationIssue(
            field_path="x", message="watch out", severity=ValidationSeverity.WARNING
        )
        result.add_issue(issue)
        assert len(result.warnings) == 1
        # Warnings should not invalidate by default
        assert result.is_valid

    def test_to_dict(self):
        result = ValidationResult(is_valid=True)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "is_valid" in d


# ---------------------------------------------------------------------------
# ConfigSchema
# ---------------------------------------------------------------------------


class TestConfigSchema:
    def test_create_basic_schema(self):
        schema = ConfigSchema(type="string", required=True, description="API key")
        assert schema.type == "string"
        assert schema.required is True

    def test_schema_with_constraints(self):
        schema = ConfigSchema(
            type="integer",
            constraints={"min": 1, "max": 65535},
        )
        assert schema.constraints["min"] == 1
        assert schema.constraints["max"] == 65535

    def test_nested_schema(self):
        nested = {
            "host": ConfigSchema(type="string", required=True),
            "port": ConfigSchema(type="integer", default=5432),
        }
        schema = ConfigSchema(type="object", nested_schema=nested)
        assert schema.nested_schema is not None
        assert "host" in schema.nested_schema

    def test_to_dict(self):
        schema = ConfigSchema(type="string", required=True)
        d = schema.to_dict()
        assert isinstance(d, dict)
        assert d["type"] == "string"


# ---------------------------------------------------------------------------
# ConfigValidator — Schema Validation
# ---------------------------------------------------------------------------


class TestConfigValidatorSchema:
    def test_validate_valid_config(self):
        schema = {
            "name": ConfigSchema(type="str", required=True),
            "port": ConfigSchema(type="int", required=True),
        }
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"name": "myapp", "port": 8080})
        assert result.is_valid

    def test_validate_missing_required_field(self):
        schema = {
            "name": ConfigSchema(type="str", required=True),
        }
        validator = ConfigValidator(schema=schema)
        result = validator.validate({})
        assert not result.is_valid

    def test_validate_wrong_type(self):
        schema = {
            "port": ConfigSchema(type="int", required=True),
        }
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"port": "not-a-number"})
        assert not result.is_valid

    def test_validate_optional_field_missing_ok(self):
        schema = {
            "name": ConfigSchema(type="str", required=True),
            "debug": ConfigSchema(type="bool", required=False, default=False),
        }
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"name": "myapp"})
        assert result.is_valid


# ---------------------------------------------------------------------------
# ConfigValidator — Required Fields
# ---------------------------------------------------------------------------


class TestConfigValidatorRequired:
    def test_all_required_present(self):
        validator = ConfigValidator()
        missing = validator.validate_required_fields(
            {"a": 1, "b": 2}, required=["a", "b"]
        )
        assert len(missing) == 0

    def test_some_required_missing(self):
        validator = ConfigValidator()
        missing = validator.validate_required_fields(
            {"a": 1}, required=["a", "b", "c"]
        )
        assert "b" in missing
        assert "c" in missing

    def test_empty_config_all_missing(self):
        validator = ConfigValidator()
        missing = validator.validate_required_fields({}, required=["x", "y"])
        assert len(missing) == 2


# ---------------------------------------------------------------------------
# ConfigValidator — Type Validation
# ---------------------------------------------------------------------------


class TestConfigValidatorTypes:
    def test_validate_type_string(self):
        validator = ConfigValidator()
        issues = validator.validate_types(
            {"name": "hello"}, {"name": "str"}
        )
        assert len(issues) == 0

    def test_validate_type_integer(self):
        validator = ConfigValidator()
        issues = validator.validate_types(
            {"port": 8080}, {"port": "int"}
        )
        assert len(issues) == 0

    def test_validate_type_mismatch(self):
        validator = ConfigValidator()
        issues = validator.validate_types(
            {"port": "not_int"}, {"port": "int"}
        )
        assert len(issues) > 0

    def test_validate_type_boolean(self):
        validator = ConfigValidator()
        issues = validator.validate_types(
            {"debug": True}, {"debug": "bool"}
        )
        assert len(issues) == 0


# ---------------------------------------------------------------------------
# ConfigValidator — Value Constraints
# ---------------------------------------------------------------------------


class TestConfigValidatorConstraints:
    def test_validate_min_constraint(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"port": 0}, {"port": {"min": 1}}
        )
        assert len(issues) > 0

    def test_validate_max_constraint(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"port": 70000}, {"port": {"max": 65535}}
        )
        assert len(issues) > 0

    def test_validate_within_range(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"port": 8080}, {"port": {"min": 1, "max": 65535}}
        )
        assert len(issues) == 0


# ---------------------------------------------------------------------------
# ConfigValidator — Custom Validators
# ---------------------------------------------------------------------------


class TestConfigValidatorCustom:
    def test_add_and_use_custom_validator(self):
        validator = ConfigValidator()

        def check_database_url(config):
            issues = []
            if "database_url" in config:
                url = config["database_url"]
                if not url.startswith(("postgres://", "postgresql://")):
                    issues.append(
                        ValidationIssue(
                            field_path="database_url",
                            message="Must start with postgres://",
                            severity=ValidationSeverity.ERROR,
                        )
                    )
            return issues

        validator.add_custom_validator("db_url_check", check_database_url)
        # Custom validators are stored
        assert "db_url_check" in validator.custom_validators


# ---------------------------------------------------------------------------
# ConfigValidator — _check_type
# ---------------------------------------------------------------------------


class TestCheckType:
    def test_check_string_type(self):
        validator = ConfigValidator()
        assert validator._check_type("hello", "str")

    def test_check_integer_type(self):
        validator = ConfigValidator()
        assert validator._check_type(42, "int")

    def test_check_float_type(self):
        validator = ConfigValidator()
        assert validator._check_type(3.14, "float")

    def test_check_boolean_type(self):
        validator = ConfigValidator()
        assert validator._check_type(True, "bool")

    def test_check_list_type(self):
        validator = ConfigValidator()
        assert validator._check_type([1, 2], "list")

    def test_check_dict_type(self):
        validator = ConfigValidator()
        assert validator._check_type({"a": 1}, "dict")

    def test_check_wrong_type_returns_false(self):
        validator = ConfigValidator()
        assert not validator._check_type("str", "int")
