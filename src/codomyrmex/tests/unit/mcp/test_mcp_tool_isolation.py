"""Tests for MCP tool execution isolation (Stream 4).

Verifies:
- Exception in one tool does not affect others
- Global state changes in one tool do not leak to others
- Timeout in one tool does not block others
- Handler failures are properly contained
"""

from __future__ import annotations

import asyncio
import time

import pytest

from codomyrmex.model_context_protocol.schemas.mcp_schemas import (
    MCPToolCall,
    MCPToolRegistry,
)
from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig


# ── Helpers ───────────────────────────────────────────────────────────


_GLOBAL_STATE: dict[str, int] = {}


def _echo(**kwargs):
    return kwargs


def _raises(**kwargs):
    raise RuntimeError("intentional failure")


def _mutates_global(**kwargs):
    """Tool that mutates global state."""
    key = kwargs.get("key", "default")
    _GLOBAL_STATE[key] = _GLOBAL_STATE.get(key, 0) + 1
    return {"count": _GLOBAL_STATE[key]}


def _slow(duration: float = 1.0, **kwargs):
    """Tool that sleeps for a specified duration."""
    time.sleep(duration)
    return {"slept": duration}


# ── Exception isolation ───────────────────────────────────────────────


class TestExceptionIsolation:
    """Verify that handler exceptions don't affect other tools."""

    def test_exception_returns_failure_result(self) -> None:
        """A raising handler produces a failure MCPToolResult."""
        reg = MCPToolRegistry()
        reg.register("bad", schema={}, handler=_raises)
        result = reg.execute(MCPToolCall(tool_name="bad", arguments={}))
        assert result.status == "failure"
        assert result.error is not None
        assert "intentional failure" in result.error.error_message

    def test_exception_does_not_affect_next_call(self) -> None:
        """After a tool raises, the next tool call succeeds normally."""
        reg = MCPToolRegistry()
        reg.register("bad", schema={}, handler=_raises)
        reg.register("good", schema={}, handler=_echo)

        # First call: fails
        r1 = reg.execute(MCPToolCall(tool_name="bad", arguments={}))
        assert r1.status == "failure"

        # Second call: succeeds
        r2 = reg.execute(MCPToolCall(tool_name="good", arguments={"x": 42}))
        assert r2.status == "success"
        assert r2.data["result"]["x"] == 42

    @pytest.mark.asyncio
    async def test_server_exception_isolation(self) -> None:
        """Server-level _call_tool: exception in one tool doesn't affect others."""
        config = MCPServerConfig(warm_up=False)
        server = MCPServer(config=config)
        server.register_tool(name="bad", schema={}, handler=_raises)
        server.register_tool(name="good", schema={}, handler=_echo)

        r1 = await server._call_tool({"name": "bad", "arguments": {}})
        r2 = await server._call_tool({"name": "good", "arguments": {"val": 1}})

        # r1 should be an error response
        assert isinstance(r1, dict)
        # r2 should be a success response
        assert "content" in r2

    def test_multiple_exception_types(self) -> None:
        """Different exception types are all properly isolated."""
        def _value_error(**kwargs):
            raise ValueError("bad value")

        def _type_error(**kwargs):
            raise TypeError("wrong type")

        def _key_error(**kwargs):
            raise KeyError("missing_key")

        reg = MCPToolRegistry()
        reg.register("ve", schema={}, handler=_value_error)
        reg.register("te", schema={}, handler=_type_error)
        reg.register("ke", schema={}, handler=_key_error)
        reg.register("ok", schema={}, handler=_echo)

        for name in ("ve", "te", "ke"):
            r = reg.execute(MCPToolCall(tool_name=name, arguments={}))
            assert r.status == "failure"

        r_ok = reg.execute(MCPToolCall(tool_name="ok", arguments={"x": 1}))
        assert r_ok.status == "success"


# ── Global state isolation ────────────────────────────────────────────


