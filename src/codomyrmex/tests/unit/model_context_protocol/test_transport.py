"""Tests for model_context_protocol.transport — server, client config, and errors module.

Tests the MCPServer JSON-RPC handling, MCPServerConfig defaults,
MCPClientConfig defaults, MCPClientError, and the structured error
types from errors.py (MCPToolError, FieldError, MCPErrorCode, convenience
constructors).
All tests use real object construction — no mocks.
"""

import asyncio
import json

import pytest

pydantic = pytest.importorskip("pydantic")

from codomyrmex.model_context_protocol.errors import (  # noqa: E402
    FieldError,
    MCPErrorCode,
    MCPToolError,
    execution_error,
    not_found_error,
    timeout_error,
    validation_error,
)
from codomyrmex.model_context_protocol.transport.client import (  # noqa: E402
    MCPClientConfig,
    MCPClientError,
)
from codomyrmex.model_context_protocol.transport.server import (  # noqa: E402
    MCPServer,
    MCPServerConfig,
)


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)


# =========================================================================
# MCPServerConfig tests
# =========================================================================


@pytest.mark.unit
class TestMCPServerConfig:
    """Tests for MCPServerConfig defaults and customization."""

    def test_default_config_values(self):
        cfg = MCPServerConfig()
        assert cfg.name == "codomyrmex-mcp-server"
        assert cfg.version == "1.0.0"
        assert cfg.transport == "stdio"
        assert cfg.log_level == "INFO"
        assert cfg.default_tool_timeout == 60.0
        assert cfg.per_tool_timeouts is None
        assert cfg.rate_limit_rate == 50.0
        assert cfg.rate_limit_burst == 100
        assert cfg.warm_up is True

    def test_custom_config_values(self):
        cfg = MCPServerConfig(
            name="test-server",
            version="2.0.0",
            transport="http",
            default_tool_timeout=30.0,
            per_tool_timeouts={"slow_tool": 120.0},
        )
        assert cfg.name == "test-server"
        assert cfg.version == "2.0.0"
        assert cfg.transport == "http"
        assert cfg.default_tool_timeout == 30.0
        assert cfg.per_tool_timeouts["slow_tool"] == 120.0


# =========================================================================
# MCPClientConfig tests
# =========================================================================


@pytest.mark.unit
class TestMCPClientConfig:
    """Tests for MCPClientConfig defaults and customization."""

    def test_default_client_config(self):
        cfg = MCPClientConfig()
        assert cfg.name == "codomyrmex-mcp-client"
        assert cfg.version == "0.1.0"
        assert cfg.timeout_seconds == 30.0
        assert cfg.protocol_version == "2025-06-18"
        assert cfg.max_retries == 3
        assert cfg.retry_delay == 0.5
        assert cfg.health_check_interval == 0.0
        assert cfg.connection_pool_size == 10

    def test_custom_client_config(self):
        cfg = MCPClientConfig(
            name="test-client",
            timeout_seconds=10.0,
            max_retries=5,
            connection_pool_size=20,
        )
        assert cfg.name == "test-client"
        assert cfg.timeout_seconds == 10.0
        assert cfg.max_retries == 5
        assert cfg.connection_pool_size == 20


# =========================================================================
# MCPClientError tests
# =========================================================================


@pytest.mark.unit
class TestMCPClientError:
    """Tests for MCPClientError exception class."""

    def test_client_error_is_exception(self):
        assert issubclass(MCPClientError, Exception)

    def test_client_error_message(self):
        err = MCPClientError("Connection failed")
        assert str(err) == "Connection failed"

    def test_client_error_can_be_raised_and_caught(self):
        with pytest.raises(MCPClientError, match="timeout"):
            raise MCPClientError("Request timeout")


# =========================================================================
# MCPServer JSON-RPC tests
# =========================================================================


@pytest.mark.unit
class TestMCPServerBasicProtocol:
    """Tests for MCPServer JSON-RPC protocol handling with minimal setup."""

    @pytest.fixture
    def server(self):
        """Create a minimal MCP server with no tools for protocol testing."""
        cfg = MCPServerConfig(name="test-protocol", version="0.1.0")
        srv = MCPServer(cfg)
        return srv

    def test_initialize_returns_protocol_version(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "clientInfo": {"name": "test", "version": "1.0"},
                    },
                }
            )
        )
        assert resp["result"]["protocolVersion"] == "2025-06-18"

    def test_initialize_returns_server_info(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {},
                }
            )
        )
        info = resp["result"]["serverInfo"]
        assert info["name"] == "test-protocol"
        assert info["version"] == "0.1.0"

    def test_notification_returns_none(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {},
                }
            )
        )
        assert resp is None

    def test_unknown_method_returns_error_code(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 99,
                    "method": "completely/unknown",
                    "params": {},
                }
            )
        )
        assert "error" in resp
        assert resp["error"]["code"] == -32603

    def test_empty_tools_list(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {},
                }
            )
        )
        assert resp["result"]["tools"] == []

    def test_empty_resources_list(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "resources/list",
                    "params": {},
                }
            )
        )
        assert resp["result"]["resources"] == []

    def test_empty_prompts_list(self, server):
        resp = _run(
            server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "prompts/list",
                    "params": {},
                }
            )
        )
        assert resp["result"]["prompts"] == []


