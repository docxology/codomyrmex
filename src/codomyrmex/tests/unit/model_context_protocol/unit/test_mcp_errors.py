"""
Unit tests for model_context_protocol.errors — Zero-Mock compliant.

Covers: MCPErrorCode (all values), FieldError (to_dict with/without value),
MCPToolError (defaults, to_dict optional fields, to_json, to_mcp_response,
from_dict, from_json, from_mcp_response — not-error/empty/structured/
unstructured), convenience constructors (validation_error, not_found_error,
timeout_error, execution_error).
"""

import json

import pytest

from codomyrmex.model_context_protocol.errors import (
    FieldError,
    MCPErrorCode,
    MCPToolError,
    execution_error,
    not_found_error,
    timeout_error,
    validation_error,
)

# ── MCPErrorCode ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestMCPErrorCode:
    def test_validation_error_value(self):
        assert MCPErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"

    def test_execution_error_value(self):
        assert MCPErrorCode.EXECUTION_ERROR == "EXECUTION_ERROR"

    def test_timeout_value(self):
        assert MCPErrorCode.TIMEOUT == "TIMEOUT"

    def test_not_found_value(self):
        assert MCPErrorCode.NOT_FOUND == "NOT_FOUND"

    def test_rate_limited_value(self):
        assert MCPErrorCode.RATE_LIMITED == "RATE_LIMITED"

    def test_circuit_open_value(self):
        assert MCPErrorCode.CIRCUIT_OPEN == "CIRCUIT_OPEN"

    def test_dependency_missing_value(self):
        assert MCPErrorCode.DEPENDENCY_MISSING == "DEPENDENCY_MISSING"

    def test_access_denied_value(self):
        assert MCPErrorCode.ACCESS_DENIED == "ACCESS_DENIED"

    def test_internal_value(self):
        assert MCPErrorCode.INTERNAL == "INTERNAL"


# ── FieldError ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFieldError:
    def test_field_and_constraint_stored(self):
        fe = FieldError(field="name", constraint="required")
        assert fe.field == "name"
        assert fe.constraint == "required"

    def test_value_default_none(self):
        fe = FieldError(field="name", constraint="required")
        assert fe.value is None

    def test_to_dict_without_value(self):
        fe = FieldError(field="age", constraint="min:0")
        d = fe.to_dict()
        assert d["field"] == "age"
        assert d["constraint"] == "min:0"
        assert "value" not in d

    def test_to_dict_with_value(self):
        fe = FieldError(field="age", constraint="min:0", value=-5)
        d = fe.to_dict()
        assert d["field"] == "age"
        assert d["constraint"] == "min:0"
        assert d["value"] == -5

    def test_to_dict_with_zero_value(self):
        """value=0 is not None → stored."""
        fe = FieldError(field="count", constraint="positive", value=0)
        d = fe.to_dict()
        assert "value" in d
        assert d["value"] == 0

    def test_frozen_immutable(self):
        fe = FieldError(field="x", constraint="required")
        with pytest.raises((AttributeError, TypeError)):
            fe.field = "y"  # type: ignore[misc]


