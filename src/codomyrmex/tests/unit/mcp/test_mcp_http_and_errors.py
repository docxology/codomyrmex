"""Tests for MCPClient HTTP transport and error/timeout scenarios.

Uses real MCPServer instances with custom transports — zero-mock policy
applies throughout. HTTP transport tests use aiohttp's test server to
exercise the full HTTP path without network dependencies. Error tests
use purpose-built transports that simulate failures.
"""

import asyncio
import json

import pytest

from codomyrmex.model_context_protocol.transport.client import (
    MCPClient,
    MCPClientConfig,
    MCPClientError,
)
from codomyrmex.model_context_protocol.transport.server import (
    MCPServer,
    MCPServerConfig,
)

# ======================================================================
# Shared server fixture
# ======================================================================


@pytest.fixture
def mcp_server():
    """Create a minimal MCP server with echo and add tools."""
    config = MCPServerConfig(name="test-server", version="0.1.0")
    srv = MCPServer(config)

    @srv.tool(name="echo", description="Echo the input")
    def echo(text: str = "hello") -> str:
        return json.dumps({"echo": text})

    @srv.tool(name="slow", description="Simulate slow tool")
    def slow(delay: float = 0.5) -> str:
        import time

        time.sleep(delay)
        return json.dumps({"waited": delay})

    srv.register_resource(
        uri="test://data",
        name="Data",
        description="Test data",
        content_provider=lambda: "test-content",
    )
    return srv


# ======================================================================
# HTTP Transport Tests — real aiohttp test server
# ======================================================================

try:
    import aiohttp
    from aiohttp import web
    from aiohttp.test_utils import AioHTTPTestCase, TestServer

    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False


@pytest.fixture
def http_app(mcp_server):
    """Create an aiohttp app that serves the MCPServer at /mcp."""
    if not HAS_AIOHTTP:
        pytest.skip("aiohttp not available")

    app = web.Application()

    async def handle_mcp(request: web.Request) -> web.Response:
        body = await request.json()
        response = await mcp_server.handle_request(body)
        return web.json_response(response or {})

    app.router.add_post("/mcp", handle_mcp)
    return app


@pytest.mark.unit
@pytest.mark.skipif(not HAS_AIOHTTP, reason="aiohttp not installed")
class TestMCPHTTPTransport:
    """Test MCP client over real HTTP transport using aiohttp test server."""

    @pytest.mark.asyncio
    async def test_http_initialize(self, http_app, mcp_server):
        """Test that HTTP client can initialize against real server."""
        server = TestServer(http_app)
        await server.start_server()
        try:
            base_url = f"http://localhost:{server.port}"
            async with MCPClient.connect_http(base_url) as client:
                assert client._initialized is True
                assert client.server_info.get("serverInfo", {}).get("name") == "test-server"
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_http_list_tools(self, http_app, mcp_server):
        """Test tool listing over HTTP."""
        server = TestServer(http_app)
        await server.start_server()
        try:
            base_url = f"http://localhost:{server.port}"
            async with MCPClient.connect_http(base_url) as client:
                tools = await client.list_tools()
                names = [t["name"] for t in tools]
                assert "echo" in names
                assert "slow" in names
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_http_call_tool(self, http_app, mcp_server):
        """Test tool invocation over HTTP."""
        server = TestServer(http_app)
        await server.start_server()
        try:
            base_url = f"http://localhost:{server.port}"
            async with MCPClient.connect_http(base_url) as client:
                result = await client.call_tool("echo", {"text": "http-test"})
                assert "content" in result
                data = json.loads(result["content"][0]["text"])
                inner = json.loads(data["result"])
                assert inner["echo"] == "http-test"
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_http_list_resources(self, http_app, mcp_server):
        """Test resource listing over HTTP."""
        server = TestServer(http_app)
        await server.start_server()
        try:
            base_url = f"http://localhost:{server.port}"
            async with MCPClient.connect_http(base_url) as client:
                resources = await client.list_resources()
                assert any(r["uri"] == "test://data" for r in resources)
        finally:
            await server.close()

    @pytest.mark.asyncio
    async def test_http_read_resource(self, http_app, mcp_server):
        """Test resource reading over HTTP."""
        server = TestServer(http_app)
        await server.start_server()
        try:
            base_url = f"http://localhost:{server.port}"
            async with MCPClient.connect_http(base_url) as client:
                result = await client.read_resource("test://data")
                assert result["contents"][0]["text"] == "test-content"
        finally:
            await server.close()


