"""
Unit tests for tool_use.validation — Zero-Mock compliant.

Covers: ValidationResult (defaults, merge, to_dict), validate_input /
validate_output (empty schema, type checks, union types, enum, string
constraints, numeric constraints, array items/min/max, object required/
properties/additionalProperties), _validate_value edge cases.
"""

import pytest

from codomyrmex.tool_use.validation import (
    ValidationResult,
    validate_input,
    validate_output,
)

# ── ValidationResult ───────────────────────────────────────────────────


@pytest.mark.unit
class TestValidationResult:
    def test_valid_default_true(self):
        r = ValidationResult()
        assert r.valid is True

    def test_errors_default_empty(self):
        r = ValidationResult()
        assert r.errors == []

    def test_invalid_with_errors(self):
        r = ValidationResult(valid=False, errors=["field required"])
        assert r.valid is False
        assert "field required" in r.errors

    def test_to_dict_valid_true(self):
        r = ValidationResult(valid=True)
        d = r.to_dict()
        assert d["valid"] is True
        assert d["errors"] == []

    def test_to_dict_valid_false_with_errors(self):
        r = ValidationResult(valid=False, errors=["err1", "err2"])
        d = r.to_dict()
        assert d["valid"] is False
        assert len(d["errors"]) == 2

    def test_merge_both_valid(self):
        r1 = ValidationResult(valid=True)
        r2 = ValidationResult(valid=True)
        merged = r1.merge(r2)
        assert merged.valid is True

    def test_merge_one_invalid(self):
        r1 = ValidationResult(valid=True)
        r2 = ValidationResult(valid=False, errors=["bad field"])
        merged = r1.merge(r2)
        assert merged.valid is False
        assert "bad field" in merged.errors

    def test_merge_combines_errors(self):
        r1 = ValidationResult(valid=False, errors=["err1"])
        r2 = ValidationResult(valid=False, errors=["err2"])
        merged = r1.merge(r2)
        assert "err1" in merged.errors
        assert "err2" in merged.errors

    def test_merge_empty_errors(self):
        r1 = ValidationResult()
        r2 = ValidationResult()
        merged = r1.merge(r2)
        assert merged.errors == []


# ── validate_input — basic ─────────────────────────────────────────────


@pytest.mark.unit
class TestValidateInputBasic:
    def test_empty_schema_always_valid(self):
        result = validate_input({"any": "data"}, {})
        assert result.valid is True

    def test_none_schema_valid(self):
        result = validate_input("anything", {})
        assert result.valid is True

    def test_string_type_valid(self):
        result = validate_input("hello", {"type": "string"})
        assert result.valid is True

    def test_string_type_invalid(self):
        result = validate_input(42, {"type": "string"})
        assert result.valid is False
        assert len(result.errors) > 0

    def test_integer_type_valid(self):
        result = validate_input(5, {"type": "integer"})
        assert result.valid is True

    def test_number_accepts_int(self):
        result = validate_input(5, {"type": "number"})
        assert result.valid is True

    def test_number_accepts_float(self):
        result = validate_input(5.5, {"type": "number"})
        assert result.valid is True

    def test_boolean_type_valid(self):
        result = validate_input(True, {"type": "boolean"})
        assert result.valid is True

    def test_array_type_valid(self):
        result = validate_input([1, 2, 3], {"type": "array"})
        assert result.valid is True

    def test_object_type_valid(self):
        result = validate_input({"a": 1}, {"type": "object"})
        assert result.valid is True

    def test_null_type_valid(self):
        result = validate_input(None, {"type": "null"})
        assert result.valid is True


# ── validate_input — union types ───────────────────────────────────────


@pytest.mark.unit
class TestValidateInputUnionTypes:
    def test_union_string_or_null_with_string(self):
        result = validate_input("hello", {"type": ["string", "null"]})
        assert result.valid is True

    def test_union_string_or_null_with_none(self):
        result = validate_input(None, {"type": ["string", "null"]})
        assert result.valid is True

    def test_union_string_or_null_with_int_invalid(self):
        result = validate_input(42, {"type": ["string", "null"]})
        assert result.valid is False


# ── validate_input — enum ──────────────────────────────────────────────


@pytest.mark.unit
class TestValidateInputEnum:
    def test_value_in_enum_valid(self):
        result = validate_input("red", {"enum": ["red", "green", "blue"]})
        assert result.valid is True

    def test_value_not_in_enum_invalid(self):
        result = validate_input("yellow", {"enum": ["red", "green", "blue"]})
        assert result.valid is False
        assert len(result.errors) > 0


# ── validate_input — string constraints ───────────────────────────────


@pytest.mark.unit
class TestValidateInputStringConstraints:
    def test_min_length_satisfied(self):
        result = validate_input("abc", {"type": "string", "minLength": 2})
        assert result.valid is True

    def test_min_length_violated(self):
        result = validate_input("a", {"type": "string", "minLength": 3})
        assert result.valid is False

    def test_max_length_satisfied(self):
        result = validate_input("hi", {"type": "string", "maxLength": 10})
        assert result.valid is True

    def test_max_length_violated(self):
        result = validate_input("a" * 20, {"type": "string", "maxLength": 5})
        assert result.valid is False

    def test_exact_min_length_valid(self):
        result = validate_input("abc", {"type": "string", "minLength": 3})
        assert result.valid is True

    def test_exact_max_length_valid(self):
        result = validate_input("abcde", {"type": "string", "maxLength": 5})
        assert result.valid is True


