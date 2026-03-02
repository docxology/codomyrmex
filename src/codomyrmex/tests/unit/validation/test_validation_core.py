"""
Unit tests for validation.validator and validation.exceptions — Zero-Mock compliant.

Covers:
  - validation/validator.py  (Validator, ValidationResult, ValidationError,
                               ValidationWarning with json_schema/pydantic/custom strategies)
  - validation/exceptions.py  (ValidationError, SchemaError, ConstraintViolationError,
                                TypeValidationError, RequiredFieldError, RangeValidationError,
                                FormatValidationError, LengthValidationError, CustomValidationError)
"""

import pytest
from pydantic import BaseModel

from codomyrmex.validation.exceptions import (
    ConstraintViolationError,
    CustomValidationError,
    FormatValidationError,
    LengthValidationError,
    RangeValidationError,
    RequiredFieldError,
    SchemaError,
    TypeValidationError,
)
from codomyrmex.validation.exceptions import (
    ValidationError as ExcValidationError,
)
from codomyrmex.validation.validator import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
    Validator,
)

# ── ValidationResult ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_valid_result_bool_true(self):
        result = ValidationResult(is_valid=True)
        assert bool(result) is True

    def test_invalid_result_bool_false(self):
        result = ValidationResult(is_valid=False)
        assert bool(result) is False

    def test_defaults_empty_errors(self):
        result = ValidationResult(is_valid=True)
        assert result.errors == []
        assert result.warnings == []

    def test_with_errors(self):
        err = ValidationError("bad field", field="name")
        result = ValidationResult(is_valid=False, errors=[err])
        assert len(result.errors) == 1
        assert result.errors[0].field == "name"

    def test_with_warnings(self):
        warn = ValidationWarning(field="age", message="deprecated")
        result = ValidationResult(is_valid=True, warnings=[warn])
        assert len(result.warnings) == 1
        assert result.warnings[0].field == "age"


# ── ValidationWarning ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestValidationWarning:
    """Tests for the ValidationWarning dataclass."""

    def test_instantiation(self):
        w = ValidationWarning(field="x", message="deprecated field")
        assert w.field == "x"
        assert w.message == "deprecated field"
        assert w.code is None
        assert w.path == []

    def test_with_code(self):
        w = ValidationWarning(field="y", message="warn", code="W001")
        assert w.code == "W001"

    def test_with_path(self):
        w = ValidationWarning(field="z", message="w", path=["a", "b"])
        assert w.path == ["a", "b"]


# ── Validator — json_schema ────────────────────────────────────────────────


@pytest.mark.unit
class TestValidatorJsonSchema:
    """Tests for Validator with json_schema strategy."""

    def test_valid_object(self):
        v = Validator("json_schema")
        schema = {"type": "object", "required": ["name"]}
        result = v.validate({"name": "Alice"}, schema)
        assert result.is_valid is True

    def test_missing_required_field(self):
        v = Validator("json_schema")
        schema = {"type": "object", "required": ["name"]}
        result = v.validate({}, schema)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_wrong_type(self):
        v = Validator("json_schema")
        schema = {"type": "integer"}
        result = v.validate("not_int", schema)
        assert result.is_valid is False

    def test_is_valid_convenience(self):
        v = Validator("json_schema")
        assert v.is_valid(42, {"type": "integer"}) is True
        assert v.is_valid("hello", {"type": "integer"}) is False

    def test_get_errors_returns_list(self):
        v = Validator("json_schema")
        errors = v.get_errors({}, {"type": "object", "required": ["x"]})
        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_get_errors_empty_when_valid(self):
        v = Validator("json_schema")
        errors = v.get_errors({"x": 1}, {"type": "object"})
        assert errors == []

    def test_valid_array(self):
        v = Validator("json_schema")
        result = v.validate([1, 2, 3], {"type": "array"})
        assert result.is_valid is True

    def test_number_validation(self):
        v = Validator("json_schema")
        result = v.validate(3.14, {"type": "number"})
        assert result.is_valid is True

    def test_minimum_constraint(self):
        v = Validator("json_schema")
        result = v.validate(-1, {"type": "integer", "minimum": 0})
        assert result.is_valid is False


