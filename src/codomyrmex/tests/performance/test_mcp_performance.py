"""MCP performance benchmarks using pytest-benchmark (Stream 7).

Establishes quantitative baselines for:
- MCP server creation
- Tool registry operations
- Tool call overhead (without actual tool execution)
- Validation overhead
- Observability hooks overhead
- @with_retry decorator overhead (no-retry path)
- AsyncParallelRunner overhead
- AsyncScheduler overhead
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import pytest

from codomyrmex.model_context_protocol.server import MCPServer, MCPServerConfig
from codomyrmex.model_context_protocol.observability import MCPObservabilityHooks
from codomyrmex.model_context_protocol.validation import validate_tool_arguments
from codomyrmex.orchestrator.retry_policy import with_retry
from codomyrmex.orchestrator.async_runner import AsyncParallelRunner
from codomyrmex.orchestrator.async_scheduler import AsyncScheduler


# ── MCP Server Creation ──────────────────────────────────────────────


class TestMCPServerCreation:
    """Benchmark MCP server instantiation."""

    def test_server_creation_speed(self, benchmark) -> None:
        """MCPServerConfig + MCPServer.__init__ should be fast."""
        def create_server():
            config = MCPServerConfig(name="bench", warm_up=False)
            return MCPServer(config)

        result = benchmark.pedantic(create_server, rounds=50, warmup_rounds=5)
        assert result is not None

    def test_tool_registration_speed(self, benchmark) -> None:
        """Registering a tool should be sub-millisecond."""
        server = MCPServer(MCPServerConfig(name="bench", warm_up=False))

        def register_tool():
            server.register_tool(
                name="bench_tool",
                schema={"name": "bench_tool", "description": "test", "inputSchema": {"type": "object"}},
                handler=lambda tc: {"status": "ok"},
            )

        benchmark.pedantic(register_tool, rounds=100, warmup_rounds=5)


# ── Validation Overhead ──────────────────────────────────────────────


class TestValidationOverhead:
    """Benchmark argument validation."""

    def test_validation_overhead(self, benchmark) -> None:
        """validate_tool_arguments should add < 1ms overhead."""
        schema = {
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            }
        }
        args = {"query": "hello", "limit": 10}

        result = benchmark.pedantic(
            lambda: validate_tool_arguments("test_tool", args, schema),
            rounds=200,
            warmup_rounds=10,
        )
        assert result is not None

    def test_validation_empty_schema(self, benchmark) -> None:
        """Empty schema validation should be near-zero."""
        result = benchmark.pedantic(
            lambda: validate_tool_arguments("test_tool", {}, {}),
            rounds=200,
            warmup_rounds=10,
        )
        assert result is not None


# ── Observability Hooks Overhead ──────────────────────────────────────


class TestObservabilityOverhead:
    """Benchmark MCPObservabilityHooks — should add negligible overhead."""

    def test_on_tool_call_end_overhead(self, benchmark) -> None:
        """on_tool_call_end should add < 0.05ms per call."""
        hooks = MCPObservabilityHooks()

        def call_hook():
            hooks.on_tool_call_end("bench_tool", duration=0.001, error=None)

        benchmark.pedantic(call_hook, rounds=1000, warmup_rounds=50)

    def test_get_metrics_overhead(self, benchmark) -> None:
        """get_metrics should be fast even with many tools."""
        hooks = MCPObservabilityHooks()
        for i in range(50):
            hooks.on_tool_call_end(f"tool_{i}", duration=0.01, error=None)

        benchmark.pedantic(hooks.get_metrics, rounds=200, warmup_rounds=10)


# ── Retry Decorator Overhead ─────────────────────────────────────────


class TestRetryDecoratorOverhead:
    """Benchmark @with_retry overhead on the no-retry path."""

    def test_sync_no_retry_overhead(self, benchmark) -> None:
        """@with_retry on a no-op sync function should add < 0.1ms."""

        @with_retry(max_attempts=3, base_delay=0.01)
        def noop():
            return 42

        result = benchmark.pedantic(noop, rounds=500, warmup_rounds=20)
        assert result == 42

    def test_async_no_retry_overhead(self, benchmark) -> None:
        """@with_retry on a no-op async function should add < 0.1ms."""

        @with_retry(max_attempts=3, base_delay=0.01)
        async def async_noop():
            return 42

        def run_async_noop():
            return asyncio.get_event_loop().run_until_complete(async_noop())

        result = benchmark.pedantic(run_async_noop, rounds=100, warmup_rounds=5)
        assert result == 42


# ── AsyncParallelRunner Overhead ─────────────────────────────────────


class TestAsyncRunnerOverhead:
    """Benchmark AsyncParallelRunner."""


    def test_runner_10_noop_tasks(self, benchmark) -> None:
        """10 no-op tasks should complete quickly."""

        async def noop_task():
            return "done"

        async def run_10():
            runner = AsyncParallelRunner(max_concurrency=4)
            tasks = [(f"task_{i}", noop_task, ()) for i in range(10)]
            return await runner.run(tasks)

        def do_run():
            return asyncio.get_event_loop().run_until_complete(run_10())

        result = benchmark.pedantic(do_run, rounds=20, warmup_rounds=3)
        assert result.total == 10

    def test_runner_100_noop_tasks(self, benchmark) -> None:
        """100 no-op tasks with bounded concurrency."""

        async def noop_task():
            return "done"

        async def run_100():
            runner = AsyncParallelRunner(max_concurrency=8)
            tasks = [(f"task_{i}", noop_task, ()) for i in range(100)]
            return await runner.run(tasks)

        def do_run():
            return asyncio.get_event_loop().run_until_complete(run_100())

        result = benchmark.pedantic(do_run, rounds=10, warmup_rounds=2)
        assert result.total == 100


# ── AsyncScheduler Overhead ──────────────────────────────────────────


class TestAsyncSchedulerOverhead:
    """Benchmark AsyncScheduler."""

    def test_scheduler_10_jobs(self, benchmark) -> None:
        """10 no-op jobs should complete quickly."""

        async def noop_job():
            return "done"

        async def run_10():
            sched = AsyncScheduler(max_concurrency=4)
            for i in range(10):
                sched.schedule(noop_job, name=f"job_{i}")
            return await sched.run_all()

        def do_run():
            return asyncio.get_event_loop().run_until_complete(run_10())

        benchmark.pedantic(do_run, rounds=20, warmup_rounds=3)

    def test_scheduler_100_jobs(self, benchmark) -> None:
        """100 no-op jobs with max_concurrency=4 should complete in < 1s."""

        async def noop_job():
            return "done"

        async def run_100():
            sched = AsyncScheduler(max_concurrency=4)
            for i in range(100):
                sched.schedule(noop_job, name=f"job_{i}", priority=i % 5)
            return await sched.run_all()

        def do_run():
            return asyncio.get_event_loop().run_until_complete(run_100())

        result = benchmark.pedantic(do_run, rounds=5, warmup_rounds=1)
        assert result is not None
