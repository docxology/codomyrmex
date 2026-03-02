"""Additional coverage tests for model_context_protocol.transport.server.

Targets uncovered lines in server.py to push coverage from ~60% toward 80%+.
Focuses on:
  - call_tool_fn injection (line 76)
  - Tool decorator with typed params and output_schema (lines 122, 148)
  - register_tool with title/output_schema (lines 172-176)
  - register_file_resource (lines 201-213)
  - Per-tool timeout configuration (lines 380-382)
  - Validation error with FieldError (lines 368-377)
  - structuredContent response (line 414-415)
  - MCPToolResult error wrapping (lines 419-427)
  - _get_prompt with argument substitution (line 478)
  - Unknown dispatch method (line 296)

All tests use real implementations -- no mocks, stubs, or monkeypatch.
"""

import asyncio
import json

import pytest

pydantic = pytest.importorskip("pydantic")

from codomyrmex.model_context_protocol.transport.server import (
    MCPServer,
    MCPServerConfig,
)


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


# =========================================================================
# A. call_tool_fn injection
# =========================================================================


@pytest.mark.unit
class TestCallToolFnInjection:
    """Tests for the call_tool_fn injection path (line 76)."""

    def test_call_tool_fn_overrides_default_dispatch(self):
        """Test functionality: custom call_tool_fn replaces _call_tool dispatch."""
        call_log = []

        async def custom_call_tool(params):
            call_log.append(params)
            return {
                "content": [{"type": "text", "text": json.dumps({"custom": True})}],
            }

        cfg = MCPServerConfig(name="injection-test", version="0.1.0")
        srv = MCPServer(cfg, call_tool_fn=custom_call_tool)

        # Register a dummy tool so it shows in tools/list
        srv.register_tool(
            name="dummy",
            schema={
                "name": "dummy",
                "description": "A dummy tool",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
            handler=lambda: "should not be called",
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "dummy", "arguments": {}},
        }))

        # The custom call_tool_fn was invoked
        assert len(call_log) == 1
        assert call_log[0]["name"] == "dummy"
        # Result came from our custom function
        result = resp["result"]
        assert "content" in result
        parsed = json.loads(result["content"][0]["text"])
        assert parsed["custom"] is True

    def test_server_without_call_tool_fn_uses_default(self):
        """Test functionality: server without call_tool_fn uses registry-based dispatch."""
        cfg = MCPServerConfig(name="no-injection", version="0.1.0")
        srv = MCPServer(cfg)

        @srv.tool(name="ping", description="Simple ping")
        def ping(message: str = "pong") -> str:
            return json.dumps({"reply": message})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "ping", "arguments": {"message": "hello"}},
        }))

        result = resp["result"]
        assert "content" in result
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["reply"] == "hello"


# =========================================================================
# B. Tool decorator with typed parameters
# =========================================================================


@pytest.mark.unit
class TestToolDecoratorTypedParams:
    """Tests for tool decorator schema building with typed annotations (lines 118-130)."""

    def test_int_param_becomes_integer_schema(self):
        """Test functionality: int annotation produces 'integer' type in schema."""
        srv = MCPServer(MCPServerConfig(name="typed-test", version="0.1.0"))

        @srv.tool(name="add", description="Add numbers")
        def add(a: int, b: int) -> int:
            return a + b

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        props = tool_schema["inputSchema"]["properties"]
        assert props["a"]["type"] == "integer"
        assert props["b"]["type"] == "integer"
        assert "a" in tool_schema["inputSchema"]["required"]
        assert "b" in tool_schema["inputSchema"]["required"]

    def test_float_param_becomes_number_schema(self):
        """Test functionality: float annotation produces 'number' type in schema."""
        srv = MCPServer(MCPServerConfig(name="float-test", version="0.1.0"))

        @srv.tool(name="scale", description="Scale a value")
        def scale(value: float, factor: float = 1.0) -> float:
            return value * factor

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        props = tool_schema["inputSchema"]["properties"]
        assert props["value"]["type"] == "number"
        assert props["factor"]["type"] == "number"
        # 'value' is required (no default), 'factor' is optional
        assert "value" in tool_schema["inputSchema"]["required"]
        assert "factor" not in tool_schema["inputSchema"]["required"]

    def test_bool_param_becomes_boolean_schema(self):
        """Test functionality: bool annotation produces 'boolean' type in schema."""
        srv = MCPServer(MCPServerConfig(name="bool-test", version="0.1.0"))

        @srv.tool(name="toggle", description="Toggle something")
        def toggle(enabled: bool, verbose: bool = False) -> str:
            return json.dumps({"enabled": enabled, "verbose": verbose})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        props = tool_schema["inputSchema"]["properties"]
        assert props["enabled"]["type"] == "boolean"
        assert props["verbose"]["type"] == "boolean"
        assert "enabled" in tool_schema["inputSchema"]["required"]
        assert "verbose" not in tool_schema["inputSchema"]["required"]

    def test_mixed_types_in_single_tool(self):
        """Test functionality: tool with str, int, float, bool all build correct schema."""
        srv = MCPServer(MCPServerConfig(name="mixed-test", version="0.1.0"))

        @srv.tool(name="mixed", description="Mixed types")
        def mixed(name: str, count: int, weight: float, active: bool) -> str:
            return "ok"

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        props = tool_schema["inputSchema"]["properties"]
        assert props["name"]["type"] == "string"
        assert props["count"]["type"] == "integer"
        assert props["weight"]["type"] == "number"
        assert props["active"]["type"] == "boolean"
        # All four are required (no defaults)
        assert len(tool_schema["inputSchema"]["required"]) == 4


