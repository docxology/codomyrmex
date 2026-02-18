"""Tests for MCPObservabilityHooks (Stream 6).

Verifies:
- Tool call counters increment correctly
- Duration tracking
- Error counting by tool name
- JSON metrics resource output
- Structured JSON toggle functions
"""

from __future__ import annotations

import json
import logging

import pytest

from codomyrmex.model_context_protocol.observability import (
    MCPObservabilityHooks,
    ToolMetrics,
    get_mcp_observability_hooks,
)
from codomyrmex.logging_monitoring.core.logger_config import (
    JSONFormatter,
    enable_structured_json,
    configure_all_structured,
)


# ── Basic counters ────────────────────────────────────────────────────


class TestBasicCounters:
    """Verify call and error counters."""

    def test_single_tool_call_increments(self) -> None:
        hooks = MCPObservabilityHooks()
        hooks.on_tool_call_end("search_code", duration=0.1, error=None)

        m = hooks.get_metrics()
        assert m["mcp_tool_call_total"] == 1
        assert m["mcp_tool_errors_total"] == 0
        assert m["per_tool"]["search_code"]["calls"] == 1

    def test_multiple_tool_calls(self) -> None:
        hooks = MCPObservabilityHooks()
        for _ in range(5):
            hooks.on_tool_call_end("read_file", duration=0.05, error=None)
        for _ in range(3):
            hooks.on_tool_call_end("write_file", duration=0.1, error=None)

        m = hooks.get_metrics()
        assert m["mcp_tool_call_total"] == 8
        assert m["per_tool"]["read_file"]["calls"] == 5
        assert m["per_tool"]["write_file"]["calls"] == 3

    def test_error_counting(self) -> None:
        hooks = MCPObservabilityHooks()
        hooks.on_tool_call_end("bad_tool", duration=0.01, error="timeout")
        hooks.on_tool_call_end("bad_tool", duration=0.02, error=None)
        hooks.on_tool_call_end("bad_tool", duration=0.01, error="crash")

        m = hooks.get_metrics()
        assert m["mcp_tool_errors_total"] == 2
        assert m["per_tool"]["bad_tool"]["errors"] == 2
        assert m["per_tool"]["bad_tool"]["calls"] == 3


# ── Duration tracking ────────────────────────────────────────────────


class TestDurationTracking:
    """Verify cumulative duration tracking."""

    def test_total_duration(self) -> None:
        hooks = MCPObservabilityHooks()
        hooks.on_tool_call_end("tool_a", duration=0.1, error=None)
        hooks.on_tool_call_end("tool_a", duration=0.2, error=None)

        m = hooks.get_metrics()
        assert abs(m["mcp_tool_duration_seconds"] - 0.3) < 0.001
        assert abs(m["per_tool"]["tool_a"]["total_duration"] - 0.3) < 0.001

    def test_average_duration(self) -> None:
        hooks = MCPObservabilityHooks()
        hooks.on_tool_call_end("tool_b", duration=0.1, error=None)
        hooks.on_tool_call_end("tool_b", duration=0.3, error=None)

        avg = hooks.get_metrics()["per_tool"]["tool_b"]["avg_duration"]
        assert abs(avg - 0.2) < 0.001

    def test_start_returns_timestamp(self) -> None:
        hooks = MCPObservabilityHooks()
        t0 = hooks.on_tool_call_start("tool_c")
        assert isinstance(t0, float)
        assert t0 > 0


# ── JSON metrics resource ────────────────────────────────────────────


class TestMetricsResource:
    """Verify JSON serialisation for MCP resource."""

    def test_get_metrics_json(self) -> None:
        hooks = MCPObservabilityHooks()
        hooks.on_tool_call_end("x", duration=0.1, error=None)

        j = hooks.get_metrics_json()
        d = json.loads(j)
        assert d["mcp_tool_call_total"] == 1

    def test_get_tool_metrics(self) -> None:
        hooks = MCPObservabilityHooks()
        hooks.on_tool_call_end("specific_tool", duration=0.5, error=None)

        tm = hooks.get_tool_metrics("specific_tool")
        assert tm is not None
        assert tm.calls == 1
        assert abs(tm.total_duration - 0.5) < 0.001

    def test_nonexistent_tool_returns_none(self) -> None:
        hooks = MCPObservabilityHooks()
        assert hooks.get_tool_metrics("nope") is None


# ── Reset ─────────────────────────────────────────────────────────────


class TestReset:
    """Verify counter reset."""

    def test_reset_clears_all_counters(self) -> None:
        hooks = MCPObservabilityHooks()
        for _ in range(10):
            hooks.on_tool_call_end("tool", duration=0.01, error=None)

        hooks.reset()
        m = hooks.get_metrics()
        assert m["mcp_tool_call_total"] == 0
        assert m["mcp_tool_errors_total"] == 0
        assert m["per_tool"] == {}


# ── Singleton accessor ────────────────────────────────────────────────


class TestSingleton:
    """Verify global singleton."""

    def test_get_mcp_observability_hooks_returns_same_instance(self) -> None:
        h1 = get_mcp_observability_hooks()
        h2 = get_mcp_observability_hooks()
        assert h1 is h2


# ── Structured JSON toggle ───────────────────────────────────────────


class TestStructuredJsonToggle:
    """Verify enable_structured_json and configure_all_structured."""

    def test_enable_structured_json_adds_handler(self) -> None:
        test_logger = logging.getLogger("codomyrmex.test_json_toggle")
        # Remove any existing handlers
        test_logger.handlers.clear()

        enable_structured_json("codomyrmex.test_json_toggle")

        assert len(test_logger.handlers) >= 1
        assert isinstance(test_logger.handlers[0].formatter, JSONFormatter)

    def test_enable_structured_json_converts_existing_handler(self) -> None:
        test_logger = logging.getLogger("codomyrmex.test_json_convert")
        test_logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        test_logger.addHandler(handler)

        enable_structured_json("codomyrmex.test_json_convert")

        assert isinstance(test_logger.handlers[0].formatter, JSONFormatter)

    def test_configure_all_structured(self) -> None:
        # Create a test logger under codomyrmex namespace
        test_logger = logging.getLogger("codomyrmex.test_all_structured")
        test_logger.handlers.clear()
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        test_logger.addHandler(handler)

        configure_all_structured()

        # The test logger's handler should now use JSONFormatter
        assert isinstance(test_logger.handlers[0].formatter, JSONFormatter)
