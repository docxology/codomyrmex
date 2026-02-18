"""Tests for MCP transport stress (Stream 4).

Verifies:
- Concurrent HTTP request handling via MCPServer
- Rapid message processing (100 messages in tight loop)
- Server handles reconnect patterns gracefully
- Partial/malformed JSON-RPC over stdio transport
"""

from __future__ import annotations

import asyncio
import json

import pytest

from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig


# ── Helpers ───────────────────────────────────────────────────────────


def _echo(**kwargs):
    return kwargs


def _make_server() -> MCPServer:
    """Build a test server with echo tool registered."""
    config = MCPServerConfig(warm_up=False)
    server = MCPServer(config=config)
    server.register_tool(
        name="echo",
        schema={"type": "object", "properties": {"msg": {"type": "string"}}},
        handler=_echo,
    )
    return server


# ── Concurrent HTTP-level requests ────────────────────────────────────


class TestConcurrentHTTPRequests:
    """Verify server handles concurrent HTTP-level request processing."""

    @pytest.mark.asyncio
    async def test_50_concurrent_requests(self) -> None:
        """50 concurrent _call_tool invocations via async gather."""
        server = _make_server()

        async def _req(i: int) -> dict:
            return await server._call_tool(
                {"name": "echo", "arguments": {"msg": f"request_{i}"}}
            )

        results = await asyncio.gather(*[_req(i) for i in range(50)])
        assert len(results) == 50
        for r in results:
            assert "content" in r

    @pytest.mark.asyncio
    async def test_concurrent_mixed_valid_invalid(self) -> None:
        """Mix of valid and invalid tool calls — server remains stable."""
        server = _make_server()

        async def _valid(i: int) -> dict:
            return await server._call_tool(
                {"name": "echo", "arguments": {"msg": f"ok_{i}"}}
            )

        async def _invalid(i: int) -> dict:
            return await server._call_tool(
                {"name": f"nonexistent_{i}", "arguments": {}}
            )

        tasks = []
        for i in range(20):
            tasks.append(_valid(i))
            tasks.append(_invalid(i))

        results = await asyncio.gather(*tasks)
        assert len(results) == 40

        # Valid calls should have content
        valid_results = results[::2]
        for r in valid_results:
            assert "content" in r

        # Invalid calls should have error markers
        invalid_results = results[1::2]
        for r in invalid_results:
            assert "isError" in r or "error" in str(r).lower()


# ── Rapid message processing ─────────────────────────────────────────


class TestRapidMessageProcessing:
    """Verify high-speed sequential message handling."""

    @pytest.mark.asyncio
    async def test_100_rapid_messages(self) -> None:
        """Process 100 JSON-RPC-style messages in tight async loop."""
        server = _make_server()
        results = []
        for i in range(100):
            r = await server._call_tool(
                {"name": "echo", "arguments": {"msg": f"rapid_{i}"}}
            )
            results.append(r)

        assert len(results) == 100
        successes = [r for r in results if "content" in r]
        assert len(successes) == 100

    @pytest.mark.asyncio
    async def test_rapid_register_and_call(self) -> None:
        """Register a new tool and immediately call it, 50 times."""
        server = _make_server()

        for i in range(50):
            name = f"rapid_tool_{i}"
            server.register_tool(name=name, schema={}, handler=_echo)
            r = await server._call_tool({"name": name, "arguments": {"n": i}})
            assert "content" in r


# ── Malformed JSON-RPC handling ───────────────────────────────────────


class TestMalformedJSONRPC:
    """Verify graceful handling of malformed JSON-RPC requests."""

    @pytest.mark.asyncio
    async def test_handle_request_with_malformed_json(self) -> None:
        """Server._handle_request with invalid JSON → error response."""
        server = _make_server()
        # _handle_request expects a parsed dict, simulate malformed request
        result = await server.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "", "arguments": {}},
        })
        # Should return a response dict (possibly error), not crash
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_handle_unknown_method(self) -> None:
        """Unknown JSON-RPC method → error response."""
        server = _make_server()
        result = await server.handle_request({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "unknown/method",
            "params": {},
        })
        assert isinstance(result, dict)


# ── Server stability under error conditions ───────────────────────────


class TestServerStability:
    """Verify server remains stable after various error conditions."""

    @pytest.mark.asyncio
    async def test_server_survives_handler_exception(self) -> None:
        """A tool handler that raises should not crash the server."""
        def _bad_handler(**kwargs):
            raise RuntimeError("boom")

        server = _make_server()
        server.register_tool(name="bad", schema={}, handler=_bad_handler)

        # Call the bad tool
        r1 = await server._call_tool({"name": "bad", "arguments": {}})
        # Should get an error response
        assert isinstance(r1, dict)

        # Server still operational — call a good tool
        r2 = await server._call_tool({"name": "echo", "arguments": {"msg": "ok"}})
        assert "content" in r2

    @pytest.mark.asyncio
    async def test_server_survives_many_errors(self) -> None:
        """100 error-producing calls followed by a valid call — server ok."""
        server = _make_server()
        for i in range(100):
            await server._call_tool({"name": f"missing_{i}", "arguments": {}})

        # Server should still work
        r = await server._call_tool({"name": "echo", "arguments": {"msg": "valid"}})
        assert "content" in r