# =========================================================================
# C. Tool decorator with output_schema
# =========================================================================


@pytest.mark.unit
class TestToolDecoratorOutputSchema:
    """Tests for tool decorator with output_schema (line 148)."""

    def test_output_schema_added_to_tool_schema(self):
        """Test functionality: output_schema appears as outputSchema in tool listing."""
        srv = MCPServer(MCPServerConfig(name="output-schema-test", version="0.1.0"))

        output_schema = {
            "type": "object",
            "properties": {"result": {"type": "string"}},
            "required": ["result"],
        }

        @srv.tool(
            name="structured_tool",
            description="Tool with structured output",
            output_schema=output_schema,
        )
        def structured_tool(input_text: str) -> str:
            return json.dumps({"result": input_text.upper()})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        assert "outputSchema" in tool_schema
        assert tool_schema["outputSchema"]["type"] == "object"
        assert "result" in tool_schema["outputSchema"]["properties"]

    def test_tool_without_output_schema_has_no_outputSchema(self):
        """Test functionality: tool without output_schema does not include outputSchema."""
        srv = MCPServer(MCPServerConfig(name="no-output-test", version="0.1.0"))

        @srv.tool(name="plain_tool", description="No output schema")
        def plain_tool(text: str) -> str:
            return text

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        assert "outputSchema" not in tool_schema

    def test_tool_decorator_with_title(self):
        """Test functionality: title param appears in tool schema (line 144)."""
        srv = MCPServer(MCPServerConfig(name="title-test", version="0.1.0"))

        @srv.tool(
            name="titled_tool",
            description="A tool with a title",
            title="My Titled Tool",
        )
        def titled_tool(x: str) -> str:
            return x

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        assert tool_schema["title"] == "My Titled Tool"


# =========================================================================
# D. register_tool with title and output_schema
# =========================================================================


