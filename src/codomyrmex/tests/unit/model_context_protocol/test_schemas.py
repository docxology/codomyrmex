"""Tests for model_context_protocol.schemas — schema dataclasses and pydantic models.

Tests cover the dataclass-based schema module (schemas/__init__.py) including
Tool, ToolParameter, ToolCall, ToolResult, Message, Conversation, Request,
Response, and the create_tool factory.  Also tests the pydantic models from
schemas/mcp_schemas.py including MCPToolRegistry.
All tests use real object construction — no mocks.
"""

import json

import pytest

pydantic = pytest.importorskip("pydantic")

from codomyrmex.model_context_protocol.schemas import (
    ContentType,
    Conversation,
    FileContent,
    ImageContent,
    Message,
    MessageRole,
    Request,
    Response,
    TextContent,
    Tool,
    ToolCall,
    ToolParameter,
    ToolResult,
    create_tool,
)
from codomyrmex.model_context_protocol.schemas.mcp_schemas import (
    MCPMessage,
    MCPToolCall,
    MCPToolRegistry,
)

# =========================================================================
# Dataclass schema tests (schemas/__init__.py)
# =========================================================================


@pytest.mark.unit
class TestToolParameter:
    """Tests for the ToolParameter dataclass."""

    def test_to_dict_includes_all_fields(self):
        """Test functionality: to_dict includes name, type, description, required."""
        param = ToolParameter(
            name="path",
            param_type="string",
            description="File path",
            required=True,
        )
        d = param.to_dict()
        assert d["name"] == "path"
        assert d["type"] == "string"
        assert d["description"] == "File path"
        assert d["required"] is True

    def test_to_dict_includes_default_when_set(self):
        """Test functionality: default appears in dict when non-None."""
        param = ToolParameter(
            name="encoding",
            param_type="string",
            description="Encoding",
            required=False,
            default="utf-8",
        )
        d = param.to_dict()
        assert d["default"] == "utf-8"

    def test_to_dict_includes_enum_when_set(self):
        """Test functionality: enum list appears in dict when non-None."""
        param = ToolParameter(
            name="format",
            param_type="string",
            description="Output format",
            enum=["json", "text", "csv"],
        )
        d = param.to_dict()
        assert d["enum"] == ["json", "text", "csv"]

    def test_to_json_schema_format(self):
        """Test functionality: to_json_schema returns type and description."""
        param = ToolParameter(
            name="count",
            param_type="integer",
            description="Number of items",
        )
        schema = param.to_json_schema()
        assert schema["type"] == "integer"
        assert schema["description"] == "Number of items"

    def test_to_json_schema_includes_enum(self):
        """Test functionality: to_json_schema includes enum when set."""
        param = ToolParameter(
            name="level",
            param_type="string",
            description="Log level",
            enum=["DEBUG", "INFO", "ERROR"],
        )
        schema = param.to_json_schema()
        assert schema["enum"] == ["DEBUG", "INFO", "ERROR"]


@pytest.mark.unit
class TestTool:
    """Tests for the Tool dataclass."""

    def test_to_dict_basic_tool(self):
        """Test functionality: to_dict serializes a basic tool."""
        tool = Tool(
            name="read_file",
            description="Read a file",
            parameters=[
                ToolParameter(name="path", param_type="string", description="Path"),
            ],
        )
        d = tool.to_dict()
        assert d["name"] == "read_file"
        assert d["description"] == "Read a file"
        assert len(d["parameters"]) == 1
        assert d["parameters"][0]["name"] == "path"

    def test_to_openai_format(self):
        """Test functionality: to_openai_format produces function calling format."""
        tool = Tool(
            name="calculate",
            description="Calculate expression",
            parameters=[
                ToolParameter(name="expression", param_type="string", description="Math expr", required=True),
                ToolParameter(name="precision", param_type="integer", description="Decimal places", required=False),
            ],
        )
        oai = tool.to_openai_format()
        assert oai["type"] == "function"
        fn = oai["function"]
        assert fn["name"] == "calculate"
        assert fn["description"] == "Calculate expression"
        assert fn["parameters"]["type"] == "object"
        assert "expression" in fn["parameters"]["properties"]
        assert "expression" in fn["parameters"]["required"]
        assert "precision" not in fn["parameters"]["required"]

    def test_tool_version_defaults(self):
        """Test functionality: default version is 1.0.0."""
        tool = Tool(name="t", description="d")
        assert tool.version == "1.0.0"


