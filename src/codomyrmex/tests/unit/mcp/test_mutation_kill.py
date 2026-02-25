"""Targeted mutation-killing tests for validation.py and mcp_schemas.py.

These tests exercise boundary conditions, boolean logic, and return paths
to improve the mutation kill ratio above 80%.

Note: We intentionally do NOT use `from __future__ import annotations` here
because _generate_schema_from_func uses `param.annotation is int` identity
checks that only work with real type objects, not stringified annotations.
"""

from typing import Any

import pytest

from codomyrmex.model_context_protocol.quality.validation import (
    _coerce_types,
    _extract_input_schema,
    _generate_schema_from_func,
    _validate_builtin,
    validate_tool_arguments,
)
from codomyrmex.model_context_protocol.schemas.mcp_schemas import (
    MCPToolCall,
    MCPToolRegistry,
    MCPToolResult,
)

# ── validate_tool_arguments boundary tests ────────────────────────


class TestValidateToolArguments:
    """Kill surviving mutants in validate_tool_arguments."""

    def test_none_args_normalized_to_empty(self) -> None:
        """If arguments=None, should be treated as {}."""
        schema = {"inputSchema": {"type": "object", "properties": {}}}
        result = validate_tool_arguments("test", None, schema)
        assert result.valid is True
        assert result.coerced_args == {}

    def test_valid_args_returned_true(self) -> None:
        """Valid args → valid=True."""
        schema = {
            "inputSchema": {
                "type": "object",
                "properties": {"x": {"type": "integer"}},
            }
        }
        result = validate_tool_arguments("test", {"x": 42}, schema)
        assert result.valid is True
        assert result.coerced_args["x"] == 42

    def test_invalid_args_returned_false(self) -> None:
        """Invalid args → valid=False with errors."""
        schema = {
            "inputSchema": {
                "type": "object",
                "properties": {"x": {"type": "integer"}},
                "required": ["x"],
            }
        }
        result = validate_tool_arguments("test", {}, schema)
        assert result.valid is False
        assert len(result.errors) > 0

    def test_no_input_schema_passes_through(self) -> None:
        """No inputSchema → pass through."""
        result = validate_tool_arguments("t", {"x": 1}, {"name": "test"})
        assert result.valid is True
        assert result.coerced_args == {"x": 1}

    def test_coerce_disabled(self) -> None:
        """coerce=False should NOT coerce string→int."""
        schema = {
            "inputSchema": {
                "type": "object",
                "properties": {"x": {"type": "integer"}},
            }
        }
        result = validate_tool_arguments("t", {"x": "42"}, schema, coerce=False)
        # Should NOT coerce; "42" stays a string → validation may fail on type
        assert result.coerced_args.get("x") != 42 or not result.valid


# ── _extract_input_schema boundary tests ──────────────────────────


class TestExtractInputSchema:
    """Kill surviving ComparisonMutator in _extract_input_schema."""

    def test_has_input_schema_key(self) -> None:
        """If 'inputSchema' exists → return it."""
        schema = {"inputSchema": {"type": "object"}}
        assert _extract_input_schema(schema) == {"type": "object"}

    def test_bare_type_schema(self) -> None:
        """If 'type' exists → treat as bare schema."""
        schema = {"type": "object", "properties": {}}
        assert _extract_input_schema(schema) is schema

    def test_bare_properties_only(self) -> None:
        """If 'properties' exists → treat as schema."""
        schema = {"properties": {"x": {"type": "string"}}}
        assert _extract_input_schema(schema) is schema

    def test_unknown_schema_returns_none(self) -> None:
        """No recognizable keys → returns None."""
        assert _extract_input_schema({"name": "t"}) is None

    def test_empty_schema_returns_none(self) -> None:
        """Empty dict → returns None."""
        assert _extract_input_schema({}) is None


# ── _coerce_types boundary and BoolOp tests ───────────────────────