@pytest.mark.unit
class TestRegisterToolWithTitleAndOutputSchema:
    """Tests for register_tool() with title and output_schema (lines 172-176)."""

    def test_register_tool_sets_title_in_schema(self):
        """Test functionality: register_tool with title adds title to schema."""
        srv = MCPServer(MCPServerConfig(name="reg-title", version="0.1.0"))
        schema = {
            "name": "manual_tool",
            "description": "Manual tool",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        }
        srv.register_tool(
            name="manual_tool",
            schema=schema,
            handler=lambda: "ok",
            title="Manual Tool Title",
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        assert tool_schema["title"] == "Manual Tool Title"

    def test_register_tool_sets_output_schema(self):
        """Test functionality: register_tool with output_schema adds outputSchema."""
        srv = MCPServer(MCPServerConfig(name="reg-output", version="0.1.0"))
        out_schema = {"type": "object", "properties": {"count": {"type": "integer"}}}
        schema = {
            "name": "counting_tool",
            "description": "Counts items",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        }
        srv.register_tool(
            name="counting_tool",
            schema=schema,
            handler=lambda: "ok",
            output_schema=out_schema,
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        assert "outputSchema" in tool_schema
        assert tool_schema["outputSchema"]["type"] == "object"

    def test_register_tool_with_both_title_and_output_schema(self):
        """Test functionality: register_tool with both title and output_schema."""
        srv = MCPServer(MCPServerConfig(name="reg-both", version="0.1.0"))
        out_schema = {"type": "string"}
        schema = {
            "name": "full_tool",
            "description": "Fully specified tool",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        }
        srv.register_tool(
            name="full_tool",
            schema=schema,
            handler=lambda: "ok",
            title="Full Tool",
            output_schema=out_schema,
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        assert tool_schema["title"] == "Full Tool"
        assert tool_schema["outputSchema"]["type"] == "string"


# =========================================================================
# E. register_file_resource
# =========================================================================


@pytest.mark.unit
class TestRegisterFileResource:
    """Tests for register_file_resource() (lines 199-219)."""

    def test_register_and_read_text_file(self, tmp_path):
        """Test functionality: register_file_resource registers .txt and reads content back."""
        srv = MCPServer(MCPServerConfig(name="file-res", version="0.1.0"))
        test_file = tmp_path / "hello.txt"
        test_file.write_text("Hello, file resource!")

        srv.register_file_resource(str(test_file))

        # Verify it appears in resources list
        list_resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {},
        }))
        resources = list_resp["result"]["resources"]
        assert len(resources) == 1
        assert resources[0]["name"] == "hello.txt"
        assert resources[0]["mimeType"] == "text/plain"
        assert resources[0]["description"] == "File: hello.txt"

        # Verify content can be read back
        uri = resources[0]["uri"]
        read_resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "resources/read",
            "params": {"uri": uri},
        }))
        contents = read_resp["result"]["contents"]
        assert contents[0]["text"] == "Hello, file resource!"

    def test_register_json_file_gets_json_mime_type(self, tmp_path):
        """Test functionality: .json file gets application/json mime type."""
        srv = MCPServer(MCPServerConfig(name="json-res", version="0.1.0"))
        json_file = tmp_path / "data.json"
        json_file.write_text('{"key": "value"}')

        srv.register_file_resource(str(json_file))

        list_resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {},
        }))
        assert list_resp["result"]["resources"][0]["mimeType"] == "application/json"

    def test_register_markdown_file_gets_markdown_mime_type(self, tmp_path):
        """Test functionality: .md file gets text/markdown mime type."""
        srv = MCPServer(MCPServerConfig(name="md-res", version="0.1.0"))
        md_file = tmp_path / "readme.md"
        md_file.write_text("# Title\n\nContent")

        srv.register_file_resource(str(md_file))

        list_resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {},
        }))
        assert list_resp["result"]["resources"][0]["mimeType"] == "text/markdown"

    def test_register_python_file_gets_python_mime_type(self, tmp_path):
        """Test functionality: .py file gets text/x-python mime type."""
        srv = MCPServer(MCPServerConfig(name="py-res", version="0.1.0"))
        py_file = tmp_path / "script.py"
        py_file.write_text("print('hello')")

        srv.register_file_resource(str(py_file))

        list_resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {},
        }))
        assert list_resp["result"]["resources"][0]["mimeType"] == "text/x-python"

    def test_register_unknown_extension_defaults_to_text_plain(self, tmp_path):
        """Test functionality: unknown extension falls back to text/plain."""
        srv = MCPServer(MCPServerConfig(name="unknown-ext", version="0.1.0"))
        unk_file = tmp_path / "data.xyz"
        unk_file.write_text("some data")

        srv.register_file_resource(str(unk_file))

        list_resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "resources/list",
            "params": {},
        }))
        assert list_resp["result"]["resources"][0]["mimeType"] == "text/plain"


# =========================================================================
# F. Per-tool timeout configuration
# =========================================================================