# ── Validator — pydantic ───────────────────────────────────────────────────


@pytest.mark.unit
class TestValidatorPydantic:
    """Tests for Validator with pydantic strategy."""

    def test_valid_model(self):
        class User(BaseModel):
            name: str
            age: int

        v = Validator("pydantic")
        result = v.validate({"name": "Alice", "age": 30}, User)
        assert result.is_valid is True

    def test_invalid_model_wrong_type(self):
        class Item(BaseModel):
            count: int

        v = Validator("pydantic")
        result = v.validate({"count": "not_an_int"}, Item)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_missing_required_field(self):
        class Config(BaseModel):
            host: str
            port: int

        v = Validator("pydantic")
        result = v.validate({"host": "localhost"}, Config)
        assert result.is_valid is False

    def test_error_has_field(self):
        class Config(BaseModel):
            port: int

        v = Validator("pydantic")
        result = v.validate({"port": "bad"}, Config)
        assert len(result.errors) > 0
        assert result.errors[0].field is not None


# ── Validator — custom ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestValidatorCustom:
    """Tests for Validator with custom strategy."""

    def test_custom_returns_bool_true(self):
        v = Validator("custom")
        result = v.validate({"x": 5}, lambda d: d.get("x", 0) > 0)
        assert result.is_valid is True

    def test_custom_returns_bool_false(self):
        v = Validator("custom")
        result = v.validate({"x": -1}, lambda d: d.get("x", 0) > 0)
        assert result.is_valid is False

    def test_custom_returns_validation_result(self):
        v = Validator("custom")

        def my_validator(data):
            return ValidationResult(is_valid=True)

        result = v.validate({}, my_validator)
        assert result.is_valid is True

    def test_custom_exception_caught(self):
        v = Validator("custom")
        result = v.validate({}, lambda d: 1 / 0)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_custom_non_bool_treated_as_valid(self):
        v = Validator("custom")
        # Validator returning a string (not bool/ValidationResult) → treated as valid
        result = v.validate({}, lambda d: "ok")
        assert result.is_valid is True


# ── Validator — unknown type ───────────────────────────────────────────────


@pytest.mark.unit
class TestValidatorUnknownType:
    """Tests for Validator with unknown strategy."""

    def test_unknown_validator_returns_invalid(self):
        v = Validator("unknown_type")
        result = v.validate({}, {})
        assert result.is_valid is False

    def test_default_validator_type_is_json_schema(self):
        v = Validator()
        assert v.validator_type == "json_schema"

    def test_default_validates_json_schema(self):
        v = Validator()
        result = v.validate("hello", {"type": "string"})
        assert result.is_valid is True


# ── exceptions.py — ValidationError ───────────────────────────────────────


@pytest.mark.unit
class TestExcValidationError:
    """Tests for ValidationError in exceptions.py."""

    def test_basic_instantiation(self):
        err = ExcValidationError("Invalid value")
        assert "Invalid value" in str(err)

    def test_with_field(self):
        err = ExcValidationError("Missing field", field="email")
        assert err.context["field"] == "email"

    def test_with_value(self):
        err = ExcValidationError("Bad value", value="hello")
        assert err.context["value"] == "hello"

    def test_value_truncated_when_long(self):
        long_val = "x" * 200
        err = ExcValidationError("Too long", value=long_val)
        assert len(err.context["value"]) <= 103  # 100 + "..."

    def test_with_rule(self):
        err = ExcValidationError("Rule violated", rule="min_length")
        assert err.context["rule"] == "min_length"

    def test_no_field_no_context_key(self):
        err = ExcValidationError("Error")
        assert "field" not in err.context

    def test_is_exception(self):
        err = ExcValidationError("Test")
        assert isinstance(err, Exception)


# ── exceptions.py — SchemaError ───────────────────────────────────────────


