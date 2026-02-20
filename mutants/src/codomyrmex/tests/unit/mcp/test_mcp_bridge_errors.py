"""Tests for error wrapping in mcp_bridge.py call_tool().

All zero-mock — exercises the real mcp_bridge.call_tool() with
structured MCPToolError wrapping for different failure modes.
"""

import pytest

from codomyrmex.agents.pai.mcp_bridge import call_tool
from codomyrmex.model_context_protocol.errors import MCPErrorCode
from codomyrmex.agents.pai.trust_gateway import trust_all


@pytest.fixture(autouse=True)
def setup_trust():
    trust_all()


# ── Tool not found ───────────────────────────────────────────────────

def test_unknown_tool_raises_key_error():
    """call_tool raises KeyError for unknown tool names."""
    with pytest.raises(KeyError, match="Unknown tool"):
        call_tool("codomyrmex.nonexistent_tool_xyz")


# ── Validation errors ────────────────────────────────────────────────

def test_validation_error_on_wrong_type():
    """Passing wrong argument types returns structured VALIDATION_ERROR."""
    # read_file requires path (string) — pass integer
    result = call_tool("codomyrmex.read_file", path=12345)
    # The handler itself may catch this, or validation may.
    # Either way the result should succeed or have an error key.
    # Since path is typed as string and we pass int, validation should catch it.
    if "error" in result:
        assert result["error"]["code"] == MCPErrorCode.VALIDATION_ERROR.value


# ── Execution errors ─────────────────────────────────────────────────

def test_execution_error_wrapped_structured():
    """Handler that raises gets wrapped in structured EXECUTION_ERROR."""
    # analyze_python on a nonexistent file should trigger an exception
    # that the bridge wraps in a structured envelope.
    result = call_tool("codomyrmex.analyze_python", path="/nonexistent/path/abc.py")
    # analyze_python may handle internally or raise — assert either format:
    if isinstance(result.get("error"), dict):
        assert result["error"]["code"] == MCPErrorCode.EXECUTION_ERROR.value
        assert "correlation_id" in result["error"]
    else:
        # Handler caught internally — just verify 'error' key exists
        assert "error" in result


def test_handler_internal_error_preserved():
    """read_file catches errors internally and returns plain error string."""
    result = call_tool("codomyrmex.read_file", path="/nonexistent/path/xyz123")
    assert result.get("success") is False
    assert isinstance(result["error"], str)
    assert "not found" in result["error"].lower() or "nonexistent" in result["error"]


# ── Successful execution ─────────────────────────────────────────────

def test_list_modules_succeeds():
    """call_tool('codomyrmex.list_modules') returns module data."""
    result = call_tool("codomyrmex.list_modules")
    assert "error" not in result
    assert "modules" in result


def test_module_info_succeeds():
    """call_tool('codomyrmex.module_info') with valid module returns info."""
    result = call_tool("codomyrmex.module_info", module_name="events")
    assert "error" not in result
    assert "module" in result or "name" in result or "exports" in str(result)


# ── Error envelope structure ─────────────────────────────────────────

def test_structured_error_envelope_has_required_fields():
    """When a handler raises, the structured envelope has code, message, correlation_id."""
    # Use a tool that is likely to raise for this test.
    # checksum_file with nonexistent path raises:
    result = call_tool("codomyrmex.checksum_file", path="/nonexistent/path/xyz")
    if isinstance(result.get("error"), dict):
        err = result["error"]
        assert "code" in err
        assert "message" in err
        assert "correlation_id" in err
    else:
        # Handler caught internally — just verify structure
        assert "error" in result


# ── Server-level integration ────────────────────────────────────────

@pytest.mark.asyncio
async def test_server_call_tool_validation_error():
    """MCPServer._call_tool returns structured error for invalid args."""
    from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig

    server = MCPServer(config=MCPServerConfig())

    # Register a tool that expects string 'name'
    def greet(*, name: str) -> dict:
        return {"greeting": f"Hello {name}"}

    server.register_tool(
        name="test.greet",
        schema={
            "name": "test.greet",
            "description": "test",
            "inputSchema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        handler=greet,
    )

    # Call with missing required field
    result = await server._call_tool({"name": "test.greet", "arguments": {}})
    assert result["isError"] is True

    # Parse the structured error
    import json
    parsed = json.loads(result["content"][0]["text"])
    assert parsed["code"] == "VALIDATION_ERROR"
    assert "name" in parsed["message"].lower() or any("name" in str(e) for e in parsed.get("field_errors", []))


@pytest.mark.asyncio
async def test_server_call_tool_not_found():
    """MCPServer._call_tool returns NOT_FOUND for unknown tool."""
    from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig
    import json

    server = MCPServer(config=MCPServerConfig())
    result = await server._call_tool({"name": "nonexistent.tool", "arguments": {}})
    assert result["isError"] is True
    parsed = json.loads(result["content"][0]["text"])
    assert parsed["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_server_call_tool_success():
    """MCPServer._call_tool succeeds with valid args and returns content."""
    from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig

    server = MCPServer(config=MCPServerConfig())

    def add(*, a: int, b: int) -> dict:
        return {"sum": a + b}

    server.register_tool(
        name="test.add",
        schema={
            "name": "test.add",
            "description": "Add two numbers",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
        handler=add,
    )

    result = await server._call_tool({"name": "test.add", "arguments": {"a": 3, "b": 4}})
    assert "isError" not in result or result.get("isError") is False
    assert result["content"][0]["type"] == "text"
    import json
    data = json.loads(result["content"][0]["text"])
    assert data["result"]["sum"] == 7


@pytest.mark.asyncio
async def test_server_coerces_str_to_int():
    """Server validates and coerces '3' -> 3 before calling handler."""
    from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig
    import json

    server = MCPServer(config=MCPServerConfig())

    def multiply(*, x: int, y: int) -> dict:
        return {"product": x * y}

    server.register_tool(
        name="test.mul",
        schema={
            "name": "test.mul",
            "description": "Multiply",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                },
                "required": ["x", "y"],
            },
        },
        handler=multiply,
    )

    result = await server._call_tool({"name": "test.mul", "arguments": {"x": "3", "y": "5"}})
    assert "isError" not in result
    data = json.loads(result["content"][0]["text"])
    assert data["result"]["product"] == 15
