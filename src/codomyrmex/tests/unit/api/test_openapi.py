"""Tests for APISchema and OpenAPISpecification from codomyrmex.api.openapi_generator."""

import json
import os
import tempfile

import pytest

from codomyrmex.api.openapi_generator import (
    APISchema,
    OpenAPISpecification,
)


# ---------------------------------------------------------------------------
# APISchema dataclass
# ---------------------------------------------------------------------------

class TestAPISchemaParametrized:
    """Parametrized tests for APISchema across different schema types."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "schema_type",
        ["object", "array", "string", "integer", "number", "boolean"],
    )
    def test_schema_type_round_trips(self, schema_type):
        """Each schema_type must appear in to_dict output unchanged."""
        schema = APISchema(name="T", schema_type=schema_type)
        result = schema.to_dict()
        assert result["type"] == schema_type

    @pytest.mark.unit
    def test_schema_empty_properties(self):
        """Schema with no properties should still have an empty dict."""
        schema = APISchema(name="Empty", schema_type="object")
        result = schema.to_dict()
        assert result["properties"] == {}

    @pytest.mark.unit
    def test_schema_required_omitted_when_empty(self):
        """If required list is empty, key must NOT appear in output."""
        schema = APISchema(name="NoReq", schema_type="object", required=[])
        result = schema.to_dict()
        assert "required" not in result

    @pytest.mark.unit
    def test_schema_example_omitted_when_none(self):
        """If example is None, key must NOT appear in output."""
        schema = APISchema(name="NoEx", schema_type="object", example=None)
        result = schema.to_dict()
        assert "example" not in result

    @pytest.mark.unit
    def test_schema_multiple_required_fields(self):
        """All required field names must appear in output."""
        schema = APISchema(
            name="Multi",
            schema_type="object",
            properties={"a": {"type": "string"}, "b": {"type": "integer"}, "c": {"type": "boolean"}},
            required=["a", "b", "c"],
        )
        result = schema.to_dict()
        assert result["required"] == ["a", "b", "c"]

    @pytest.mark.unit
    def test_schema_nested_properties(self):
        """Properties can contain nested schema references."""
        schema = APISchema(
            name="Parent",
            schema_type="object",
            properties={
                "child": {
                    "type": "object",
                    "properties": {"inner": {"type": "string"}},
                },
            },
        )
        result = schema.to_dict()
        assert result["properties"]["child"]["type"] == "object"


# ---------------------------------------------------------------------------
# OpenAPISpecification container
# ---------------------------------------------------------------------------

class TestOpenAPISpecificationExtended:
    """Extended tests for OpenAPISpecification beyond basic coverage."""

    @pytest.mark.unit
    def test_to_json_custom_indent(self):
        """to_json should honour a custom indent value."""
        spec = OpenAPISpecification()
        spec.spec = {"openapi": "3.0.3", "info": {"title": "T"}, "paths": {}}
        json_4 = spec.to_json(indent=4)
        # 4-space indent produces at least 4 leading spaces on nested keys
        assert "    " in json_4

    @pytest.mark.unit
    def test_to_json_is_valid_json(self):
        """Output of to_json must be parseable."""
        spec = OpenAPISpecification()
        spec.spec = {"key": [1, 2, 3]}
        parsed = json.loads(spec.to_json())
        assert parsed["key"] == [1, 2, 3]

    @pytest.mark.unit
    def test_default_version_is_303(self):
        """Default version attribute should be 3.0.3."""
        spec = OpenAPISpecification()
        assert spec.version == "3.0.3"

    @pytest.mark.unit
    def test_save_to_file_yaml(self):
        """save_to_file with format='yaml' should produce a readable file."""
        spec = OpenAPISpecification()
        spec.spec = {"openapi": "3.0.3", "info": {"title": "Y"}, "paths": {}}
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            filepath = f.name
        try:
            spec.save_to_file(filepath, format="yaml")
            with open(filepath) as f:
                content = f.read()
            assert "openapi" in content
        finally:
            os.unlink(filepath)

    @pytest.mark.unit
    def test_save_to_file_json_roundtrip(self):
        """save_to_file(json) content should round-trip through json.load."""
        spec = OpenAPISpecification()
        spec.spec = {"openapi": "3.0.3", "info": {"title": "RT"}, "paths": {}}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name
        try:
            spec.save_to_file(filepath, format="json")
            with open(filepath) as f:
                loaded = json.load(f)
            assert loaded == spec.spec
        finally:
            os.unlink(filepath)

    @pytest.mark.unit
    def test_to_dict_returns_same_reference(self):
        """to_dict should return the actual spec dict (same object)."""
        spec = OpenAPISpecification()
        spec.spec = {"a": 1}
        assert spec.to_dict() is spec.spec