@pytest.mark.unit
class TestMCPServerToolRegistration:
    """Tests for MCPServer tool registration and execution."""

    @pytest.fixture
    def server_with_tool(self):
        """Create an MCP server with a registered tool."""
        cfg = MCPServerConfig(name="tool-test", version="0.1.0")
        srv = MCPServer(cfg)

        @srv.tool(name="echo", description="Echo input back")
        def echo(message: str) -> str:
            return json.dumps({"echoed": message})

        return srv

    def test_registered_tool_appears_in_list(self, server_with_tool):
        resp = _run(
            server_with_tool.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {},
                }
            )
        )
        tools = resp["result"]["tools"]
        names = [t["name"] for t in tools]
        assert "echo" in names

    def test_tool_schema_has_input_schema(self, server_with_tool):
        resp = _run(
            server_with_tool.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {},
                }
            )
        )
        tool = resp["result"]["tools"][0]
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"

    def test_register_resource_and_list(self):
        srv = MCPServer(MCPServerConfig(name="res-test", version="0.1.0"))
        srv.register_resource(
            uri="test://data",
            name="Test Data",
            description="Test resource",
            content_provider=lambda: "resource content",
        )
        resp = _run(
            srv.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "resources/list",
                    "params": {},
                }
            )
        )
        resources = resp["result"]["resources"]
        assert len(resources) == 1
        assert resources[0]["uri"] == "test://data"
        assert resources[0]["name"] == "Test Data"

    def test_read_resource_returns_content(self):
        srv = MCPServer(MCPServerConfig(name="res-read", version="0.1.0"))
        srv.register_resource(
            uri="test://hello",
            name="Hello",
            content_provider=lambda: "Hello World",
        )
        resp = _run(
            srv.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "resources/read",
                    "params": {"uri": "test://hello"},
                }
            )
        )
        contents = resp["result"]["contents"]
        assert contents[0]["text"] == "Hello World"

    def test_read_nonexistent_resource_returns_error(self):
        srv = MCPServer(MCPServerConfig(name="res-err", version="0.1.0"))
        resp = _run(
            srv.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "resources/read",
                    "params": {"uri": "test://missing"},
                }
            )
        )
        assert "error" in resp

    def test_register_prompt_and_get(self):
        srv = MCPServer(MCPServerConfig(name="prompt-test", version="0.1.0"))
        srv.register_prompt(
            name="greet",
            description="Greeting prompt",
            template="Hello {name}, welcome to {place}!",
            arguments=[
                {"name": "name", "description": "Person name"},
                {"name": "place", "description": "Location"},
            ],
        )
        resp = _run(
            srv.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "prompts/get",
                    "params": {
                        "name": "greet",
                        "arguments": {"name": "Alice", "place": "Wonderland"},
                    },
                }
            )
        )
        messages = resp["result"]["messages"]
        text = messages[0]["content"]["text"]
        assert "Alice" in text
        assert "Wonderland" in text


# =========================================================================
# Structured Error types (errors.py)
# =========================================================================


@pytest.mark.unit
class TestMCPErrorCode:
    """Tests for MCPErrorCode enum."""

    def test_all_error_codes_exist(self):
        expected = {
            "VALIDATION_ERROR",
            "EXECUTION_ERROR",
            "TIMEOUT",
            "NOT_FOUND",
            "RATE_LIMITED",
            "CIRCUIT_OPEN",
            "DEPENDENCY_MISSING",
            "ACCESS_DENIED",
            "INTERNAL",
        }
        actual = {e.value for e in MCPErrorCode}
        assert expected == actual

    def test_error_code_is_string_enum(self):
        for code in MCPErrorCode:
            assert isinstance(code.value, str)


@pytest.mark.unit
class TestFieldError:
    """Tests for the FieldError dataclass."""

    def test_field_error_to_dict_minimal(self):
        fe = FieldError(field="name", constraint="required")
        d = fe.to_dict()
        assert d["field"] == "name"
        assert d["constraint"] == "required"
        assert "value" not in d

    def test_field_error_to_dict_with_value(self):
        fe = FieldError(field="age", constraint="min:0", value=-5)
        d = fe.to_dict()
        assert d["value"] == -5

    def test_field_error_is_frozen(self):
        fe = FieldError(field="f", constraint="c")
        with pytest.raises(AttributeError):
            fe.field = "new"