class TestGlobalStateIsolation:
    """Verify tools don't leak state to each other."""

    def test_separate_keys_dont_interfere(self) -> None:
        """Two tools mutating different global keys work independently."""
        _GLOBAL_STATE.clear()
        reg = MCPToolRegistry()
        reg.register("mutator", schema={}, handler=_mutates_global)

        r1 = reg.execute(MCPToolCall(tool_name="mutator", arguments={"key": "a"}))
        r2 = reg.execute(MCPToolCall(tool_name="mutator", arguments={"key": "b"}))

        assert r1.data["result"]["count"] == 1
        assert r2.data["result"]["count"] == 1

    def test_same_key_accumulates(self) -> None:
        """Multiple calls with same key show accumulation (expected behavior)."""
        _GLOBAL_STATE.clear()
        reg = MCPToolRegistry()
        reg.register("mutator", schema={}, handler=_mutates_global)

        for i in range(5):
            r = reg.execute(MCPToolCall(tool_name="mutator", arguments={"key": "shared"}))

        assert r.data["result"]["count"] == 5

    def test_echo_has_no_side_effects(self) -> None:
        """The echo handler produces no side effects."""
        _GLOBAL_STATE.clear()
        reg = MCPToolRegistry()
        reg.register("echo", schema={}, handler=_echo)

        for i in range(10):
            reg.execute(MCPToolCall(tool_name="echo", arguments={"x": i}))

        assert _GLOBAL_STATE == {}


# ── Timeout isolation ─────────────────────────────────────────────────


class TestTimeoutIsolation:
    """Verify tool timeouts don't block other tools."""

    @pytest.mark.asyncio
    async def test_timeout_does_not_block_next_call(self) -> None:
        """After a tool times out, the next call still works."""
        config = MCPServerConfig(
            warm_up=False,
            default_tool_timeout=0.1,  # 100ms timeout
        )
        server = MCPServer(config=config)
        server.register_tool(name="slow", schema={}, handler=lambda **kw: _slow(1.0))
        server.register_tool(name="fast", schema={}, handler=_echo)

        # This should timeout
        r1 = await server._call_tool({"name": "slow", "arguments": {}})
        assert isinstance(r1, dict)
        # Check it was a timeout error
        content_str = str(r1)
        assert "timeout" in content_str.lower() or "isError" in content_str

        # This should succeed quickly
        t0 = time.monotonic()
        r2 = await server._call_tool({"name": "fast", "arguments": {"x": 1}})
        elapsed = time.monotonic() - t0
        assert "content" in r2
        assert elapsed < 1.0  # Should not be blocked by the slow tool

    @pytest.mark.asyncio
    async def test_concurrent_fast_and_slow_tools(self) -> None:
        """Fast tools complete while a slow tool is timing out."""
        config = MCPServerConfig(
            warm_up=False,
            default_tool_timeout=0.2,
        )
        server = MCPServer(config=config)
        server.register_tool(name="slow", schema={}, handler=lambda **kw: _slow(2.0))
        server.register_tool(name="fast", schema={}, handler=_echo)

        async def _call_slow() -> dict:
            return await server._call_tool({"name": "slow", "arguments": {}})

        async def _call_fast(n: int) -> dict:
            return await server._call_tool({"name": "fast", "arguments": {"n": n}})

        # Run one slow + 5 fast concurrently
        results = await asyncio.gather(
            _call_slow(),
            *[_call_fast(i) for i in range(5)],
        )

        # Slow should have timed out
        slow_result = results[0]
        assert isinstance(slow_result, dict)

        # All fast should have succeeded
        for fast_result in results[1:]:
            assert "content" in fast_result

    @pytest.mark.asyncio
    async def test_per_tool_timeout_isolation(self) -> None:
        """Tools with different timeouts don't interfere."""
        config = MCPServerConfig(
            warm_up=False,
            default_tool_timeout=0.05,
            per_tool_timeouts={"patient_tool": 2.0},
        )
        server = MCPServer(config=config)
        server.register_tool(
            name="patient_tool",
            schema={},
            handler=lambda **kw: _slow(0.1),
        )
        server.register_tool(
            name="impatient_tool",
            schema={},
            handler=lambda **kw: _slow(0.2),
        )

        # patient_tool has 2s timeout, sleeping 0.1s → success
        r1 = await server._call_tool({"name": "patient_tool", "arguments": {}})
        assert "content" in r1

        # impatient_tool has 0.05s timeout, sleeping 0.2s → timeout
        r2 = await server._call_tool({"name": "impatient_tool", "arguments": {}})
        content_str = str(r2)
        assert "timeout" in content_str.lower() or "isError" in content_str