@pytest.mark.unit
class TestSchemaError:
    """Tests for SchemaError in exceptions.py."""

    def test_basic(self):
        err = SchemaError("Schema not found")
        assert "Schema not found" in str(err)

    def test_with_schema_name(self):
        err = SchemaError("Bad schema", schema_name="user_schema")
        assert err.context["schema_name"] == "user_schema"

    def test_with_all_fields(self):
        err = SchemaError(
            "Load error",
            schema_name="cfg",
            schema_path="/path/to/schema.json",
            schema_type="json_schema",
        )
        assert err.context["schema_path"] == "/path/to/schema.json"
        assert err.context["schema_type"] == "json_schema"


# ── exceptions.py — ConstraintViolationError ──────────────────────────────


@pytest.mark.unit
class TestConstraintViolationError:
    """Tests for ConstraintViolationError."""

    def test_basic(self):
        err = ConstraintViolationError("Unique constraint violated")
        assert isinstance(err, ExcValidationError)

    def test_with_context(self):
        err = ConstraintViolationError(
            "Duplicate key",
            constraint_name="unique_email",
            constraint_type="unique",
            expected="unique",
            actual="duplicate",
        )
        assert err.context["constraint_name"] == "unique_email"
        assert err.context["constraint_type"] == "unique"


# ── exceptions.py — TypeValidationError ───────────────────────────────────


@pytest.mark.unit
class TestTypeValidationError:
    """Tests for TypeValidationError."""

    def test_basic(self):
        err = TypeValidationError("Type mismatch")
        assert isinstance(err, ExcValidationError)

    def test_with_types(self):
        err = TypeValidationError(
            "Wrong type",
            expected_type="int",
            actual_type="str",
            field="age",
        )
        assert err.context["expected_type"] == "int"
        assert err.context["actual_type"] == "str"
        assert err.context["field"] == "age"


# ── exceptions.py — RequiredFieldError ────────────────────────────────────


@pytest.mark.unit
class TestRequiredFieldError:
    """Tests for RequiredFieldError."""

    def test_basic(self):
        err = RequiredFieldError("Missing required field", field="name")
        assert err.context["field"] == "name"

    def test_with_parent(self):
        err = RequiredFieldError("Missing", field="host", parent="config.database")
        assert err.context["parent"] == "config.database"


# ── exceptions.py — RangeValidationError ──────────────────────────────────


@pytest.mark.unit
class TestRangeValidationError:
    """Tests for RangeValidationError."""

    def test_with_range(self):
        err = RangeValidationError(
            "Out of range",
            field="age",
            value=-5,
            min_value=0,
            max_value=150,
        )
        assert err.context["min_value"] == 0
        assert err.context["max_value"] == 150

    def test_without_optional_fields(self):
        err = RangeValidationError("Out of range")
        assert "min_value" not in err.context


# ── exceptions.py — FormatValidationError ─────────────────────────────────


@pytest.mark.unit
class TestFormatValidationError:
    """Tests for FormatValidationError."""

    def test_basic(self):
        err = FormatValidationError("Invalid format", field="email", expected_format="email")
        assert err.context["expected_format"] == "email"

    def test_with_pattern(self):
        err = FormatValidationError("Invalid", pattern=r"^\d{5}$")
        assert err.context["pattern"] == r"^\d{5}$"


# ── exceptions.py — LengthValidationError ─────────────────────────────────


@pytest.mark.unit
class TestLengthValidationError:
    """Tests for LengthValidationError."""

    def test_with_lengths(self):
        err = LengthValidationError(
            "Too long",
            field="username",
            actual_length=200,
            min_length=3,
            max_length=50,
        )
        assert err.context["actual_length"] == 200
        assert err.context["max_length"] == 50

    def test_without_optional_fields(self):
        err = LengthValidationError("Length error")
        assert "actual_length" not in err.context


# ── exceptions.py — CustomValidationError ─────────────────────────────────


@pytest.mark.unit
class TestCustomValidationError:
    """Tests for CustomValidationError."""

    def test_with_validator_name(self):
        err = CustomValidationError("Custom fail", validator_name="my_rule")
        assert err.context["validator_name"] == "my_rule"

    def test_with_details(self):
        err = CustomValidationError("Fail", details={"key": "val"})
        assert err.context["details"] == {"key": "val"}

    def test_without_optional_fields(self):
        err = CustomValidationError("Custom fail")
        assert "validator_name" not in err.context