@pytest.mark.unit
class TestMCPToolError:
    """Tests for the MCPToolError dataclass and its serialization."""

    def test_to_dict_basic(self):
        err = MCPToolError(
            code=MCPErrorCode.VALIDATION_ERROR,
            message="Bad input",
            tool_name="my_tool",
        )
        d = err.to_dict()
        assert d["code"] == "VALIDATION_ERROR"
        assert d["message"] == "Bad input"
        assert d["tool_name"] == "my_tool"
        assert "correlation_id" in d
        assert len(d["correlation_id"]) == 12

    def test_to_dict_includes_field_errors(self):
        err = MCPToolError(
            code=MCPErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            field_errors=[
                FieldError(field="path", constraint="required"),
                FieldError(field="size", constraint="max:1000", value=2000),
            ],
        )
        d = err.to_dict()
        assert len(d["field_errors"]) == 2
        assert d["field_errors"][0]["field"] == "path"

    def test_to_dict_includes_suggestion(self):
        err = MCPToolError(
            code=MCPErrorCode.NOT_FOUND,
            message="Not found",
            suggestion="Did you mean 'read_file'?",
        )
        d = err.to_dict()
        assert d["suggestion"] == "Did you mean 'read_file'?"

    def test_to_json_produces_valid_json(self):
        err = MCPToolError(
            code=MCPErrorCode.EXECUTION_ERROR,
            message="Crash",
        )
        json_str = err.to_json()
        parsed = json.loads(json_str)
        assert parsed["code"] == "EXECUTION_ERROR"
        assert parsed["message"] == "Crash"

    def test_to_mcp_response_shape(self):
        err = MCPToolError(
            code=MCPErrorCode.TIMEOUT,
            message="Timed out",
        )
        resp = err.to_mcp_response()
        assert resp["isError"] is True
        assert len(resp["content"]) == 1
        assert resp["content"][0]["type"] == "text"
        # The text field should be parseable JSON
        inner = json.loads(resp["content"][0]["text"])
        assert inner["code"] == "TIMEOUT"

    def test_from_dict_roundtrip(self):
        original = MCPToolError(
            code=MCPErrorCode.ACCESS_DENIED,
            message="No permission",
            tool_name="secret_tool",
            module="codomyrmex.security",
            suggestion="Request access first",
            field_errors=[FieldError(field="token", constraint="valid")],
        )
        d = original.to_dict()
        restored = MCPToolError.from_dict(d)
        assert restored.code == MCPErrorCode.ACCESS_DENIED
        assert restored.message == "No permission"
        assert restored.tool_name == "secret_tool"
        assert restored.module == "codomyrmex.security"
        assert restored.suggestion == "Request access first"
        assert len(restored.field_errors) == 1

    def test_from_json_roundtrip(self):
        original = MCPToolError(
            code=MCPErrorCode.INTERNAL,
            message="Unexpected error",
        )
        json_str = original.to_json()
        restored = MCPToolError.from_json(json_str)
        assert restored.code == MCPErrorCode.INTERNAL
        assert restored.message == "Unexpected error"
        assert restored.correlation_id == original.correlation_id

    def test_from_mcp_response_parses_error(self):
        err = MCPToolError(
            code=MCPErrorCode.RATE_LIMITED,
            message="Too many requests",
            tool_name="busy_tool",
        )
        resp = err.to_mcp_response()
        parsed = MCPToolError.from_mcp_response(resp)
        assert parsed is not None
        assert parsed.code == MCPErrorCode.RATE_LIMITED
        assert parsed.tool_name == "busy_tool"

    def test_from_mcp_response_returns_none_for_non_error(self):
        resp = {"content": [{"type": "text", "text": "ok"}]}
        assert MCPToolError.from_mcp_response(resp) is None

    def test_from_mcp_response_handles_unstructured_error(self):
        resp = {
            "isError": True,
            "content": [{"type": "text", "text": "Something broke badly"}],
        }
        parsed = MCPToolError.from_mcp_response(resp)
        assert parsed is not None
        assert parsed.code == MCPErrorCode.INTERNAL
        assert "Something broke badly" in parsed.message


@pytest.mark.unit
class TestConvenienceConstructors:
    """Tests for error convenience constructors."""

    def test_validation_error_constructor(self):
        err = validation_error(
            tool_name="check_input",
            message="Invalid data",
            field_errors=[FieldError(field="x", constraint="required")],
        )
        assert err.code == MCPErrorCode.VALIDATION_ERROR
        assert err.tool_name == "check_input"
        assert len(err.field_errors) == 1

    def test_not_found_error_constructor(self):
        err = not_found_error("missing_tool")
        assert err.code == MCPErrorCode.NOT_FOUND
        assert "missing_tool" in err.message

    def test_timeout_error_constructor(self):
        err = timeout_error("slow_tool", 30.0)
        assert err.code == MCPErrorCode.TIMEOUT
        assert "30" in err.message
        assert err.tool_name == "slow_tool"

    def test_execution_error_constructor(self):
        exc = RuntimeError("segfault")
        err = execution_error(
            "crashy_tool",
            exc,
            module="codomyrmex.crashy",
            suggestion="Try again",
        )
        assert err.code == MCPErrorCode.EXECUTION_ERROR
        assert "RuntimeError" in err.message
        assert "segfault" in err.message
        assert err.module == "codomyrmex.crashy"
        assert err.suggestion == "Try again"