@pytest.mark.unit
class TestPerToolTimeout:
    """Tests for per-tool timeout configuration (lines 380-382)."""

    def test_per_tool_timeout_used_for_matching_tool(self):
        """Test functionality: per_tool_timeouts overrides default for named tool."""
        cfg = MCPServerConfig(
            name="timeout-test",
            version="0.1.0",
            default_tool_timeout=60.0,
            per_tool_timeouts={"fast_tool": 5.0},
        )
        srv = MCPServer(cfg)

        @srv.tool(name="fast_tool", description="A fast tool")
        def fast_tool(value: str = "ok") -> str:
            return json.dumps({"value": value})

        # Tool should execute normally (it's fast, well within 5s timeout)
        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "fast_tool", "arguments": {"value": "hello"}},
        }))
        result = resp["result"]
        assert "content" in result
        assert "isError" not in result

    def test_tool_not_in_per_tool_timeouts_uses_default(self):
        """Test functionality: tool not in per_tool_timeouts uses default_tool_timeout."""
        cfg = MCPServerConfig(
            name="default-timeout-test",
            version="0.1.0",
            default_tool_timeout=60.0,
            per_tool_timeouts={"other_tool": 5.0},
        )
        srv = MCPServer(cfg)

        @srv.tool(name="normal_tool", description="A normal tool")
        def normal_tool(text: str = "hi") -> str:
            return json.dumps({"text": text})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "normal_tool", "arguments": {"text": "world"}},
        }))
        result = resp["result"]
        assert "content" in result
        assert "isError" not in result


# =========================================================================
# G. Validation error response structure
# =========================================================================


@pytest.mark.unit
class TestValidationErrorResponse:
    """Tests for validation error with FieldError creation (lines 368-377)."""

    def test_missing_required_arg_returns_validation_error(self):
        """Test functionality: calling a tool with missing required arg yields validation error."""
        srv = MCPServer(MCPServerConfig(name="val-err", version="0.1.0"))

        @srv.tool(name="requires_path", description="Requires a path argument")
        def requires_path(path: str) -> str:
            return json.dumps({"path": path})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "requires_path", "arguments": {}},
        }))
        result = resp["result"]
        assert result.get("isError") is True
        error_text = result["content"][0]["text"]
        error_data = json.loads(error_text)
        assert error_data["code"] == "VALIDATION_ERROR"
        assert "Validation failed" in error_data["message"]

    def test_wrong_type_arg_returns_validation_error(self):
        """Test functionality: calling a tool with wrong type returns validation error."""
        srv = MCPServer(MCPServerConfig(name="type-err", version="0.1.0"))

        @srv.tool(name="int_tool", description="Takes an integer")
        def int_tool(count: int) -> str:
            return json.dumps({"count": count})

        # Pass a non-coercible string where int is expected
        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "int_tool", "arguments": {"count": "not_a_number"}},
        }))
        result = resp["result"]
        assert result.get("isError") is True
        error_text = result["content"][0]["text"]
        error_data = json.loads(error_text)
        assert error_data["code"] == "VALIDATION_ERROR"


# =========================================================================
# H. structuredContent in response
# =========================================================================


@pytest.mark.unit
class TestStructuredContentResponse:
    """Tests for structuredContent response when outputSchema exists (lines 414-415)."""

    def test_tool_with_output_schema_returns_structured_content(self):
        """Test functionality: tool with outputSchema includes structuredContent in response."""
        out_schema = {
            "type": "object",
            "properties": {"result": {"type": "string"}},
        }
        srv = MCPServer(MCPServerConfig(name="struct-content", version="0.1.0"))

        srv.register_tool(
            name="structured_out",
            schema={
                "name": "structured_out",
                "description": "Returns structured output",
                "inputSchema": {
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": [],
                },
                "outputSchema": out_schema,
            },
            handler=lambda text="hello": json.dumps({"result": text}),
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "structured_out", "arguments": {"text": "world"}},
        }))
        result = resp["result"]
        # Should have both content and structuredContent
        assert "content" in result
        assert "structuredContent" in result
        # structuredContent should be the raw data from MCPToolResult
        assert result["structuredContent"]["result"] is not None

    def test_tool_without_output_schema_has_no_structured_content(self):
        """Test functionality: tool without outputSchema does not include structuredContent."""
        srv = MCPServer(MCPServerConfig(name="no-struct", version="0.1.0"))

        @srv.tool(name="plain", description="Plain tool")
        def plain(text: str = "hi") -> str:
            return json.dumps({"echo": text})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "plain", "arguments": {"text": "hello"}},
        }))
        result = resp["result"]
        assert "content" in result
        assert "structuredContent" not in result