# ======================================================================
# Error and Timeout Tests — custom transports for controlled failure
# ======================================================================


class _ErrorTransport:
    """Transport that returns JSON-RPC error responses."""

    def __init__(self, error_code: int = -32600, error_message: str = "Test error"):
        self._error_code = error_code
        self._error_message = error_message
        self._call_count = 0

    async def send(self, message, *, timeout=30.0):
        self._call_count += 1
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": self._error_code,
                "message": self._error_message,
            },
        }

    async def send_notification(self, message):
        pass

    async def close(self):
        pass


class _TimeoutTransport:
    """Transport that raises TimeoutError to simulate transport-level timeout.

    Real transports (aiohttp, stdio) enforce the timeout internally.
    This transport verifies the timeout parameter is passed through and
    then raises asyncio.TimeoutError to simulate expiry.
    """

    def __init__(self):
        self.last_timeout: float | None = None

    async def send(self, message, *, timeout=30.0):
        self.last_timeout = timeout
        raise TimeoutError(f"Simulated timeout after {timeout}s")

    async def send_notification(self, message):
        pass  # notifications don't timeout

    async def close(self):
        pass


class _ServerExplodingTransport:
    """Transport that raises a raw exception (simulating transport failure)."""

    def __init__(self, exception: Exception | None = None):
        self._exception = exception or ConnectionError("Connection refused")

    async def send(self, message, *, timeout=30.0):
        raise self._exception

    async def send_notification(self, message):
        raise self._exception

    async def close(self):
        pass


@pytest.mark.unit
class TestMCPClientErrorHandling:
    """Test MCPClient error handling paths."""

    def test_rpc_error_raises_mcp_client_error(self):
        """Client should raise MCPClientError on JSON-RPC error response."""
        client = MCPClient(MCPClientConfig(name="err-client"))
        client._transport = _ErrorTransport(error_code=-32601, error_message="Method not found")

        with pytest.raises(MCPClientError, match="Method not found"):
            asyncio.run(client.initialize())

    def test_rpc_error_contains_method_name(self):
        """Error message should include the RPC method name."""
        client = MCPClient(MCPClientConfig(name="err-client"))
        client._transport = _ErrorTransport(error_message="Kaboom")

        with pytest.raises(MCPClientError, match="initialize") as exc_info:
            asyncio.run(client.initialize())
        assert "Kaboom" in str(exc_info.value)

    def test_call_tool_error(self):
        """Calling a nonexistent tool should propagate the server error."""
        async def _test():
            client = MCPClient(MCPClientConfig(name="err-client"))
            client._transport = _ErrorTransport(error_message="Tool not found")
            client._initialized = True  # Skip init
            with pytest.raises(MCPClientError, match="Tool not found"):
                await client.call_tool("nonexistent", {})

        asyncio.run(_test())

    def test_transport_error_retried_and_wrapped(self):
        """Raw transport errors (ConnectionError, OSError) are retried then wrapped."""
        client = MCPClient(MCPClientConfig(
            name="err-client", max_retries=1, retry_delay=0.01,
        ))
        client._transport = _ServerExplodingTransport(ConnectionError("refused"))

        with pytest.raises(MCPClientError, match="failed after 1 retries"):
            asyncio.run(client.initialize())

    def test_close_without_transport(self):
        """Closing a client that was never connected should be a no-op."""
        client = MCPClient()
        asyncio.run(client.close())
        assert client._transport is None

    def test_close_resets_state(self):
        """Closing should reset initialized state and transport."""
        async def _test():
            client = MCPClient()
            client._transport = _ErrorTransport()  # Will fail, but let's pretend
            client._initialized = True
            await client.close()
            assert client._initialized is False
            assert client._transport is None

        asyncio.run(_test())


