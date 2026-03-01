"""Unit tests for configuration schema validation -- types, constraints, and required fields."""

import pytest

from codomyrmex.config_management.core.config_loader import (
    ConfigSchema,
)


# ---------------------------------------------------------------------------
# ConfigSchema tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigSchemaValidation:
    """Tests for ConfigSchema.validate() using real jsonschema validation."""

    def test_valid_object_passes(self):
        """Valid data against a simple object schema produces no errors."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
            },
            title="PersonSchema",
        )
        errors = schema.validate({"name": "Alice", "age": 30})
        assert errors == []

    def test_type_mismatch_produces_error(self):
        """String where integer expected returns a validation error."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            },
        )
        errors = schema.validate({"count": "not_a_number"})
        assert len(errors) == 1
        assert "Validation error" in errors[0]

    def test_missing_required_field_produces_error(self):
        """Missing required field triggers validation error."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"host": {"type": "string"}},
                "required": ["host"],
            },
        )
        errors = schema.validate({})
        assert len(errors) == 1
        assert "host" in errors[0].lower() or "required" in errors[0].lower()

    def test_additional_properties_allowed_by_default(self):
        """Extra properties pass when additionalProperties is not restricted."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"a": {"type": "string"}},
            },
        )
        errors = schema.validate({"a": "hello", "extra": 999})
        assert errors == []

    def test_additional_properties_forbidden(self):
        """Extra properties fail when additionalProperties is false."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"a": {"type": "string"}},
                "additionalProperties": False,
            },
        )
        errors = schema.validate({"a": "hello", "extra": 999})
        assert len(errors) >= 1

    def test_nested_object_validation(self):
        """Nested objects are validated recursively."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "db": {
                        "type": "object",
                        "properties": {"port": {"type": "integer"}},
                        "required": ["port"],
                    }
                },
            },
        )
        # Valid nested
        assert schema.validate({"db": {"port": 5432}}) == []
        # Invalid nested
        errors = schema.validate({"db": {"port": "bad"}})
        assert len(errors) >= 1

    def test_array_validation(self):
        """Array items are validated correctly."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
            },
        )
        assert schema.validate({"tags": ["a", "b"]}) == []
        errors = schema.validate({"tags": [1, 2]})
        assert len(errors) >= 1

    def test_enum_constraint(self):
        """Enum constraints reject values outside the allowed set."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "level": {"type": "string", "enum": ["DEBUG", "INFO", "ERROR"]},
                },
            },
        )
        assert schema.validate({"level": "INFO"}) == []
        errors = schema.validate({"level": "TRACE"})
        assert len(errors) >= 1

    def test_minimum_maximum_constraints(self):
        """Numeric min/max constraints are enforced."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                },
            },
        )
        assert schema.validate({"port": 8080}) == []
        assert len(schema.validate({"port": 0})) >= 1
        assert len(schema.validate({"port": 70000})) >= 1

    def test_empty_schema_accepts_anything(self):
        """An empty schema (no constraints) should accept any object."""
        schema = ConfigSchema(schema={})
        assert schema.validate({"anything": "goes"}) == []
        assert schema.validate(42) == []

    def test_schema_defaults(self):
        """ConfigSchema default field values are correctly set."""
        schema = ConfigSchema(schema={"type": "object"})
        assert schema.version == "draft7"
        assert schema.title == ""
        assert schema.description == ""

    @pytest.mark.parametrize(
        "data,expected_valid",
        [
            ({"name": "ok"}, True),
            ({}, False),
            ({"name": 123}, False),
            ({"name": ""}, True),  # empty string is still a string
        ],
    )
    def test_parametrized_required_string(self, data, expected_valid):
        """Parametrized validation of a required string field."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        )
        errors = schema.validate(data)
        if expected_valid:
            assert errors == []
        else:
            assert len(errors) >= 1


# ---------------------------------------------------------------------------
# ConfigSchema -- error and edge-case paths (lines 99, 105-108)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigSchemaErrorPaths:
    """Tests for ConfigSchema.validate edge cases: SchemaError, generic Exception, non-draft version."""

    def test_non_draft_version_sets_format_checker_none(self):
        """When version does not start with 'draft', format_checker is None (line 99)."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
            version="openapi3",
        )
        # Should still validate successfully without format_checker
        errors = schema.validate({"name": "hello"})
        assert errors == []

    def test_non_draft_version_still_catches_type_errors(self):
        """Non-draft version still catches type validation errors."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            },
            version="custom_v1",
        )
        errors = schema.validate({"count": "not_int"})
        assert len(errors) == 1
        assert "Validation error" in errors[0]

    def test_schema_error_is_caught(self):
        """An invalid schema (SchemaError) is caught and reported (lines 105-106)."""
        # A schema with an invalid type value triggers SchemaError
        schema = ConfigSchema(
            schema={
                "type": "not_a_valid_type",
            },
        )
        errors = schema.validate({"anything": True})
        assert len(errors) >= 1
        assert any("Schema error" in e or "Validation failed" in e for e in errors)

    def test_generic_exception_in_validate(self):
        """A schema that triggers a generic exception is caught (lines 107-108)."""
        # Pass something that is not a valid JSON schema structure at all
        schema = ConfigSchema(
            schema=None,  # type: ignore[arg-type]
        )
        errors = schema.validate({"anything": True})
        assert len(errors) >= 1
        # Should be caught by the generic Exception handler
        assert any("Validation failed" in e or "Schema error" in e for e in errors)

    def test_format_checker_for_draft_version(self):
        """Draft versions create a FormatChecker and use it during validation."""
        schema = ConfigSchema(
            schema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                },
            },
            version="draft7",
        )
        # Basic string that happens to pass -- format checking may be lenient
        # depending on jsonschema version, but the code path is exercised
        errors = schema.validate({"email": "test@example.com"})
        assert errors == []