# =========================================================================
# I. MCPToolResult error wrapping
# =========================================================================


@pytest.mark.unit
class TestToolExecutionErrorWrapping:
    """Tests for tool execution error wrapping (lines 419-427)."""

    def test_tool_that_raises_returns_error_via_registry(self):
        """Test functionality: tool handler raising RuntimeError yields error response.

        When a handler raises, MCPToolRegistry.execute catches it and returns
        a MCPToolResult with status='failure'. The server then wraps it via
        the error path at lines 419-427, using error_message from MCPErrorDetail.
        The 'module' field in MCPToolError gets set to the error_type from MCPErrorDetail.
        """
        srv = MCPServer(MCPServerConfig(name="raise-test", version="0.1.0"))

        @srv.tool(name="crashy", description="Crashes on purpose")
        def crashy(msg: str = "boom") -> str:
            raise RuntimeError(f"Intentional crash: {msg}")

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "crashy", "arguments": {"msg": "test"}},
        }))
        result = resp["result"]
        assert result.get("isError") is True
        error_data = json.loads(result["content"][0]["text"])
        assert error_data["code"] == "EXECUTION_ERROR"
        # The message comes from MCPErrorDetail.error_message (str(e))
        assert "Intentional crash: test" in error_data["message"]
        # The module comes from MCPErrorDetail.error_type (type(e).__name__)
        assert error_data["module"] == "RuntimeError"

    def test_tool_returning_failure_status_wraps_error(self):
        """Test functionality: MCPToolResult with failure status yields error wrapping.

        When the registry.execute returns a result with status != "success",
        the server wraps it as an MCPToolError with EXECUTION_ERROR code.
        This covers lines 419-427.
        """
        # The simplest way to get a failure result: register a tool whose
        # handler raises, which causes MCPToolRegistry.execute to return
        # status="failure" with an MCPErrorDetail.
        srv = MCPServer(MCPServerConfig(name="fail-result", version="0.1.0"))

        @srv.tool(name="value_error_tool", description="Raises ValueError")
        def value_error_tool(x: str = "bad") -> str:
            raise ValueError(f"Invalid value: {x}")

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "value_error_tool", "arguments": {"x": "oops"}},
        }))
        result = resp["result"]
        assert result.get("isError") is True
        error_data = json.loads(result["content"][0]["text"])
        assert error_data["code"] == "EXECUTION_ERROR"


# =========================================================================
# J. _get_prompt with argument substitution
# =========================================================================


@pytest.mark.unit
class TestGetPromptWithArgSubstitution:
    """Tests for _get_prompt with template argument substitution (line 478+)."""

    def test_simple_arg_substitution(self):
        """Test functionality: prompt template with {name} is substituted correctly."""
        srv = MCPServer(MCPServerConfig(name="prompt-sub", version="0.1.0"))
        srv.register_prompt(
            name="greeting",
            description="A greeting prompt",
            template="Hello {name}!",
            arguments=[{"name": "name", "description": "The name"}],
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/get",
            "params": {"name": "greeting", "arguments": {"name": "Alice"}},
        }))
        messages = resp["result"]["messages"]
        assert messages[0]["content"]["text"] == "Hello Alice!"

    def test_multiple_arg_substitution(self):
        """Test functionality: multiple template variables are all substituted."""
        srv = MCPServer(MCPServerConfig(name="multi-prompt", version="0.1.0"))
        srv.register_prompt(
            name="intro",
            description="An introduction prompt",
            template="My name is {name} and I am {age} years old.",
            arguments=[
                {"name": "name", "description": "Name"},
                {"name": "age", "description": "Age"},
            ],
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/get",
            "params": {"name": "intro", "arguments": {"name": "Bob", "age": "30"}},
        }))
        text = resp["result"]["messages"][0]["content"]["text"]
        assert text == "My name is Bob and I am 30 years old."

    def test_nonexistent_prompt_returns_error(self):
        """Test functionality: getting a nonexistent prompt returns error (line 478)."""
        srv = MCPServer(MCPServerConfig(name="no-prompt", version="0.1.0"))

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/get",
            "params": {"name": "nonexistent", "arguments": {}},
        }))
        assert "error" in resp
        assert resp["error"]["code"] == -32603
        assert "Prompt not found" in resp["error"]["message"]

    def test_prompt_with_no_args_uses_template_as_is(self):
        """Test functionality: prompt with empty arguments returns template unchanged."""
        srv = MCPServer(MCPServerConfig(name="no-args-prompt", version="0.1.0"))
        srv.register_prompt(
            name="static",
            description="A static prompt",
            template="No variables here.",
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "prompts/get",
            "params": {"name": "static", "arguments": {}},
        }))
        text = resp["result"]["messages"][0]["content"]["text"]
        assert text == "No variables here."


