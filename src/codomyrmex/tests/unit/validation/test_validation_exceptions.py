"""Zero-mock tests for validation/exceptions.py.

Tests all exception classes: hierarchy, context storage for all optional args,
value truncation at 100 chars, and the to_dict interface from CodomyrmexError.
"""

from __future__ import annotations

import pytest

from codomyrmex.validation.exceptions import (
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


@pytest.mark.unit
class TestValidationError:
    """Tests for the ValidationError base class in this module."""

    def test_is_exception(self):
        err = ValidationError("invalid input")
        assert isinstance(err, Exception)

    def test_message_preserved(self):
        err = ValidationError("something is wrong")
        assert "something is wrong" in str(err)

    def test_stores_field(self):
        err = ValidationError("invalid", field="email")
        assert err.context["field"] == "email"

    def test_stores_value(self):
        err = ValidationError("invalid", value="bad_value")
        assert err.context["value"] == "bad_value"

    def test_stores_rule(self):
        err = ValidationError("invalid", rule="must_be_email")
        assert err.context["rule"] == "must_be_email"

    def test_value_truncated_at_100_chars(self):
        long_value = "x" * 150
        err = ValidationError("invalid", value=long_value)
        stored = err.context["value"]
        assert stored.endswith("...")
        assert len(stored) == 103  # 100 + "..."

    def test_value_short_not_truncated(self):
        short_value = "abc"
        err = ValidationError("invalid", value=short_value)
        assert err.context["value"] == "abc"

    def test_no_optional_args_clean_context(self):
        err = ValidationError("invalid")
        assert "field" not in err.context
        assert "value" not in err.context
        assert "rule" not in err.context

    def test_to_dict_contains_expected_keys(self):
        err = ValidationError("invalid", field="name")
        d = err.to_dict()
        assert "error_type" in d
        assert "message" in d
        assert "context" in d

    def test_value_none_not_stored(self):
        # value=None is falsy for "if value is not None" — None IS the boundary
        err = ValidationError("invalid", value=None)
        # value=None should NOT be stored because the check is "if value is not None"
        # Wait — the code does `if value is not None:` which means None is excluded
        assert "value" not in err.context

    def test_value_zero_is_stored(self):
        # value=0 is not None, so it SHOULD be stored
        err = ValidationError("invalid", value=0)
        assert "value" in err.context
        assert err.context["value"] == "0"


@pytest.mark.unit
class TestSchemaError:
    """Tests for SchemaError context storage."""

    def test_is_exception(self):
        err = SchemaError("schema error")
        assert isinstance(err, Exception)

    def test_stores_schema_name(self):
        err = SchemaError("invalid schema", schema_name="UserSchema")
        assert err.context["schema_name"] == "UserSchema"

    def test_stores_schema_path(self):
        err = SchemaError("invalid schema", schema_path="/schemas/user.json")
        assert err.context["schema_path"] == "/schemas/user.json"

    def test_stores_schema_type(self):
        err = SchemaError("invalid schema", schema_type="json_schema")
        assert err.context["schema_type"] == "json_schema"

    def test_all_optional_args_together(self):
        err = SchemaError(
            "schema load failed",
            schema_name="Config",
            schema_path="/config.schema.json",
            schema_type="pydantic",
        )
        assert err.context["schema_name"] == "Config"
        assert err.context["schema_path"] == "/config.schema.json"
        assert err.context["schema_type"] == "pydantic"

    def test_no_optional_args_clean_context(self):
        err = SchemaError("schema error")
        assert "schema_name" not in err.context
        assert "schema_path" not in err.context
        assert "schema_type" not in err.context


@pytest.mark.unit
class TestConstraintViolationError:
    """Tests for ConstraintViolationError context storage."""

    def test_is_validation_error(self):
        err = ConstraintViolationError("constraint violated")
        assert isinstance(err, ValidationError)

    def test_stores_constraint_name(self):
        err = ConstraintViolationError("violated", constraint_name="unique_email")
        assert err.context["constraint_name"] == "unique_email"

    def test_stores_constraint_type(self):
        err = ConstraintViolationError("violated", constraint_type="unique")
        assert err.context["constraint_type"] == "unique"

    def test_stores_expected(self):
        err = ConstraintViolationError("violated", expected="unique value")
        assert err.context["expected"] == "unique value"

    def test_stores_actual(self):
        err = ConstraintViolationError("violated", actual="duplicate@example.com")
        assert err.context["actual"] == "duplicate@example.com"

    def test_all_fields_together(self):
        err = ConstraintViolationError(
            "constraint failed",
            constraint_name="max_age",
            constraint_type="range",
            expected="<= 120",
            actual="200",
        )
        assert err.context["constraint_name"] == "max_age"
        assert err.context["constraint_type"] == "range"
        assert err.context["expected"] == "<= 120"
        assert err.context["actual"] == "200"


@pytest.mark.unit
class TestTypeValidationError:
    """Tests for TypeValidationError context storage."""

    def test_is_validation_error(self):
        err = TypeValidationError("wrong type")
        assert isinstance(err, ValidationError)

    def test_stores_expected_type(self):
        err = TypeValidationError("wrong type", expected_type="int")
        assert err.context["expected_type"] == "int"

    def test_stores_actual_type(self):
        err = TypeValidationError("wrong type", actual_type="str")
        assert err.context["actual_type"] == "str"

    def test_stores_field_via_parent(self):
        err = TypeValidationError("wrong type", field="age")
        assert err.context["field"] == "age"

    def test_type_mismatch_full_context(self):
        err = TypeValidationError(
            "type error",
            expected_type="int",
            actual_type="str",
            field="count",
        )
        assert err.context["expected_type"] == "int"
        assert err.context["actual_type"] == "str"
        assert err.context["field"] == "count"


@pytest.mark.unit
class TestRequiredFieldError:
    """Tests for RequiredFieldError context storage."""

    def test_is_validation_error(self):
        err = RequiredFieldError("field required")
        assert isinstance(err, ValidationError)

    def test_stores_field(self):
        err = RequiredFieldError("required", field="username")
        assert err.context["field"] == "username"

    def test_stores_parent(self):
        err = RequiredFieldError("required", field="id", parent="user.address")
        assert err.context["parent"] == "user.address"

    def test_no_parent_not_in_context(self):
        err = RequiredFieldError("required", field="name")
        assert "parent" not in err.context


@pytest.mark.unit
class TestRangeValidationError:
    """Tests for RangeValidationError context storage."""

    def test_is_validation_error(self):
        err = RangeValidationError("out of range")
        assert isinstance(err, ValidationError)

    def test_stores_min_value(self):
        err = RangeValidationError("too low", min_value=0)
        assert err.context["min_value"] == 0

    def test_stores_max_value(self):
        err = RangeValidationError("too high", max_value=100)
        assert err.context["max_value"] == 100

    def test_min_value_zero_is_stored(self):
        err = RangeValidationError("range error", field="age", min_value=0)
        assert err.context["min_value"] == 0

    def test_stores_field_and_value_together(self):
        err = RangeValidationError(
            "range error", field="age", value=150, min_value=0, max_value=120
        )
        assert err.context["field"] == "age"
        assert err.context["min_value"] == 0
        assert err.context["max_value"] == 120


@pytest.mark.unit
class TestFormatValidationError:
    """Tests for FormatValidationError context storage."""

    def test_is_validation_error(self):
        err = FormatValidationError("bad format")
        assert isinstance(err, ValidationError)

    def test_stores_expected_format(self):
        err = FormatValidationError("bad format", expected_format="email")
        assert err.context["expected_format"] == "email"

    def test_stores_pattern(self):
        err = FormatValidationError("bad format", pattern=r"^\S+@\S+\.\S+$")
        assert err.context["pattern"] == r"^\S+@\S+\.\S+$"

    def test_stores_field(self):
        err = FormatValidationError("bad format", field="email_address")
        assert err.context["field"] == "email_address"

    def test_no_optional_args_clean(self):
        err = FormatValidationError("bad format")
        assert "expected_format" not in err.context
        assert "pattern" not in err.context


@pytest.mark.unit
class TestLengthValidationError:
    """Tests for LengthValidationError context storage."""

    def test_is_validation_error(self):
        err = LengthValidationError("wrong length")
        assert isinstance(err, ValidationError)

    def test_stores_actual_length(self):
        err = LengthValidationError("too long", actual_length=256)
        assert err.context["actual_length"] == 256

    def test_stores_min_length(self):
        err = LengthValidationError("too short", min_length=8)
        assert err.context["min_length"] == 8

    def test_stores_max_length(self):
        err = LengthValidationError("too long", max_length=100)
        assert err.context["max_length"] == 100

    def test_actual_length_zero_stored(self):
        err = LengthValidationError("empty", actual_length=0)
        assert err.context["actual_length"] == 0

    def test_min_length_zero_stored(self):
        err = LengthValidationError("wrong", min_length=0)
        assert err.context["min_length"] == 0

    def test_all_length_fields_together(self):
        err = LengthValidationError(
            "length error",
            field="bio",
            actual_length=1500,
            min_length=10,
            max_length=1000,
        )
        assert err.context["field"] == "bio"
        assert err.context["actual_length"] == 1500
        assert err.context["min_length"] == 10
        assert err.context["max_length"] == 1000


@pytest.mark.unit
class TestCustomValidationError:
    """Tests for CustomValidationError context storage."""

    def test_is_validation_error(self):
        err = CustomValidationError("custom failed")
        assert isinstance(err, ValidationError)

    def test_stores_validator_name(self):
        err = CustomValidationError("failed", validator_name="must_be_unique")
        assert err.context["validator_name"] == "must_be_unique"

    def test_stores_field(self):
        err = CustomValidationError("failed", field="username")
        assert err.context["field"] == "username"

    def test_stores_details_dict(self):
        extra = {"reason": "already exists", "suggestions": ["user1", "user2"]}
        err = CustomValidationError("failed", details=extra)
        assert err.context["details"]["reason"] == "already exists"

    def test_no_optional_args_clean(self):
        err = CustomValidationError("failed")
        assert "validator_name" not in err.context
        assert "details" not in err.context

    def test_all_args_together(self):
        err = CustomValidationError(
            "validation failed",
            validator_name="check_luhn",
            field="credit_card",
            details={"algorithm": "luhn"},
        )
        assert err.context["validator_name"] == "check_luhn"
        assert err.context["field"] == "credit_card"
        assert err.context["details"]["algorithm"] == "luhn"