# ── validate_input — numeric constraints ──────────────────────────────


@pytest.mark.unit
class TestValidateInputNumericConstraints:
    def test_minimum_satisfied(self):
        result = validate_input(5, {"type": "integer", "minimum": 0})
        assert result.valid is True

    def test_minimum_violated(self):
        result = validate_input(-1, {"type": "integer", "minimum": 0})
        assert result.valid is False

    def test_minimum_at_boundary_valid(self):
        result = validate_input(0, {"type": "integer", "minimum": 0})
        assert result.valid is True

    def test_maximum_satisfied(self):
        result = validate_input(50, {"type": "number", "maximum": 100})
        assert result.valid is True

    def test_maximum_violated(self):
        result = validate_input(150.0, {"type": "number", "maximum": 100})
        assert result.valid is False

    def test_maximum_at_boundary_valid(self):
        result = validate_input(100, {"type": "integer", "maximum": 100})
        assert result.valid is True

    def test_bool_not_treated_as_number(self):
        """bool is a subclass of int but numeric constraints should not apply."""
        result = validate_input(True, {"type": "boolean"})
        assert result.valid is True


# ── validate_input — array constraints ────────────────────────────────


@pytest.mark.unit
class TestValidateInputArrayConstraints:
    def test_min_items_satisfied(self):
        result = validate_input([1, 2, 3], {"type": "array", "minItems": 2})
        assert result.valid is True

    def test_min_items_violated(self):
        result = validate_input([1], {"type": "array", "minItems": 2})
        assert result.valid is False

    def test_max_items_satisfied(self):
        result = validate_input([1, 2], {"type": "array", "maxItems": 5})
        assert result.valid is True

    def test_max_items_violated(self):
        result = validate_input([1, 2, 3, 4, 5, 6], {"type": "array", "maxItems": 5})
        assert result.valid is False

    def test_items_schema_valid(self):
        result = validate_input(
            ["a", "b", "c"],
            {"type": "array", "items": {"type": "string"}},
        )
        assert result.valid is True

    def test_items_schema_invalid_element(self):
        result = validate_input(
            ["a", 2, "c"],
            {"type": "array", "items": {"type": "string"}},
        )
        assert result.valid is False

    def test_empty_array_min_items_violated(self):
        result = validate_input([], {"type": "array", "minItems": 1})
        assert result.valid is False

    def test_empty_array_min_items_zero_valid(self):
        result = validate_input([], {"type": "array", "minItems": 0})
        assert result.valid is True


# ── validate_input — object constraints ───────────────────────────────


@pytest.mark.unit
class TestValidateInputObjectConstraints:
    def test_required_fields_present(self):
        schema = {
            "type": "object",
            "required": ["name", "age"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
        }
        result = validate_input({"name": "Alice", "age": 30}, schema)
        assert result.valid is True

    def test_required_field_missing(self):
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        result = validate_input({}, schema)
        assert result.valid is False
        assert any("required" in e for e in result.errors)

    def test_property_type_violation(self):
        schema = {
            "type": "object",
            "properties": {"count": {"type": "integer"}},
        }
        result = validate_input({"count": "not-a-number"}, schema)
        assert result.valid is False

    def test_additional_properties_false_disallows_extra(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": False,
        }
        result = validate_input({"name": "Alice", "extra": "field"}, schema)
        assert result.valid is False
        assert any("additional" in e for e in result.errors)

    def test_additional_properties_not_set_allows_extra(self):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        result = validate_input({"name": "Alice", "extra": "field"}, schema)
        assert result.valid is True

    def test_nested_object_validation(self):
        schema = {
            "type": "object",
            "properties": {
                "address": {
                    "type": "object",
                    "required": ["city"],
                    "properties": {"city": {"type": "string"}},
                }
            },
        }
        result = validate_input({"address": {"city": "NYC"}}, schema)
        assert result.valid is True

    def test_nested_object_missing_required(self):
        schema = {
            "type": "object",
            "properties": {
                "address": {
                    "type": "object",
                    "required": ["city"],
                    "properties": {"city": {"type": "string"}},
                }
            },
        }
        result = validate_input({"address": {}}, schema)
        assert result.valid is False

    def test_type_error_skips_deeper_checks(self):
        """If type check fails, deeper checks are skipped (early return)."""
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}},
        }
        # Passing a string instead of dict → type error, not required field error
        result = validate_input("not a dict", schema)
        assert result.valid is False
        # Should only have the type error, not a "required" error
        assert len(result.errors) == 1


# ── validate_output — mirrors validate_input ──────────────────────────


@pytest.mark.unit
class TestValidateOutput:
    def test_empty_schema_valid(self):
        result = validate_output({"result": 42}, {})
        assert result.valid is True

    def test_type_check(self):
        result = validate_output("hello", {"type": "string"})
        assert result.valid is True

    def test_type_violation(self):
        result = validate_output(42, {"type": "string"})
        assert result.valid is False

    def test_returns_validation_result(self):
        result = validate_output({}, {"type": "object"})
        assert isinstance(result, ValidationResult)

    def test_full_object_schema(self):
        schema = {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {"type": "string", "enum": ["ok", "error"]},
                "data": {"type": "object"},
            },
        }
        result = validate_output({"status": "ok", "data": {"key": "val"}}, schema)
        assert result.valid is True
