"""Tests for MCP concurrent tool operations (Stream 4).

Verifies thread-safety and correctness under concurrent load:
- 50 concurrent call_tool() invocations
- 20 concurrent tool registrations
- Mixed concurrent read/write (register + list_tools + execute)
- Concurrent registry access consistency
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import threading

import pytest

from codomyrmex.model_context_protocol.schemas.mcp_schemas import (
    MCPToolCall,
    MCPToolRegistry,
    MCPToolResult,
)
from codomyrmex.model_context_protocol.transport.server import (
    MCPServer,
    MCPServerConfig,
)

# ── Helpers ───────────────────────────────────────────────────────────


def _echo_handler(**kwargs):
    """Simple tool handler that echoes arguments."""
    return kwargs


def _slow_handler(**kwargs):
    """Handler that simulates work."""
    import time
    time.sleep(0.01)
    return {"ok": True}


def _make_registry_with_tools(n: int = 10) -> MCPToolRegistry:
    """Build a registry pre-loaded with N echo tools."""
    reg = MCPToolRegistry()
    for i in range(n):
        reg.register(
            f"tool_{i}",
            schema={"type": "object", "properties": {"x": {"type": "integer"}}},
            handler=_echo_handler,
        )
    return reg


# ── Concurrent call_tool ─────────────────────────────────────────────


class TestConcurrentCallTool:
    """Verify tool execution under concurrent load."""

    def test_50_concurrent_executions(self) -> None:
        """50 threads each execute a tool — all should succeed."""
        reg = _make_registry_with_tools(5)
        results: list[MCPToolResult] = []
        errors: list[Exception] = []

        def _call(idx: int) -> None:
            try:
                call = MCPToolCall(tool_name=f"tool_{idx % 5}", arguments={"x": idx})
                result = reg.execute(call)
                results.append(result)
            except Exception as e:
                errors.append(e)

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
            futures = [pool.submit(_call, i) for i in range(50)]
            concurrent.futures.wait(futures)

        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results) == 50
        assert all(r.status == "success" for r in results)

    def test_concurrent_executions_return_correct_data(self) -> None:
        """Each concurrent call returns its own arguments, not another's."""
        reg = MCPToolRegistry()
        reg.register("echo", schema={}, handler=_echo_handler)
        results: list[MCPToolResult] = []

        def _call(val: int) -> None:
            call = MCPToolCall(tool_name="echo", arguments={"value": val})
            results.append(reg.execute(call))

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(_call, i) for i in range(20)]
            concurrent.futures.wait(futures)

        returned_values = sorted(
            r.data["result"]["value"] for r in results if r.status == "success"
        )
        assert returned_values == list(range(20))


# ── Concurrent registrations ─────────────────────────────────────────


class TestConcurrentRegistrations:
    """Verify tool registration under concurrent load."""

    def test_20_concurrent_registrations(self) -> None:
        """20 threads each register a unique tool — all should be visible."""
        reg = MCPToolRegistry()
        barrier = threading.Barrier(20)

        def _register(idx: int) -> None:
            barrier.wait()
            reg.register(
                f"concurrent_tool_{idx}",
                schema={"type": "object"},
                handler=_echo_handler,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
            futures = [pool.submit(_register, i) for i in range(20)]
            concurrent.futures.wait(futures)

        tools = reg.list_tools()
        assert len(tools) == 20
        for i in range(20):
            assert f"concurrent_tool_{i}" in tools

    def test_concurrent_register_and_unregister(self) -> None:
        """Register and unregister concurrently without crashing."""
        reg = _make_registry_with_tools(20)
        errors: list[Exception] = []

        def _unregister(idx: int) -> None:
            try:
                reg.unregister(f"tool_{idx}")
            except Exception as e:
                errors.append(e)

        def _register(idx: int) -> None:
            try:
                reg.register(f"new_tool_{idx}", schema={}, handler=_echo_handler)
            except Exception as e:
                errors.append(e)

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
            unreg_futures = [pool.submit(_unregister, i) for i in range(10)]
            reg_futures = [pool.submit(_register, i) for i in range(10)]
            concurrent.futures.wait(unreg_futures + reg_futures)

        assert len(errors) == 0


# ── Mixed read/write ─────────────────────────────────────────────────


class TestMixedReadWrite:
    """Test concurrent reads and writes on the registry."""

    def test_mixed_register_list_execute(self) -> None:
        """Interleave registrations, listings, and executions."""
        reg = _make_registry_with_tools(5)
        errors: list[Exception] = []

        def _reader() -> None:
            for _ in range(20):
                try:
                    reg.list_tools()
                except Exception as e:
                    errors.append(e)

        def _writer(idx: int) -> None:
            try:
                reg.register(f"new_{idx}", schema={}, handler=_echo_handler)
            except Exception as e:
                errors.append(e)

        def _executor(idx: int) -> None:
            try:
                call = MCPToolCall(tool_name=f"tool_{idx % 5}", arguments={})
                reg.execute(call)
            except Exception as e:
                errors.append(e)

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as pool:
            futures = []
            futures.extend(pool.submit(_reader) for _ in range(10))
            futures.extend(pool.submit(_writer, i) for i in range(10))
            futures.extend(pool.submit(_executor, i) for i in range(10))
            concurrent.futures.wait(futures)

        assert len(errors) == 0


# ── Async concurrent call_tool on MCPServer ───────────────────────────


class TestAsyncConcurrentServer:
    """Verify MCPServer._call_tool under concurrent async load."""

    @pytest.mark.asyncio
    async def test_concurrent_async_call_tool(self) -> None:
        """Run 20 concurrent _call_tool invocations on a real MCPServer."""
        config = MCPServerConfig(warm_up=False)
        server = MCPServer(config=config)
        server.register_tool(
            name="async_echo",
            schema={"type": "object", "properties": {"n": {"type": "integer"}}},
            handler=_echo_handler,
        )

        async def _call(n: int) -> dict:
            return await server._call_tool({"name": "async_echo", "arguments": {"n": n}})

        results = await asyncio.gather(*[_call(i) for i in range(20)])
        assert len(results) == 20
        for r in results:
            assert "content" in r

    @pytest.mark.asyncio
    async def test_concurrent_call_with_missing_tool(self) -> None:
        """Call non-existent tools concurrently → structured errors."""
        config = MCPServerConfig(warm_up=False)
        server = MCPServer(config=config)

        async def _call(n: int) -> dict:
            return await server._call_tool({"name": f"missing_{n}", "arguments": {}})

        results = await asyncio.gather(*[_call(i) for i in range(10)])
        for r in results:
            assert "isError" in r or "error" in str(r).lower()