@pytest.mark.unit
class TestCreateToolFactory:
    """Tests for the create_tool helper function."""

    def test_create_tool_with_parameters(self):
        """Test functionality: create_tool builds a Tool with proper params."""
        tool = create_tool(
            name="search",
            description="Search documents",
            parameters={
                "query": {"type": "string", "description": "Search query", "required": True},
                "limit": {"type": "integer", "description": "Max results", "required": False, "default": 10},
            },
        )
        assert tool.name == "search"
        assert len(tool.parameters) == 2
        names = [p.name for p in tool.parameters]
        assert "query" in names
        assert "limit" in names

    def test_create_tool_without_parameters(self):
        """Test functionality: create_tool with no params yields empty list."""
        tool = create_tool(name="ping", description="Health check")
        assert tool.parameters == []


@pytest.mark.unit
class TestToolCallAndResult:
    """Tests for ToolCall and ToolResult dataclasses."""

    def test_tool_call_to_dict(self):
        """Test functionality: ToolCall.to_dict produces expected shape."""
        tc = ToolCall(id="call_123", name="read_file", arguments={"path": "/tmp/f"})
        d = tc.to_dict()
        assert d["type"] == "tool_call"
        assert d["id"] == "call_123"
        assert d["name"] == "read_file"
        assert d["arguments"]["path"] == "/tmp/f"

    def test_tool_result_success(self):
        """Test functionality: ToolResult.to_dict for success."""
        tr = ToolResult(tool_call_id="call_123", content="file content", is_error=False)
        d = tr.to_dict()
        assert d["type"] == "tool_result"
        assert d["tool_call_id"] == "call_123"
        assert d["content"] == "file content"
        assert d["is_error"] is False

    def test_tool_result_error(self):
        """Test functionality: ToolResult.to_dict for error."""
        tr = ToolResult(tool_call_id="call_456", content="Not found", is_error=True)
        d = tr.to_dict()
        assert d["is_error"] is True


@pytest.mark.unit
class TestContentTypes:
    """Tests for TextContent, ImageContent, FileContent dataclasses."""

    def test_text_content_to_dict(self):
        """Test functionality: TextContent serializes correctly."""
        tc = TextContent(text="Hello world")
        d = tc.to_dict()
        assert d["type"] == "text"
        assert d["text"] == "Hello world"

    def test_image_content_to_dict(self):
        """Test functionality: ImageContent serializes with media_type."""
        ic = ImageContent(source="https://example.com/img.png", media_type="image/png")
        d = ic.to_dict()
        assert d["type"] == "image"
        assert d["source"] == "https://example.com/img.png"
        assert d["media_type"] == "image/png"

    def test_image_content_alt_text_included_when_set(self):
        """Test functionality: alt_text appears in dict when set."""
        ic = ImageContent(source="img.jpg", alt_text="A photo")
        d = ic.to_dict()
        assert d["alt_text"] == "A photo"

    def test_file_content_to_dict(self):
        """Test functionality: FileContent serializes correctly."""
        fc = FileContent(name="data.csv", path="/tmp/data.csv", mime_type="text/csv")
        d = fc.to_dict()
        assert d["type"] == "file"
        assert d["name"] == "data.csv"
        assert d["path"] == "/tmp/data.csv"
        assert d["mime_type"] == "text/csv"