# ── MCPToolError ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestMCPToolError:
    def test_code_and_message_required(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="internal error")
        assert e.code == MCPErrorCode.INTERNAL
        assert e.message == "internal error"

    def test_tool_name_default_empty(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert e.tool_name == ""

    def test_module_default_empty(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert e.module == ""

    def test_field_errors_default_empty(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert e.field_errors == []

    def test_suggestion_default_none(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert e.suggestion is None

    def test_correlation_id_auto_generated(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert len(e.correlation_id) > 0

    def test_correlation_ids_unique(self):
        e1 = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        e2 = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert e1.correlation_id != e2.correlation_id

    def test_to_dict_required_keys(self):
        e = MCPToolError(code=MCPErrorCode.NOT_FOUND, message="not found")
        d = e.to_dict()
        assert d["code"] == "NOT_FOUND"
        assert d["message"] == "not found"
        assert "correlation_id" in d

    def test_to_dict_tool_name_included_when_set(self):
        e = MCPToolError(
            code=MCPErrorCode.EXECUTION_ERROR, message="err", tool_name="my_tool"
        )
        d = e.to_dict()
        assert d["tool_name"] == "my_tool"

    def test_to_dict_tool_name_excluded_when_empty(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert "tool_name" not in e.to_dict()

    def test_to_dict_module_included_when_set(self):
        e = MCPToolError(
            code=MCPErrorCode.EXECUTION_ERROR, message="err", module="search"
        )
        d = e.to_dict()
        assert d["module"] == "search"

    def test_to_dict_module_excluded_when_empty(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert "module" not in e.to_dict()

    def test_to_dict_field_errors_included_when_present(self):
        fe = FieldError(field="name", constraint="required")
        e = MCPToolError(
            code=MCPErrorCode.VALIDATION_ERROR,
            message="invalid",
            field_errors=[fe],
        )
        d = e.to_dict()
        assert "field_errors" in d
        assert len(d["field_errors"]) == 1

    def test_to_dict_field_errors_excluded_when_empty(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert "field_errors" not in e.to_dict()

    def test_to_dict_suggestion_included_when_set(self):
        e = MCPToolError(
            code=MCPErrorCode.EXECUTION_ERROR,
            message="err",
            suggestion="Try again later",
        )
        d = e.to_dict()
        assert d["suggestion"] == "Try again later"

    def test_to_dict_suggestion_excluded_when_none(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="err")
        assert "suggestion" not in e.to_dict()

    def test_to_json_returns_valid_json(self):
        e = MCPToolError(
            code=MCPErrorCode.NOT_FOUND, message="not found", tool_name="get_item"
        )
        text = e.to_json()
        parsed = json.loads(text)
        assert parsed["code"] == "NOT_FOUND"
        assert parsed["message"] == "not found"

    def test_to_mcp_response_structure(self):
        e = MCPToolError(code=MCPErrorCode.INTERNAL, message="oops")
        resp = e.to_mcp_response()
        assert resp["isError"] is True
        assert isinstance(resp["content"], list)
        assert resp["content"][0]["type"] == "text"

    def test_to_mcp_response_content_parseable(self):
        e = MCPToolError(code=MCPErrorCode.TIMEOUT, message="timed out")
        resp = e.to_mcp_response()
        parsed = json.loads(resp["content"][0]["text"])
        assert parsed["code"] == "TIMEOUT"


# ── MCPToolError — from_dict / from_json ──────────────────────────────


@pytest.mark.unit
class TestMCPToolErrorDeserialization:
    def test_from_dict_round_trip(self):
        original = MCPToolError(
            code=MCPErrorCode.NOT_FOUND,
            message="not found",
            tool_name="get_user",
        )
        d = original.to_dict()
        restored = MCPToolError.from_dict(d)
        assert restored.code == MCPErrorCode.NOT_FOUND
        assert restored.message == "not found"
        assert restored.tool_name == "get_user"

    def test_from_dict_with_field_errors(self):
        data = {
            "code": "VALIDATION_ERROR",
            "message": "invalid input",
            "correlation_id": "abc123",
            "field_errors": [{"field": "name", "constraint": "required"}],
        }
        e = MCPToolError.from_dict(data)
        assert len(e.field_errors) == 1
        assert e.field_errors[0].field == "name"

    def test_from_dict_optional_fields_defaults(self):
        data = {
            "code": "INTERNAL",
            "message": "err",
        }
        e = MCPToolError.from_dict(data)
        assert e.tool_name == ""
        assert e.module == ""
        assert e.suggestion is None

    def test_from_json_round_trip(self):
        original = MCPToolError(
            code=MCPErrorCode.EXECUTION_ERROR, message="crashed", module="search"
        )
        text = original.to_json()
        restored = MCPToolError.from_json(text)
        assert restored.code == MCPErrorCode.EXECUTION_ERROR
        assert restored.message == "crashed"
        assert restored.module == "search"


# ── MCPToolError — from_mcp_response ──────────────────────────────────


@pytest.mark.unit
class TestMCPToolErrorFromMCPResponse:
    def test_non_error_response_returns_none(self):
        resp = {"isError": False, "content": [{"type": "text", "text": "ok"}]}
        assert MCPToolError.from_mcp_response(resp) is None

    def test_no_iserror_key_returns_none(self):
        resp = {"content": [{"type": "text", "text": "ok"}]}
        assert MCPToolError.from_mcp_response(resp) is None

    def test_empty_content_returns_none(self):
        resp = {"isError": True, "content": []}
        assert MCPToolError.from_mcp_response(resp) is None

    def test_structured_error_parsed(self):
        original = MCPToolError(
            code=MCPErrorCode.TIMEOUT, message="timeout"
        )
        resp = original.to_mcp_response()
        restored = MCPToolError.from_mcp_response(resp)
        assert restored is not None
        assert restored.code == MCPErrorCode.TIMEOUT

    def test_unstructured_error_wrapped_as_internal(self):
        """Non-JSON content → wrapped as INTERNAL error."""
        resp = {
            "isError": True,
            "content": [{"type": "text", "text": "plain error text"}],
        }
        e = MCPToolError.from_mcp_response(resp)
        assert e is not None
        assert e.code == MCPErrorCode.INTERNAL
        assert e.message == "plain error text"

    def test_invalid_json_wrapped_as_internal(self):
        resp = {
            "isError": True,
            "content": [{"type": "text", "text": "{invalid json}"}],
        }
        e = MCPToolError.from_mcp_response(resp)
        assert e is not None
        assert e.code == MCPErrorCode.INTERNAL


# ── Convenience constructors ───────────────────────────────────────────


@pytest.mark.unit
class TestConvenienceConstructors:
    def test_validation_error_code(self):
        e = validation_error("my_tool", "name is required")
        assert e.code == MCPErrorCode.VALIDATION_ERROR

    def test_validation_error_tool_name(self):
        e = validation_error("my_tool", "name is required")
        assert e.tool_name == "my_tool"

    def test_validation_error_message(self):
        e = validation_error("my_tool", "name is required")
        assert e.message == "name is required"

    def test_validation_error_with_field_errors(self):
        fe = FieldError(field="name", constraint="required")
        e = validation_error("tool", "bad input", field_errors=[fe])
        assert len(e.field_errors) == 1

    def test_validation_error_default_empty_field_errors(self):
        e = validation_error("tool", "bad input")
        assert e.field_errors == []

    def test_not_found_error_code(self):
        e = not_found_error("unknown_tool")
        assert e.code == MCPErrorCode.NOT_FOUND

    def test_not_found_error_tool_name(self):
        e = not_found_error("unknown_tool")
        assert e.tool_name == "unknown_tool"

    def test_not_found_error_message_contains_tool(self):
        e = not_found_error("my_tool")
        assert "my_tool" in e.message

    def test_timeout_error_code(self):
        e = timeout_error("slow_tool", 30.0)
        assert e.code == MCPErrorCode.TIMEOUT

    def test_timeout_error_tool_name(self):
        e = timeout_error("slow_tool", 30.0)
        assert e.tool_name == "slow_tool"

    def test_timeout_error_message_contains_seconds(self):
        e = timeout_error("slow_tool", 30.0)
        assert "30" in e.message

    def test_execution_error_code(self):
        e = execution_error("my_tool", ValueError("bad value"))
        assert e.code == MCPErrorCode.EXECUTION_ERROR

    def test_execution_error_tool_name(self):
        e = execution_error("my_tool", ValueError("bad value"))
        assert e.tool_name == "my_tool"

    def test_execution_error_message_contains_exception_type(self):
        e = execution_error("my_tool", ValueError("bad value"))
        assert "ValueError" in e.message

    def test_execution_error_with_module(self):
        e = execution_error("my_tool", RuntimeError("oops"), module="search")
        assert e.module == "search"

    def test_execution_error_with_suggestion(self):
        e = execution_error(
            "my_tool", RuntimeError("oops"), suggestion="Check inputs"
        )
        assert e.suggestion == "Check inputs"

    def test_execution_error_default_module_empty(self):
        e = execution_error("tool", RuntimeError("oops"))
        assert e.module == ""