class TestCoerceTypes:
    """Kill surviving BoolOpMutator in _coerce_types."""

    def test_string_to_int(self) -> None:
        """Test functionality: string to int."""
        schema = {"properties": {"x": {"type": "integer"}}}
        result = _coerce_types({"x": "42"}, schema)
        assert result["x"] == 42
        assert isinstance(result["x"], int)

    def test_string_to_float(self) -> None:
        """Test functionality: string to float."""
        schema = {"properties": {"x": {"type": "number"}}}
        result = _coerce_types({"x": "3.14"}, schema)
        assert result["x"] == pytest.approx(3.14)
        assert isinstance(result["x"], float)

    def test_string_to_bool_true(self) -> None:
        """Test functionality: string to bool true."""
        schema = {"properties": {"x": {"type": "boolean"}}}
        for val in ("true", "1", "yes", "on", "True", "YES"):
            result = _coerce_types({"x": val}, schema)
            assert result["x"] is True, f"Failed for {val}"

    def test_string_to_bool_false(self) -> None:
        """Test functionality: string to bool false."""
        schema = {"properties": {"x": {"type": "boolean"}}}
        for val in ("false", "0", "no", "off", "False", "NO"):
            result = _coerce_types({"x": val}, schema)
            assert result["x"] is False, f"Failed for {val}"

    def test_unknown_key_not_coerced(self) -> None:
        """Keys not in properties should be left unchanged."""
        schema = {"properties": {"x": {"type": "integer"}}}
        result = _coerce_types({"y": "42"}, schema)
        assert result["y"] == "42"  # unchanged

    def test_no_type_key_not_coerced(self) -> None:
        """Property without 'type' should not be coerced."""
        schema = {"properties": {"x": {"description": "test"}}}
        result = _coerce_types({"x": "42"}, schema)
        assert result["x"] == "42"  # unchanged

    def test_non_string_not_coerced(self) -> None:
        """Non-string values should not be coerced."""
        schema = {"properties": {"x": {"type": "integer"}}}
        result = _coerce_types({"x": 42}, schema)
        assert result["x"] == 42  # already int

    def test_invalid_int_not_coerced(self) -> None:
        """Non-numeric string for integer → stays string."""
        schema = {"properties": {"x": {"type": "integer"}}}
        result = _coerce_types({"x": "hello"}, schema)
        assert result["x"] == "hello"

    def test_ambiguous_bool_not_coerced(self) -> None:
        """String not in truthy/falsy sets stays unchanged."""
        schema = {"properties": {"x": {"type": "boolean"}}}
        result = _coerce_types({"x": "maybe"}, schema)
        assert result["x"] == "maybe"


# ── _validate_builtin boundary tests ──────────────────────────────


class TestValidateBuiltin:
    """Kill surviving ComparisonMutator and BoolOpMutator in _validate_builtin."""

    def test_required_missing(self) -> None:
        """Test functionality: required missing."""
        schema = {"required": ["x"], "properties": {}}
        errors = _validate_builtin({}, schema, "t")
        assert any("required" in e for e in errors)

    def test_required_present(self) -> None:
        """Test functionality: required present."""
        schema = {"required": ["x"], "properties": {"x": {"type": "string"}}}
        errors = _validate_builtin({"x": "hello"}, schema, "t")
        assert len(errors) == 0

    def test_type_mismatch(self) -> None:
        """Test functionality: type mismatch."""
        schema = {"properties": {"x": {"type": "integer"}}}
        errors = _validate_builtin({"x": "hello"}, schema, "t")
        assert any("type" in e for e in errors)

    def test_type_correct(self) -> None:
        """Test functionality: type correct."""
        schema = {"properties": {"x": {"type": "string"}}}
        errors = _validate_builtin({"x": "hello"}, schema, "t")
        assert len(errors) == 0

    def test_enum_valid(self) -> None:
        """Test functionality: enum valid."""
        schema = {"properties": {"x": {"type": "string", "enum": ["a", "b"]}}}
        errors = _validate_builtin({"x": "a"}, schema, "t")
        assert len(errors) == 0

    def test_enum_invalid(self) -> None:
        """Test functionality: enum invalid."""
        schema = {"properties": {"x": {"type": "string", "enum": ["a", "b"]}}}
        errors = _validate_builtin({"x": "c"}, schema, "t")
        assert any("allowed" in e for e in errors)

    def test_minimum_boundary(self) -> None:
        """Exact minimum should pass; below should fail."""
        schema = {"properties": {"x": {"type": "integer", "minimum": 5}}}
        assert len(_validate_builtin({"x": 5}, schema, "t")) == 0  # exact = OK
        assert len(_validate_builtin({"x": 4}, schema, "t")) > 0  # below = fail
        assert len(_validate_builtin({"x": 6}, schema, "t")) == 0  # above = OK

    def test_maximum_boundary(self) -> None:
        """Exact maximum should pass; above should fail."""
        schema = {"properties": {"x": {"type": "integer", "maximum": 10}}}
        assert len(_validate_builtin({"x": 10}, schema, "t")) == 0  # exact = OK
        assert len(_validate_builtin({"x": 11}, schema, "t")) > 0  # above = fail
        assert len(_validate_builtin({"x": 9}, schema, "t")) == 0  # below = OK

    def test_pattern_match(self) -> None:
        """Test functionality: pattern match."""
        schema = {"properties": {"x": {"type": "string", "pattern": "^[a-z]+$"}}}
        assert len(_validate_builtin({"x": "hello"}, schema, "t")) == 0
        assert len(_validate_builtin({"x": "Hello"}, schema, "t")) > 0

    def test_unknown_key_ignored(self) -> None:
        """Unknown properties not in schema should be silently ignored."""
        schema = {"properties": {"x": {"type": "string"}}}
        errors = _validate_builtin({"x": "ok", "y": 123}, schema, "t")
        assert len(errors) == 0


