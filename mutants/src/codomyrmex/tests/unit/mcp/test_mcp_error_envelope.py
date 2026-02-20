"""Tests for MCPToolError structured error envelope.

All zero-mock — validates serialisation, deserialisation, MCP response
format, error code coverage, and backward compatibility.
"""

import json

import pytest

from codomyrmex.model_context_protocol.errors import (
    MCPErrorCode,
    MCPToolError,
    FieldError,
    validation_error,
    not_found_error,
    timeout_error,
    execution_error,
)


# ── MCPToolError basics ──────────────────────────────────────────────

class TestMCPToolError:
    """Core dataclass behaviour."""

    def test_create_with_defaults(self):
        err = MCPToolError(code=MCPErrorCode.INTERNAL, message="boom")
        assert err.code == MCPErrorCode.INTERNAL
        assert err.message == "boom"
        assert len(err.correlation_id) == 12

    def test_correlation_id_unique(self):
        ids = {MCPToolError(code=MCPErrorCode.INTERNAL, message="x").correlation_id for _ in range(20)}
        assert len(ids) == 20, "correlation_ids should be unique"

    def test_all_error_codes(self):
        """Every MCPErrorCode can be used to construct a valid MCPToolError."""
        for code in MCPErrorCode:
            err = MCPToolError(code=code, message=f"test {code.value}")
            assert err.code == code


# ── Serialisation round-trip ─────────────────────────────────────────

class TestSerialisation:
    """JSON serialisation / deserialisation."""

    def test_to_dict_minimal(self):
        err = MCPToolError(code=MCPErrorCode.TIMEOUT, message="slow", correlation_id="abc123")
        d = err.to_dict()
        assert d["code"] == "TIMEOUT"
        assert d["message"] == "slow"
        assert d["correlation_id"] == "abc123"
        assert "tool_name" not in d  # empty string omitted

    def test_to_dict_full(self):
        err = MCPToolError(
            code=MCPErrorCode.VALIDATION_ERROR,
            message="bad input",
            tool_name="codomyrmex.read_file",
            module="file_io",
            field_errors=[FieldError(field="path", constraint="required", value=None)],
            suggestion="Provide a valid file path",
            correlation_id="xyz",
        )
        d = err.to_dict()
        assert d["tool_name"] == "codomyrmex.read_file"
        assert d["module"] == "file_io"
        assert len(d["field_errors"]) == 1
        assert d["field_errors"][0]["field"] == "path"
        assert d["suggestion"] == "Provide a valid file path"

    def test_to_json_roundtrip(self):
        err = MCPToolError(
            code=MCPErrorCode.EXECUTION_ERROR,
            message="RuntimeError: fail",
            tool_name="tool.x",
            correlation_id="rnd",
        )
        text = err.to_json()
        restored = MCPToolError.from_json(text)
        assert restored.code == err.code
        assert restored.message == err.message
        assert restored.tool_name == err.tool_name
        assert restored.correlation_id == err.correlation_id

    def test_from_dict(self):
        d = {"code": "NOT_FOUND", "message": "nope", "correlation_id": "abc"}
        err = MCPToolError.from_dict(d)
        assert err.code == MCPErrorCode.NOT_FOUND
        assert err.message == "nope"

    def test_field_error_serialises(self):
        fe = FieldError(field="count", constraint="minimum 1", value=-5)
        d = fe.to_dict()
        assert d["field"] == "count"
        assert d["value"] == -5


# ── MCP response format ─────────────────────────────────────────────

class TestMCPResponse:
    """Compatibility with MCP ``isError: true`` protocol."""

    def test_to_mcp_response_shape(self):
        err = MCPToolError(code=MCPErrorCode.RATE_LIMITED, message="slow down")
        resp = err.to_mcp_response()
        assert resp["isError"] is True
        assert len(resp["content"]) == 1
        assert resp["content"][0]["type"] == "text"
        # Content text should be valid JSON containing our error
        parsed = json.loads(resp["content"][0]["text"])
        assert parsed["code"] == "RATE_LIMITED"

    def test_from_mcp_response_structured(self):
        err = MCPToolError(code=MCPErrorCode.CIRCUIT_OPEN, message="circuit open")
        resp = err.to_mcp_response()
        restored = MCPToolError.from_mcp_response(resp)
        assert restored is not None
        assert restored.code == MCPErrorCode.CIRCUIT_OPEN

    def test_from_mcp_response_legacy_unstructured(self):
        """Old-style isError responses without JSON get wrapped as INTERNAL."""
        legacy = {"content": [{"type": "text", "text": "plain error message"}], "isError": True}
        restored = MCPToolError.from_mcp_response(legacy)
        assert restored is not None
        assert restored.code == MCPErrorCode.INTERNAL
        assert "plain error message" in restored.message

    def test_from_mcp_response_non_error_returns_none(self):
        success = {"content": [{"type": "text", "text": "ok"}]}
        assert MCPToolError.from_mcp_response(success) is None


# ── Convenience constructors ─────────────────────────────────────────

class TestConvenienceConstructors:

    def test_validation_error(self):
        err = validation_error("tool.a", "bad args", [FieldError("x", "required")])
        assert err.code == MCPErrorCode.VALIDATION_ERROR
        assert err.tool_name == "tool.a"
        assert len(err.field_errors) == 1

    def test_not_found_error(self):
        err = not_found_error("tool.missing")
        assert err.code == MCPErrorCode.NOT_FOUND
        assert "tool.missing" in err.message

    def test_timeout_error(self):
        err = timeout_error("slow_tool", 30.0)
        assert err.code == MCPErrorCode.TIMEOUT
        assert "30" in err.message

    def test_execution_error(self):
        err = execution_error(
            "tool.crash",
            RuntimeError("kaboom"),
            module="core",
            suggestion="Check logs",
        )
        assert err.code == MCPErrorCode.EXECUTION_ERROR
        assert "RuntimeError" in err.message
        assert "kaboom" in err.message
        assert err.module == "core"
        assert err.suggestion == "Check logs"
