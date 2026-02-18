"""Tests for MCP validation middleware (validate_tool_arguments).

All zero-mock — validates real JSON Schema checking, type coercion,
and error reporting.
"""

import pytest

from codomyrmex.model_context_protocol.validation import (
    ValidationResult,
    validate_tool_arguments,
)


# ── Helpers ──────────────────────────────────────────────────────────

TOOL = "test_tool"

SCHEMA_SIMPLE = {
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "count": {"type": "integer"},
            "enabled": {"type": "boolean"},
        },
        "required": ["name"],
    }
}

SCHEMA_ENUM = {
    "inputSchema": {
        "type": "object",
        "properties": {
            "level": {"type": "string", "enum": ["low", "medium", "high"]},
        },
        "required": ["level"],
    }
}

SCHEMA_NUMERIC = {
    "inputSchema": {
        "type": "object",
        "properties": {
            "value": {"type": "integer", "minimum": 0, "maximum": 100},
        },
        "required": ["value"],
    }
}

SCHEMA_PATTERN = {
    "inputSchema": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "pattern": r"^[\w.+-]+@[\w-]+\.[\w.]+$"},
        },
    }
}

SCHEMA_NESTED = {
    "inputSchema": {
        "type": "object",
        "properties": {
            "config": {
                "type": "object",
                "properties": {
                    "timeout": {"type": "integer"},
                },
                "required": ["timeout"],
            },
        },
        "required": ["config"],
    }
}

SCHEMA_ARRAY = {
    "inputSchema": {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }
}


# ── Basic validation ─────────────────────────────────────────────────

def test_valid_args_pass():
    result = validate_tool_arguments(TOOL, {"name": "hello", "count": 5}, SCHEMA_SIMPLE)
    assert result.valid
    assert result.errors == []
    assert result.coerced_args["name"] == "hello"


def test_missing_required_field_rejected():
    result = validate_tool_arguments(TOOL, {"count": 5}, SCHEMA_SIMPLE)
    assert not result.valid
    assert any("name" in e for e in result.errors)


def test_invalid_type_rejected():
    result = validate_tool_arguments(
        TOOL, {"name": "hello", "count": "not_a_number"}, SCHEMA_SIMPLE, coerce=False
    )
    assert not result.valid
    assert any("count" in e or "type" in e for e in result.errors)


def test_extra_field_ignored():
    """additionalProperties is not restricted — extra fields pass through."""
    result = validate_tool_arguments(
        TOOL, {"name": "hello", "extra_field": "ignored"}, SCHEMA_SIMPLE
    )
    assert result.valid


# ── Type coercion ────────────────────────────────────────────────────

def test_coerce_str_to_int():
    result = validate_tool_arguments(TOOL, {"name": "x", "count": "42"}, SCHEMA_SIMPLE)
    assert result.valid
    assert result.coerced_args["count"] == 42


def test_coerce_str_to_bool_true():
    result = validate_tool_arguments(
        TOOL, {"name": "x", "enabled": "true"}, SCHEMA_SIMPLE
    )
    assert result.valid
    assert result.coerced_args["enabled"] is True


def test_coerce_str_to_bool_false():
    result = validate_tool_arguments(
        TOOL, {"name": "x", "enabled": "false"}, SCHEMA_SIMPLE
    )
    assert result.valid
    assert result.coerced_args["enabled"] is False


# ── Enum validation ──────────────────────────────────────────────────

def test_enum_valid():
    result = validate_tool_arguments(TOOL, {"level": "high"}, SCHEMA_ENUM)
    assert result.valid


def test_enum_invalid():
    result = validate_tool_arguments(TOOL, {"level": "extreme"}, SCHEMA_ENUM)
    assert not result.valid
    assert any("level" in e for e in result.errors)


# ── Numeric range ────────────────────────────────────────────────────

def test_minimum_violated():
    result = validate_tool_arguments(TOOL, {"value": -1}, SCHEMA_NUMERIC)
    assert not result.valid
    assert any("minimum" in e.lower() or "value" in e for e in result.errors)


def test_maximum_violated():
    result = validate_tool_arguments(TOOL, {"value": 101}, SCHEMA_NUMERIC)
    assert not result.valid
    assert any("maximum" in e.lower() or "value" in e for e in result.errors)


def test_in_range_passes():
    result = validate_tool_arguments(TOOL, {"value": 50}, SCHEMA_NUMERIC)
    assert result.valid


# ── Pattern validation ───────────────────────────────────────────────

def test_pattern_match():
    result = validate_tool_arguments(TOOL, {"email": "a@b.com"}, SCHEMA_PATTERN)
    assert result.valid


def test_pattern_mismatch():
    result = validate_tool_arguments(TOOL, {"email": "not-an-email"}, SCHEMA_PATTERN)
    assert not result.valid
    assert any("pattern" in e.lower() or "email" in e for e in result.errors)


# ── Nested / array schemas ──────────────────────────────────────────

def test_nested_schema_valid():
    result = validate_tool_arguments(TOOL, {"config": {"timeout": 30}}, SCHEMA_NESTED)
    assert result.valid


def test_nested_schema_missing_inner_required():
    result = validate_tool_arguments(TOOL, {"config": {}}, SCHEMA_NESTED)
    assert not result.valid


def test_array_schema_valid():
    result = validate_tool_arguments(TOOL, {"tags": ["a", "b"]}, SCHEMA_ARRAY)
    assert result.valid


# ── Edge cases ───────────────────────────────────────────────────────

def test_no_schema_passes_through():
    """Tool with no inputSchema validation passes everything."""
    result = validate_tool_arguments(TOOL, {"anything": "goes"}, {})
    assert result.valid


def test_empty_args_with_no_required():
    schema = {"inputSchema": {"type": "object", "properties": {"x": {"type": "string"}}}}
    result = validate_tool_arguments(TOOL, {}, schema)
    assert result.valid


def test_bare_json_schema_detected():
    """Schema that IS a JSON Schema object (not wrapped in inputSchema) is handled."""
    bare = {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
    result = validate_tool_arguments(TOOL, {"name": "ok"}, bare)
    assert result.valid
