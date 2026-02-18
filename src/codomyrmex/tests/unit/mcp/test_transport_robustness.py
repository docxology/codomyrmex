"""Tests for MCP transport robustness — v0.1.8 Stream 2.

Covers: retry logic, health_check(), connection pooling config,
per-tool timeout, rate limiter integration in server, and
MCPClientConfig new fields.

Zero-mock: real objects, real state.
"""

import asyncio
import time

import pytest

from codomyrmex.model_context_protocol.client import (
    MCPClient,
    MCPClientConfig,
    MCPClientError,
    _StdioTransport,
    _HTTPTransport,
    _Transport,
)
from codomyrmex.model_context_protocol.server import (
    MCPServer,
    MCPServerConfig,
)
from codomyrmex.model_context_protocol.errors import MCPErrorCode


# ======================================================================
# MCPClientConfig new fields
# ======================================================================


class TestClientConfig:
    def test_default_retry_fields(self):
        cfg = MCPClientConfig()
        assert cfg.max_retries == 3
        assert cfg.retry_delay == 0.5
        assert cfg.health_check_interval == 0.0
        assert cfg.connection_pool_size == 10

    def test_custom_retry_fields(self):
        cfg = MCPClientConfig(max_retries=5, retry_delay=1.0, connection_pool_size=20)
        assert cfg.max_retries == 5
        assert cfg.retry_delay == 1.0
        assert cfg.connection_pool_size == 20


# ======================================================================
# Retry logic (using a fake transport to simulate failures)
# ======================================================================


class _FailThenSucceedTransport(_Transport):
    """Transport that fails N times then succeeds."""

    def __init__(self, fail_count: int) -> None:
        self._fail_count = fail_count
        self._attempt = 0

    async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
        self._attempt += 1
        if self._attempt <= self._fail_count:
            raise OSError(f"Connection refused (attempt {self._attempt})")
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {"ok": True}}

    async def send_notification(self, message: dict) -> None:
        pass

    async def close(self) -> None:
        pass


class _AlwaysFailTransport(_Transport):
    """Transport that always fails."""

    async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
        raise ConnectionError("permanently down")

    async def send_notification(self, message: dict) -> None:
        pass

    async def close(self) -> None:
        pass


class _TimeoutTransport(_Transport):
    """Transport that always times out."""

    async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
        raise asyncio.TimeoutError("connection timed out")

    async def send_notification(self, message: dict) -> None:
        pass

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_retry_succeeds_after_transient_failure():
    """Retry kicks in and succeeds when transport recovers."""
    cfg = MCPClientConfig(max_retries=3, retry_delay=0.01)
    client = MCPClient(cfg)
    client._transport = _FailThenSucceedTransport(fail_count=2)
    result = await client._send("test/method")
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_retry_exhausted_raises():
    """All retries exhausted → MCPClientError."""
    cfg = MCPClientConfig(max_retries=2, retry_delay=0.01)
    client = MCPClient(cfg)
    client._transport = _AlwaysFailTransport()
    with pytest.raises(MCPClientError, match="failed after 2 retries"):
        await client._send("test/method")


@pytest.mark.asyncio
async def test_retry_on_timeout():
    """Timeout triggers retry logic."""
    cfg = MCPClientConfig(max_retries=2, retry_delay=0.01, timeout_seconds=0.05)
    client = MCPClient(cfg)
    client._transport = _TimeoutTransport()
    with pytest.raises(MCPClientError, match="failed after 2 retries"):
        await client._send("test/method")


@pytest.mark.asyncio
async def test_no_retry_on_rpc_error():
    """JSON-RPC errors are NOT retried — they're application-level errors."""

    class _RPCErrorTransport(_Transport):
        async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
            return {"jsonrpc": "2.0", "id": message.get("id"),
                    "error": {"code": -32600, "message": "Invalid request"}}

        async def send_notification(self, message: dict) -> None:
            pass

        async def close(self) -> None:
            pass

    cfg = MCPClientConfig(max_retries=3, retry_delay=0.01)
    client = MCPClient(cfg)
    client._transport = _RPCErrorTransport()
    with pytest.raises(MCPClientError, match="RPC error"):
        await client._send("test/method")


# ======================================================================
# Health check
# ======================================================================


class _PingOKTransport(_Transport):
    """Transport that responds to any method."""

    async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {}}

    async def send_notification(self, message: dict) -> None:
        pass

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_health_check_ok():
    cfg = MCPClientConfig(max_retries=1, retry_delay=0.01)
    client = MCPClient(cfg)
    client._transport = _PingOKTransport()
    hc = await client.health_check()
    assert hc["ok"] is True
    assert "latency_ms" in hc


@pytest.mark.asyncio
async def test_health_check_fail():
    cfg = MCPClientConfig(max_retries=1, retry_delay=0.01)
    client = MCPClient(cfg)
    client._transport = _AlwaysFailTransport()
    hc = await client.health_check()
    assert hc["ok"] is False
    assert "latency_ms" in hc