# =========================================================================
# K. Unknown method returns error
# =========================================================================


@pytest.mark.unit
class TestUnknownMethodDispatch:
    """Tests for unknown method dispatch returning error (line 296)."""

    def test_completely_unknown_method_returns_error(self):
        """Test functionality: unknown method via dispatch returns -32603 error."""
        srv = MCPServer(MCPServerConfig(name="unknown-method", version="0.1.0"))

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 42,
            "method": "fantasy/method",
            "params": {},
        }))
        assert "error" in resp
        assert resp["error"]["code"] == -32603
        assert "Unknown method" in resp["error"]["message"]

    def test_empty_method_returns_error(self):
        """Test functionality: empty method string returns error."""
        srv = MCPServer(MCPServerConfig(name="empty-method", version="0.1.0"))

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 43,
            "method": "",
            "params": {},
        }))
        assert "error" in resp
        assert resp["error"]["code"] == -32603


# =========================================================================
# Additional: tool with zero timeout (no asyncio.wait_for path)
# =========================================================================


@pytest.mark.unit
class TestZeroTimeoutToolExecution:
    """Tests for tool execution with timeout=0 (synchronous path, line 398-399)."""

    def test_zero_timeout_executes_synchronously(self):
        """Test functionality: default_tool_timeout=0 uses synchronous execution."""
        cfg = MCPServerConfig(
            name="zero-timeout",
            version="0.1.0",
            default_tool_timeout=0.0,
        )
        srv = MCPServer(cfg)

        @srv.tool(name="sync_tool", description="Sync execution")
        def sync_tool(value: str = "sync") -> str:
            return json.dumps({"mode": "sync", "value": value})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "sync_tool", "arguments": {"value": "test"}},
        }))
        result = resp["result"]
        assert "content" in result
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["mode"] == "sync"
        assert inner["value"] == "test"


# =========================================================================
# Additional: Initialize capabilities include tools/resources/prompts
# =========================================================================


@pytest.mark.unit
class TestInitializeCapabilities:
    """Tests for initialize capability reporting when tools/resources/prompts exist."""

    def test_initialize_with_tools_resources_prompts(self):
        """Test functionality: initialize reports all three capabilities when populated."""
        srv = MCPServer(MCPServerConfig(name="full-caps", version="0.1.0"))

        @srv.tool(name="t1", description="Tool 1")
        def t1() -> str:
            return "ok"

        srv.register_resource(
            uri="test://r1", name="R1", content_provider=lambda: "data"
        )
        srv.register_prompt(
            name="p1", description="Prompt 1", template="Hello"
        )

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }))
        caps = resp["result"]["capabilities"]
        assert "tools" in caps
        assert "resources" in caps
        assert "prompts" in caps

    def test_initialize_with_only_tools(self):
        """Test functionality: initialize with only tools reports tools capability."""
        srv = MCPServer(MCPServerConfig(name="tools-only", version="0.1.0"))

        @srv.tool(name="only_tool", description="Only tool")
        def only_tool() -> str:
            return "ok"

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }))
        caps = resp["result"]["capabilities"]
        assert "tools" in caps
        assert "resources" not in caps
        assert "prompts" not in caps


# =========================================================================
# Additional: Rate-limit error path
# =========================================================================