@pytest.mark.unit
class TestMessageAndConversation:
    """Tests for Message and Conversation dataclasses."""

    def test_message_from_text(self):
        """Test functionality: Message.from_text creates a text message."""
        msg = Message.from_text(MessageRole.USER, "Hello")
        assert msg.role == MessageRole.USER
        assert msg.get_text() == "Hello"

    def test_message_to_dict(self):
        """Test functionality: Message.to_dict includes role and content."""
        msg = Message.from_text(MessageRole.ASSISTANT, "Hi there")
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert len(d["content"]) == 1
        assert d["content"][0]["text"] == "Hi there"

    def test_conversation_add_messages(self):
        """Test functionality: Conversation tracks messages."""
        conv = Conversation(id="conv_1")
        conv.add_user_message("Hello")
        conv.add_assistant_message("Hi!")
        assert len(conv.messages) == 2
        assert conv.messages[0].role == MessageRole.USER
        assert conv.messages[1].role == MessageRole.ASSISTANT

    def test_conversation_to_json_roundtrip(self):
        """Test functionality: Conversation serializes to valid JSON."""
        conv = Conversation(id="conv_2")
        conv.add_user_message("Test")
        json_str = conv.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == "conv_2"
        assert len(parsed["messages"]) == 1

    def test_message_role_enum_values(self):
        """Test functionality: MessageRole enum has expected values."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.TOOL.value == "tool"

    def test_content_type_enum_values(self):
        """Test functionality: ContentType enum has expected values."""
        assert ContentType.TEXT.value == "text"
        assert ContentType.IMAGE.value == "image"
        assert ContentType.TOOL_CALL.value == "tool_call"
        assert ContentType.TOOL_RESULT.value == "tool_result"


@pytest.mark.unit
class TestRequestResponse:
    """Tests for Request and Response dataclasses."""

    def test_request_to_dict(self):
        """Test functionality: Request.to_dict includes all fields."""
        conv = Conversation(id="r_1")
        conv.add_user_message("Ask something")
        tool = Tool(name="search", description="Search")
        req = Request(conversation=conv, tools=[tool], model="test-model", temperature=0.5)
        d = req.to_dict()
        assert d["model"] == "test-model"
        assert d["temperature"] == 0.5
        assert len(d["tools"]) == 1
        assert d["conversation"]["id"] == "r_1"

    def test_response_to_dict(self):
        """Test functionality: Response.to_dict includes message and finish_reason."""
        msg = Message.from_text(MessageRole.ASSISTANT, "Answer")
        resp = Response(message=msg, finish_reason="stop", model="test-model")
        d = resp.to_dict()
        assert d["finish_reason"] == "stop"
        assert d["model"] == "test-model"
        assert d["message"]["role"] == "assistant"


# =========================================================================
# Pydantic model tests (schemas/mcp_schemas.py)
# =========================================================================


@pytest.mark.unit
class TestMCPToolRegistry:
    """Tests for the MCPToolRegistry class."""

    def test_register_and_list_tools(self):
        """Test functionality: register a tool and list it."""
        registry = MCPToolRegistry()
        registry.register("my_tool", {"name": "my_tool", "description": "Test"})
        assert "my_tool" in registry.list_tools()

    def test_get_returns_tool_data(self):
        """Test functionality: get returns the registered tool dict."""
        registry = MCPToolRegistry()
        registry.register("t1", {"name": "t1"}, handler=lambda: "ok")
        tool = registry.get("t1")
        assert tool is not None
        assert tool["name"] == "t1"
        assert tool["handler"] is not None

    def test_get_returns_none_for_missing(self):
        """Test functionality: get returns None for unregistered tool."""
        registry = MCPToolRegistry()
        assert registry.get("missing") is None

    def test_unregister_removes_tool(self):
        """Test functionality: unregister removes tool from registry."""
        registry = MCPToolRegistry()
        registry.register("removable", {"name": "removable"})
        assert registry.unregister("removable") is True
        assert registry.get("removable") is None

    def test_unregister_returns_false_for_missing(self):
        """Test functionality: unregister returns False for unknown tool."""
        registry = MCPToolRegistry()
        assert registry.unregister("nonexistent") is False

    def test_validate_call_known_tool(self):
        """Test functionality: validate_call succeeds for known tool."""
        registry = MCPToolRegistry()
        registry.register("valid_tool", {"name": "valid_tool"})
        call = MCPToolCall(tool_name="valid_tool", arguments={"x": 1})
        valid, error = registry.validate_call(call)
        assert valid is True
        assert error is None

    def test_validate_call_unknown_tool(self):
        """Test functionality: validate_call fails for unknown tool."""
        registry = MCPToolRegistry()
        call = MCPToolCall(tool_name="unknown", arguments={})
        valid, error = registry.validate_call(call)
        assert valid is False
        assert "Unknown tool" in error

    def test_execute_with_handler(self):
        """Test functionality: execute calls handler and returns success."""
        registry = MCPToolRegistry()
        registry.register(
            "adder",
            {"name": "adder"},
            handler=lambda a, b: a + b,
        )
        call = MCPToolCall(tool_name="adder", arguments={"a": 2, "b": 3})
        result = registry.execute(call)
        assert result.status == "success"
        assert result.data["result"] == 5

    def test_execute_without_handler_returns_failure(self):
        """Test functionality: execute without handler returns failure."""
        registry = MCPToolRegistry()
        registry.register("no_handler", {"name": "no_handler"})
        call = MCPToolCall(tool_name="no_handler", arguments={})
        result = registry.execute(call)
        assert result.status == "failure"
        assert result.error is not None
        assert "NoHandler" in result.error.error_type

    def test_execute_unknown_tool_returns_failure(self):
        """Test functionality: execute for unknown tool returns failure."""
        registry = MCPToolRegistry()
        call = MCPToolCall(tool_name="ghost", arguments={})
        result = registry.execute(call)
        assert result.status == "failure"
        assert "ToolNotFound" in result.error.error_type

    def test_execute_handler_exception_returns_failure(self):
        """Test functionality: handler exception captured in failure result."""
        registry = MCPToolRegistry()

        def bad_handler(**kwargs):
            raise ValueError("Something went wrong")

        registry.register("bad", {"name": "bad"}, handler=bad_handler)
        call = MCPToolCall(tool_name="bad", arguments={})
        result = registry.execute(call)
        assert result.status == "failure"
        assert result.error.error_type == "ValueError"
        assert "Something went wrong" in result.error.error_message

    def test_get_tool_alias_matches_get(self):
        """Test functionality: get_tool is an alias for get."""
        registry = MCPToolRegistry()
        registry.register("aliased", {"name": "aliased"})
        assert registry.get_tool("aliased") == registry.get("aliased")


@pytest.mark.unit
class TestMCPMessageModel:
    """Tests for the MCPMessage pydantic model."""

    def test_create_user_message(self):
        """Test functionality: create a user message with content."""
        msg = MCPMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_with_tool_calls(self):
        """Test functionality: message can carry tool_calls."""
        call = MCPToolCall(tool_name="test.tool", arguments={"x": 1})
        msg = MCPMessage(role="assistant", tool_calls=[call])
        assert len(msg.tool_calls) == 1
        assert msg.tool_calls[0].tool_name == "test.tool"

    def test_message_serialization_roundtrip(self):
        """Test functionality: MCPMessage serializes to JSON and back."""
        msg = MCPMessage(role="system", content="You are helpful", metadata={"key": "value"})
        json_str = msg.model_dump_json()
        restored = MCPMessage.model_validate_json(json_str)
        assert restored.role == "system"
        assert restored.content == "You are helpful"
        assert restored.metadata["key"] == "value"

    def test_message_allows_extra_fields(self):
        """Test functionality: MCPMessage allows extra fields."""
        msg = MCPMessage(role="user", content="Hi", custom_field="extra")
        assert hasattr(msg, "custom_field")
        assert msg.custom_field == "extra"