@pytest.mark.unit
class TestMCPClientTimeout:
    """Test MCPClient timeout behavior."""

    def test_timeout_on_initialize(self):
        """Client should timeout and wrap in MCPClientError after retry."""
        config = MCPClientConfig(
            name="timeout-client", timeout_seconds=0.1,
            max_retries=1, retry_delay=0.01,
        )
        client = MCPClient(config)
        client._transport = _TimeoutTransport()

        with pytest.raises(MCPClientError, match="failed after 1 retries"):
            asyncio.run(client.initialize())

    def test_timeout_on_call_tool(self):
        """Tool call timeout is retried then wrapped in MCPClientError."""
        async def _test():
            config = MCPClientConfig(
                name="timeout-client", timeout_seconds=0.1,
                max_retries=1, retry_delay=0.01,
            )
            client = MCPClient(config)
            client._transport = _TimeoutTransport()
            client._initialized = True
            with pytest.raises(MCPClientError, match="failed after 1 retries"):
                await client.call_tool("echo", {"text": "hello"})

        asyncio.run(_test())

    def test_timeout_on_list_tools(self):
        """List tools timeout is retried then wrapped in MCPClientError."""
        async def _test():
            config = MCPClientConfig(
                name="timeout-client", timeout_seconds=0.1,
                max_retries=1, retry_delay=0.01,
            )
            client = MCPClient(config)
            client._transport = _TimeoutTransport()
            client._initialized = True
            with pytest.raises(MCPClientError, match="failed after 1 retries"):
                await client.list_tools()

        asyncio.run(_test())

    def test_timeout_recorded_by_transport(self):
        """Verify timeout parameter is forwarded to transport."""
        async def _test():
            config = MCPClientConfig(
                name="timeout-client", timeout_seconds=0.1,
                max_retries=1, retry_delay=0.01,
            )
            client = MCPClient(config)
            transport = _TimeoutTransport()
            client._transport = transport
            client._initialized = True
            with pytest.raises(MCPClientError):
                await client.call_tool("echo", {})
            assert transport.last_timeout == 0.1

        asyncio.run(_test())


# ======================================================================
# Concurrency Tests — verify thread safety of concurrent tool calls
# ======================================================================


class _CountingTransport:
    """Transport that tracks concurrent call count and returns echo results."""

    def __init__(self):
        self._active = 0
        self._max_active = 0
        self._total = 0
        import threading
        self._lock = threading.Lock()

    async def send(self, message, *, timeout=30.0):
        with self._lock:
            self._active += 1
            self._total += 1
            self._max_active = max(self._max_active, self._active)

        # Simulate brief work to allow overlap
        await asyncio.sleep(0.01)

        with self._lock:
            self._active -= 1

        method = message.get("method", "")
        params = message.get("params", {})

        if method == "tools/call":
            tool_args = params.get("arguments", {})
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"echo": tool_args.get("text", "")})}]
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {},
        }

    async def send_notification(self, message):
        pass

    async def close(self):
        pass


@pytest.mark.unit
class TestMCPClientConcurrency:
    """Test MCPClient thread safety under concurrent tool calls."""

    def test_concurrent_call_tool(self):
        """Run 10 concurrent call_tool invocations and verify no corruption."""
        async def _test():
            transport = _CountingTransport()
            client = MCPClient(MCPClientConfig(name="concurrency-client"))
            client._transport = transport
            client._initialized = True

            tasks = [
                client.call_tool("echo", {"text": f"msg-{i}"})
                for i in range(10)
            ]
            results = await asyncio.gather(*tasks)

            # All 10 should return successfully
            assert len(results) == 10
            for _i, result in enumerate(results):
                assert "content" in result
                data = json.loads(result["content"][0]["text"])
                # Each result should be a valid echo response
                assert "echo" in data

            # Transport should have handled all 10 calls
            assert transport._total == 10

        asyncio.run(_test())