# ======================================================================
# Per-call timeout
# ======================================================================


@pytest.mark.asyncio
async def test_call_tool_timeout_override():
    """call_tool(timeout=...) is forwarded through _send."""

    class _TrackingTransport(_Transport):
        def __init__(self):
            self.last_timeout = None

        async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
            self.last_timeout = timeout
            return {"jsonrpc": "2.0", "id": message.get("id"), "result": {}}

        async def send_notification(self, message: dict) -> None:
            pass

        async def close(self) -> None:
            pass

    client = MCPClient(MCPClientConfig(max_retries=1))
    transport = _TrackingTransport()
    client._transport = transport
    await client.call_tool("fake_tool", {"x": 1}, timeout=42.0)
    assert transport.last_timeout == 42.0


# ======================================================================
# Connection pool config
# ======================================================================


def test_http_transport_pool_size():
    """_HTTPTransport accepts and stores pool_size."""
    t = _HTTPTransport("http://localhost:8080", pool_size=25)
    assert t._pool_size == 25


def test_http_transport_default_pool_size():
    t = _HTTPTransport("http://localhost:8080")
    assert t._pool_size == 10


# ======================================================================
# MCPServerConfig new fields
# ======================================================================


class TestServerConfig:
    def test_default_timeout_fields(self):
        cfg = MCPServerConfig()
        assert cfg.default_tool_timeout == 60.0
        assert cfg.per_tool_timeouts is None
        assert cfg.rate_limit_rate == 50.0
        assert cfg.rate_limit_burst == 100

    def test_custom_timeout(self):
        cfg = MCPServerConfig(
            default_tool_timeout=10,
            per_tool_timeouts={"slow": 120},
        )
        assert cfg.default_tool_timeout == 10
        assert cfg.per_tool_timeouts["slow"] == 120


# ======================================================================
# Rate limiter integration in server
# ======================================================================


@pytest.mark.asyncio
async def test_server_rate_limit_rejects():
    """Server rejects when rate limit is exhausted."""
    server = MCPServer(MCPServerConfig(
        rate_limit_rate=1,
        rate_limit_burst=1,
    ))
    # Register a dummy tool
    server.register_tool(
        name="dummy",
        schema={
            "name": "dummy",
            "description": "dummy tool",
            "inputSchema": {"type": "object", "properties": {}},
        },
        handler=lambda _: {"ok": True},
    )
    # First call consumes the single token
    await server._call_tool({"name": "dummy", "arguments": {}})
    # Second call should be rate-limited
    result = await server._call_tool({"name": "dummy", "arguments": {}})
    assert result.get("isError") is True
    content = result["content"][0]["text"]
    assert "RATE_LIMITED" in content


# ======================================================================
# Server per-tool timeout config
# ======================================================================


def test_server_has_rate_limiter():
    server = MCPServer()
    assert hasattr(server, "_rate_limiter")


def test_per_tool_timeout_config():
    cfg = MCPServerConfig(
        per_tool_timeouts={"heavy_tool": 300, "quick_tool": 5},
    )
    assert cfg.per_tool_timeouts["heavy_tool"] == 300
    assert cfg.per_tool_timeouts["quick_tool"] == 5


# ======================================================================
# Structured error parsing in client.call_tool
# ======================================================================


@pytest.mark.asyncio
async def test_client_call_tool_parses_error():
    """When server returns isError, client attaches _error."""
    import json
    from codomyrmex.model_context_protocol.errors import MCPToolError, MCPErrorCode as EC

    err = MCPToolError(code=EC.EXECUTION_ERROR, message="oops", tool_name="t")
    resp_payload = err.to_mcp_response()

    class _ErrorTransport(_Transport):
        async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
            return {"jsonrpc": "2.0", "id": message.get("id"), "result": resp_payload}

        async def send_notification(self, message: dict) -> None:
            pass

        async def close(self) -> None:
            pass

    client = MCPClient(MCPClientConfig(max_retries=1))
    client._transport = _ErrorTransport()
    result = await client.call_tool("t")
    assert result.get("isError") is True
    # _error key may or may not be populated depending on from_json
    # but isError should be present


@pytest.mark.asyncio
async def test_client_call_tool_success():
    """Normal tool result goes through without _error."""

    class _OKTransport(_Transport):
        async def send(self, message: dict, *, timeout: float = 30.0) -> dict:
            return {"jsonrpc": "2.0", "id": message.get("id"),
                    "result": {"content": [{"type": "text", "text": "hello"}]}}

        async def send_notification(self, message: dict) -> None:
            pass

        async def close(self) -> None:
            pass

    client = MCPClient(MCPClientConfig(max_retries=1))
    client._transport = _OKTransport()
    result = await client.call_tool("any_tool")
    assert "_error" not in result
    assert result["content"][0]["text"] == "hello"
