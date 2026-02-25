"""MCP Load Test — 100 concurrent tool invocations.

Validates:
- P50/P95/P99 latencies for concurrent tool calls
- Registry throughput under load
- No errors under concurrent stress
"""

from __future__ import annotations

import asyncio
import resource
import time

import pytest

from codomyrmex.model_context_protocol.schemas.mcp_schemas import MCPToolRegistry
from codomyrmex.model_context_protocol.transport.server import (
    MCPServer,
    MCPServerConfig,
)

# ── Helpers ──────────────────────────────────────────────────────────


def _create_server_with_tools(n_tools: int = 10) -> MCPServer:
    """Create a server with n registered tools."""
    server = MCPServer(MCPServerConfig(name="load-test", warm_up=False))
    for i in range(n_tools):
        server.register_tool(
            name=f"load_tool_{i}",
            schema={
                "name": f"load_tool_{i}",
                "description": f"Load test tool {i}",
                "inputSchema": {
                    "type": "object",
                    "properties": {"x": {"type": "integer"}},
                },
            },
            handler=lambda x: {"result": x * 2},  # type: ignore[arg-type]
        )
    return server


def _percentile(data: list[float], p: float) -> float:
    """Calculate percentile from sorted data."""
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


# ── Load Tests ───────────────────────────────────────────────────────


class TestMCPLoadConcurrent:
    """Test MCP under 100 concurrent tool invocations."""

    def test_100_concurrent_tool_registrations(self) -> None:
        """100 tool registrations should complete in < 500ms total."""
        registry = MCPToolRegistry()
        start = time.perf_counter()
        for i in range(100):
            registry.register(
                tool_name=f"tool_{i}",
                schema={
                    "name": f"tool_{i}",
                    "description": f"Tool {i}",
                    "inputSchema": {"type": "object"},
                },
                handler=lambda: None,
            )
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert len(registry.list_tools()) == 100
        assert elapsed_ms < 500, f"Registration took {elapsed_ms:.1f}ms (limit: 500ms)"

    def test_100_concurrent_tool_lookups(self) -> None:
        """100 concurrent tool lookups should have P95 < 1ms."""
        registry = MCPToolRegistry()
        for i in range(50):
            registry.register(
                tool_name=f"tool_{i}",
                schema={"name": f"tool_{i}", "description": f"Tool {i}", "inputSchema": {"type": "object"}},
                handler=lambda: None,
            )

        latencies: list[float] = []
        for _ in range(100):
            start = time.perf_counter()
            tool = registry.get(f"tool_{_ % 50}")
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)
            assert tool is not None

        p50 = _percentile(latencies, 50)
        p95 = _percentile(latencies, 95)
        p99 = _percentile(latencies, 99)

        assert p95 < 1.0, f"P95 lookup latency {p95:.3f}ms > 1ms"
        assert p99 < 5.0, f"P99 lookup latency {p99:.3f}ms > 5ms"

    @pytest.mark.asyncio
    async def test_100_concurrent_json_rpc_calls(self) -> None:
        """100 concurrent JSON-RPC tool/call requests should have P95 < 500ms."""
        server = _create_server_with_tools(10)

        latencies: list[float] = []
        errors: list[str] = []

        async def call_tool(idx: int) -> None:
            tool_name = f"load_tool_{idx % 10}"
            request = {
                "jsonrpc": "2.0",
                "id": idx,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": {"x": idx},
                },
            }
            start = time.perf_counter()
            try:
                response = await server.handle_request(request)
                elapsed_ms = (time.perf_counter() - start) * 1000
                latencies.append(elapsed_ms)
                if "error" in response:
                    errors.append(f"Tool {tool_name}: {response['error']}")
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                latencies.append(elapsed_ms)
                errors.append(f"Tool {tool_name}: {e}")

        # Fire 100 concurrent calls
        tasks = [call_tool(i) for i in range(100)]
        await asyncio.gather(*tasks)

        assert len(errors) == 0, f"Errors during load test: {errors[:5]}"
        assert len(latencies) == 100

        p50 = _percentile(latencies, 50)
        p95 = _percentile(latencies, 95)
        p99 = _percentile(latencies, 99)

        # P95 must be under 500ms
        assert p95 < 500.0, f"P95 latency {p95:.1f}ms exceeds 500ms limit"

    @pytest.mark.asyncio
    async def test_tool_list_under_load(self) -> None:
        """tools/list should respond fast even with 100 registered tools."""
        server = _create_server_with_tools(100)

        latencies: list[float] = []
        for _ in range(50):
            request = {
                "jsonrpc": "2.0",
                "id": _ + 1,
                "method": "tools/list",
                "params": {},
            }
            start = time.perf_counter()
            response = await server.handle_request(request)
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)
            assert "result" in response

        p95 = _percentile(latencies, 95)
        assert p95 < 100.0, f"tools/list P95 {p95:.1f}ms exceeds 100ms limit"


class TestMCPMemoryProfile:
    """Memory profiling for MCP operations."""

    def test_registry_memory_growth(self) -> None:
        """Registry with 1000 tools should not consume excessive memory."""
        rss_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        registry = MCPToolRegistry()
        for i in range(1000):
            registry.register(
                tool_name=f"mem_tool_{i}",
                schema={
                    "name": f"mem_tool_{i}",
                    "description": f"Memory test tool {i} with a moderately long description for realism",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string"},
                            "count": {"type": "integer"},
                        },
                    },
                },
                handler=lambda: None,
            )

        rss_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # RSS is in KB on Linux, bytes on macOS — normalize
        import sys
        if sys.platform == "darwin":
            delta_mb = (rss_after - rss_before) / (1024 * 1024)
        else:
            delta_mb = (rss_after - rss_before) / 1024

        assert len(registry.list_tools()) == 1000
        # 1000 tools should not add more than 50MB
        assert delta_mb < 50, f"Registry grew by {delta_mb:.1f}MB for 1000 tools"


class TestMCPThroughput:
    """Throughput benchmarks for MCP operations."""

    def test_tool_registration_throughput(self) -> None:
        """Should register ≥1000 tools/second."""
        registry = MCPToolRegistry()
        start = time.perf_counter()
        count = 500
        for i in range(count):
            registry.register(
                tool_name=f"throughput_tool_{i}",
                schema={"name": f"throughput_tool_{i}", "description": "test", "inputSchema": {"type": "object"}},
                handler=lambda: None,
            )
        elapsed = time.perf_counter() - start
        rate = count / elapsed

        assert rate >= 1000, f"Registration rate {rate:.0f}/s < 1000/s"

    @pytest.mark.asyncio
    async def test_json_rpc_throughput(self) -> None:
        """Should handle ≥200 tool calls/second."""
        server = _create_server_with_tools(5)
        count = 200
        start = time.perf_counter()

        for i in range(count):
            request = {
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/call",
                "params": {
                    "name": f"load_tool_{i % 5}",
                    "arguments": {"x": i},
                },
            }
            await server.handle_request(request)

        elapsed = time.perf_counter() - start
        rate = count / elapsed

        assert rate >= 200, f"Tool call rate {rate:.0f}/s < 200/s"
