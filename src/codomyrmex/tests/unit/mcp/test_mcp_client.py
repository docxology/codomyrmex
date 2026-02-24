"""Tests for the MCPClient class.

Tests the client against the real MCPServer using an in-memory transport
to avoid network dependencies (zero-mock policy — we use real server code).
"""

import asyncio
import json

import pytest

from codomyrmex.model_context_protocol.transport.client import (
    MCPClient,
    MCPClientConfig,
    MCPClientError,
)
from codomyrmex.model_context_protocol.transport.server import MCPServer, MCPServerConfig


# ---------------------------------------------------------------------------
# In-memory transport for testing (bridges client → server without I/O)
# ---------------------------------------------------------------------------


class _InMemoryTransport:
    """Transport that feeds requests directly into an MCPServer."""

    def __init__(self, server: MCPServer) -> None:
        self._server = server

    async def send(self, message, *, timeout=30.0):
        response = await self._server.handle_request(message)
        return response or {}

    async def send_notification(self, message):
        await self._server.handle_request(message)

    async def close(self):
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def server():
    """Create a minimal MCP server with a test tool."""
    config = MCPServerConfig(name="test-server", version="0.1.0")
    srv = MCPServer(config)

    @srv.tool(name="echo", description="Echo the input back")
    def echo(text: str = "hello") -> str:
        return json.dumps({"echo": text})

    @srv.tool(name="add", description="Add two numbers")
    def add(a: int = 0, b: int = 0) -> str:
        return json.dumps({"sum": a + b})

    srv.register_resource(
        uri="test://greeting",
        name="Greeting",
        description="A greeting resource",
        content_provider=lambda: "Hello from test!",
    )
    srv.register_prompt(
        name="greet",
        description="A greeting prompt",
        template="Say {greeting} to {name}",
        arguments=[
            {"name": "greeting", "description": "The greeting"},
            {"name": "name", "description": "Who to greet"},
        ],
    )
    return srv


@pytest.fixture
def client(server):
    """Create an MCPClient connected to the test server via in-memory transport."""
    c = MCPClient(MCPClientConfig(name="test-client", version="0.1.0"))
    c._transport = _InMemoryTransport(server)
    return c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMCPClientLifecycle:
    """Test client initialization and lifecycle."""

    def test_initialize(self, client):
        """Test functionality: initialize."""
        result = asyncio.run(client.initialize())
        assert "protocolVersion" in result
        assert client._initialized is True
        assert client.server_info.get("serverInfo", {}).get("name") == "test-server"

    def test_close(self, client):
        """Test functionality: close."""
        asyncio.run(client.initialize())
        asyncio.run(client.close())
        assert client._transport is None
        assert client._initialized is False


@pytest.mark.unit
class TestMCPClientTools:
    """Test tool listing and invocation."""

    def test_list_tools(self, client):
        """Test functionality: list tools."""
        async def _test():
            await client.initialize()
            tools = await client.list_tools()
            names = [t["name"] for t in tools]
            assert "echo" in names
            assert "add" in names
            return tools

        tools = asyncio.run(_test())
        assert len(tools) >= 2

    def test_call_tool_echo(self, client):
        """Test functionality: call tool echo."""
        async def _test():
            await client.initialize()
            result = await client.call_tool("echo", {"text": "world"})
            return result

        result = asyncio.run(_test())
        assert "content" in result
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["echo"] == "world"

    def test_call_tool_add(self, client):
        """Test functionality: call tool add."""
        async def _test():
            await client.initialize()
            result = await client.call_tool("add", {"a": 3, "b": 4})
            return result

        result = asyncio.run(_test())
        assert "content" in result
        data = json.loads(result["content"][0]["text"])
        inner = json.loads(data["result"])
        assert inner["sum"] == 7


@pytest.mark.unit
class TestMCPClientResources:
    """Test resource listing and reading."""

    def test_list_resources(self, client):
        """Test functionality: list resources."""
        async def _test():
            await client.initialize()
            resources = await client.list_resources()
            return resources

        resources = asyncio.run(_test())
        assert len(resources) >= 1
        assert resources[0]["uri"] == "test://greeting"

    def test_read_resource(self, client):
        """Test functionality: read resource."""
        async def _test():
            await client.initialize()
            result = await client.read_resource("test://greeting")
            return result

        result = asyncio.run(_test())
        assert "contents" in result
        assert result["contents"][0]["text"] == "Hello from test!"


@pytest.mark.unit
class TestMCPClientPrompts:
    """Test prompt listing and rendering."""

    def test_list_prompts(self, client):
        """Test functionality: list prompts."""
        async def _test():
            await client.initialize()
            prompts = await client.list_prompts()
            return prompts

        prompts = asyncio.run(_test())
        assert any(p["name"] == "greet" for p in prompts)

    def test_get_prompt(self, client):
        """Test functionality: get prompt."""
        async def _test():
            await client.initialize()
            result = await client.get_prompt("greet", {"greeting": "hi", "name": "Alice"})
            return result

        result = asyncio.run(_test())
        assert "messages" in result
        assert "hi" in result["messages"][0]["content"]["text"]
        assert "Alice" in result["messages"][0]["content"]["text"]