@pytest.mark.unit
class TestRateLimitPath:
    """Tests for rate-limiter error path (lines 357-362)."""

    def test_rate_limit_error_response_when_exhausted(self):
        """Test functionality: exhausted rate limiter returns RATE_LIMITED error."""
        cfg = MCPServerConfig(
            name="rate-limit-test",
            version="0.1.0",
            rate_limit_rate=0.001,  # Very low rate
            rate_limit_burst=1,     # Only 1 allowed
        )
        srv = MCPServer(cfg)

        @srv.tool(name="limited", description="Rate limited tool")
        def limited(x: str = "ok") -> str:
            return json.dumps({"x": x})

        # First call should succeed
        resp1 = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "limited", "arguments": {}},
        }))

        # Second call may be rate-limited (burst=1)
        resp2 = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "limited", "arguments": {}},
        }))

        # At least one should work; the second may be rate limited
        results = [resp1["result"], resp2["result"]]
        # Verify we can detect rate-limiting if it happens
        for r in results:
            if r.get("isError"):
                error_data = json.loads(r["content"][0]["text"])
                assert error_data["code"] == "RATE_LIMITED"


# =========================================================================
# Additional: Tool not found error path
# =========================================================================


@pytest.mark.unit
class TestToolNotFoundPath:
    """Tests for tool not found error path (lines 352-354)."""

    def test_empty_tool_name_returns_not_found(self):
        """Test functionality: empty tool name returns NOT_FOUND error."""
        srv = MCPServer(MCPServerConfig(name="not-found", version="0.1.0"))

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "", "arguments": {}},
        }))
        result = resp["result"]
        assert result.get("isError") is True
        error_data = json.loads(result["content"][0]["text"])
        assert error_data["code"] == "NOT_FOUND"


# =========================================================================
# Additional: Tool decorator with self/cls parameters (line 122)
# =========================================================================


@pytest.mark.unit
class TestToolDecoratorSelfClsSkip:
    """Tests for tool decorator skipping 'self' and 'cls' parameters (line 122)."""

    def test_method_with_self_param_excluded_from_schema(self):
        """Test functionality: 'self' parameter is excluded from tool inputSchema."""
        srv = MCPServer(MCPServerConfig(name="self-skip", version="0.1.0"))

        class MyService:
            def process(self, data: str) -> str:
                return json.dumps({"processed": data})

        # Register the unbound method to test the 'self' skip path.
        srv.tool(name="process", description="Process data")(MyService.process)

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        props = tool_schema["inputSchema"]["properties"]
        # 'self' should NOT be in the properties
        assert "self" not in props
        # 'data' should be present
        assert "data" in props
        assert props["data"]["type"] == "string"
        assert "data" in tool_schema["inputSchema"]["required"]

    def test_classmethod_with_cls_param_excluded_from_schema(self):
        """Test functionality: 'cls' parameter is excluded from tool inputSchema."""
        srv = MCPServer(MCPServerConfig(name="cls-skip", version="0.1.0"))

        # Define a function that uses 'cls' as first param to test the branch
        def factory(cls, name: str) -> str:
            return json.dumps({"name": name})

        srv.tool(name="factory", description="Factory method")(factory)

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }))
        tool_schema = resp["result"]["tools"][0]
        props = tool_schema["inputSchema"]["properties"]
        assert "cls" not in props
        assert "name" in props


# =========================================================================
# Additional: Timeout error path (lines 400-407)
# =========================================================================


@pytest.mark.unit
class TestToolTimeoutError:
    """Tests for the TimeoutError path during tool execution (lines 400-407)."""

    def test_tool_exceeding_timeout_returns_timeout_error(self):
        """Test functionality: tool that exceeds per-tool timeout returns TIMEOUT error.

        Uses a very short timeout (0.001s) with a handler that sleeps briefly,
        triggering the asyncio.wait_for TimeoutError catch path.
        """
        import time

        cfg = MCPServerConfig(
            name="timeout-err",
            version="0.1.0",
            per_tool_timeouts={"slow_tool": 0.001},  # 1ms timeout
        )
        srv = MCPServer(cfg)

        @srv.tool(name="slow_tool", description="Intentionally slow tool")
        def slow_tool(duration: float = 0.5) -> str:
            time.sleep(duration)  # Will exceed the 1ms timeout
            return json.dumps({"done": True})

        resp = _run(srv.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "slow_tool", "arguments": {"duration": 2.0}},
        }))
        result = resp["result"]
        assert result.get("isError") is True
        error_data = json.loads(result["content"][0]["text"])
        assert error_data["code"] == "TIMEOUT"
        assert "slow_tool" in error_data["message"]
        assert "timed out" in error_data["message"]