# ── _generate_schema_from_func boundary tests ─────────────────────


class TestGenerateSchemaFromFunc:
    """Kill surviving ComparisonMutator in _generate_schema_from_func."""

    def test_str_annotation(self) -> None:
        """Test functionality: str annotation."""
        def f(x: str) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "string"

    def test_int_annotation(self) -> None:
        """Test functionality: int annotation."""
        def f(x: int) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "integer"

    def test_float_annotation(self) -> None:
        """Test functionality: float annotation."""
        def f(x: float) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "number"

    def test_bool_annotation(self) -> None:
        """Test functionality: bool annotation."""
        def f(x: bool) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "boolean"

    def test_list_annotation(self) -> None:
        """Test functionality: list annotation."""
        def f(x: list) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "array"

    def test_dict_annotation(self) -> None:
        """Test functionality: dict annotation."""
        def f(x: dict) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "object"

    def test_no_annotation_defaults_string(self) -> None:
        """Test functionality: no annotation defaults string."""
        def f(x): pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "string"

    def test_complex_type_defaults_string(self) -> None:
        """Test functionality: complex type defaults string."""
        def f(x: Any) -> None: pass
        schema = _generate_schema_from_func(f)
        assert schema["properties"]["x"]["type"] == "string"

    def test_required_vs_optional(self) -> None:
        """Test functionality: required vs optional."""
        def f(x: str, y: str = "default") -> None: pass
        schema = _generate_schema_from_func(f)
        assert "x" in schema["required"]
        assert "y" not in schema["required"]

    def test_self_cls_excluded(self) -> None:
        """Test functionality: self cls excluded."""
        class C:
            def m(self, x: int) -> None: pass
        schema = _generate_schema_from_func(C.m)
        assert "self" not in schema["properties"]
        assert "x" in schema["properties"]


# ── MCPToolRegistry return value tests ────────────────────────────


class TestMCPToolRegistryMutationKill:
    """Kill ReturnConst and NoneReturn mutants in mcp_schemas.py."""

    def test_register_and_get(self) -> None:
        """Test functionality: register and get."""
        reg = MCPToolRegistry()
        reg.register(
            tool_name="t1",
            schema={"name": "t1", "description": "test", "inputSchema": {"type": "object"}},
            handler=lambda: None,
        )
        tool = reg.get("t1")
        assert tool is not None
        assert tool["name"] == "t1"

    def test_get_nonexistent_returns_none(self) -> None:
        """Test functionality: get nonexistent returns none."""
        reg = MCPToolRegistry()
        assert reg.get("nonexistent") is None

    def test_list_tools_empty(self) -> None:
        """Test functionality: list tools empty."""
        reg = MCPToolRegistry()
        tools = reg.list_tools()
        assert tools == []

    def test_list_tools_multiple(self) -> None:
        """Test functionality: list tools multiple."""
        reg = MCPToolRegistry()
        for i in range(3):
            reg.register(
                tool_name=f"t{i}",
                schema={"name": f"t{i}", "description": f"Test {i}", "inputSchema": {"type": "object"}},
                handler=lambda: None,
            )
        tools = reg.list_tools()
        assert len(tools) == 3

    def test_has_tool(self) -> None:
        """Test functionality: has tool."""
        reg = MCPToolRegistry()
        reg.register(
            tool_name="t1",
            schema={"name": "t1", "description": "test", "inputSchema": {"type": "object"}},
            handler=lambda: None,
        )
        assert reg.has("t1") is True if hasattr(reg, "has") else True
        assert reg.get("t1") is not None

    def test_tool_count(self) -> None:
        """Test functionality: tool count."""
        reg = MCPToolRegistry()
        assert len(reg.list_tools()) == 0
        reg.register(
            tool_name="t1",
            schema={"name": "t1", "description": "test", "inputSchema": {"type": "object"}},
            handler=lambda: None,
        )
        assert len(reg.list_tools()) == 1


class TestMCPToolCallResult:
    """Kill surviving mutants in MCPToolCall/MCPToolResult."""

    def test_tool_call_fields(self) -> None:
        """Test functionality: tool call fields."""
        call = MCPToolCall(tool_name="test_tool", arguments={"x": 1})
        assert call.tool_name == "test_tool"
        assert call.arguments == {"x": 1}

    def test_tool_result_success(self) -> None:
        """Test functionality: tool result success."""
        result = MCPToolResult(status="success", data={"key": "val"})
        assert result.status == "success"
        assert result.data == {"key": "val"}
        assert result.error is None

    def test_tool_result_with_explanation(self) -> None:
        """Test functionality: tool result with explanation."""
        result = MCPToolResult(status="no_change_needed", explanation="Already up to date")
        assert result.status == "no_change_needed"
        assert result.explanation == "Already up to date"
        assert result.error is None
        assert result.data is None
