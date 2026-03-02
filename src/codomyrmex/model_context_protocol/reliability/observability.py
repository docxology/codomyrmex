"""MCP observability hooks — Prometheus-style counters and metrics resource.

Instruments ``MCPServer._call_tool`` with pre/post hooks that track:
- ``mcp_tool_call_total``: Total tool calls by tool name.
- ``mcp_tool_duration_seconds``: Cumulative execution time by tool name.
- ``mcp_tool_errors_total``: Total errors by tool name and error code.

Exposes a ``codomyrmex://mcp/metrics`` resource with current counters.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolMetrics:
    """Per-tool metric counters."""
    calls: int = 0
    errors: int = 0
    total_duration: float = 0.0
    last_call_time: float | None = None


class MCPObservabilityHooks:
    """Prometheus-style counters for MCP tool calls.

    Usage::

        hooks = MCPObservabilityHooks()

        # Before calling a tool:
        hooks.on_tool_call_start("search_code")

        # After successful call:
        hooks.on_tool_call_end("search_code", duration=0.15, error=None)

        # After failed call:
        hooks.on_tool_call_end("search_code", duration=0.05, error="timeout")

        # Get metrics dict:
        print(hooks.get_metrics())
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tool_metrics: dict[str, ToolMetrics] = {}
        self._global_calls: int = 0
        self._global_errors: int = 0
        self._global_duration: float = 0.0

    # ------------------------------------------------------------------
    # Hook API
    # ------------------------------------------------------------------

    def on_tool_call_start(self, tool_name: str) -> float:
        """Record start of a tool call. Returns start timestamp."""
        return time.monotonic()

    def on_tool_call_end(
        self,
        tool_name: str,
        *,
        duration: float,
        error: str | None = None,
    ) -> None:
        """Record completion of a tool call."""
        with self._lock:
            if tool_name not in self._tool_metrics:
                self._tool_metrics[tool_name] = ToolMetrics()

            metrics = self._tool_metrics[tool_name]
            metrics.calls += 1
            metrics.total_duration += duration
            metrics.last_call_time = time.time()
            self._global_calls += 1
            self._global_duration += duration

            if error is not None:
                metrics.errors += 1
                self._global_errors += 1

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get_metrics(self) -> dict[str, Any]:
        """Return all metrics as a plain dict (JSON-serialisable)."""
        with self._lock:
            return {
                "mcp_tool_call_total": self._global_calls,
                "mcp_tool_errors_total": self._global_errors,
                "mcp_tool_duration_seconds": round(self._global_duration, 6),
                "per_tool": {
                    name: {
                        "calls": m.calls,
                        "errors": m.errors,
                        "total_duration": round(m.total_duration, 6),
                        "avg_duration": round(m.total_duration / m.calls, 6) if m.calls > 0 else 0,
                    }
                    for name, m in self._tool_metrics.items()
                },
            }

    def get_tool_metrics(self, tool_name: str) -> ToolMetrics | None:
        """Get metrics for a specific tool."""
        return self._tool_metrics.get(tool_name)

    def get_metrics_json(self) -> str:
        """Return metrics as a JSON string (for MCP resource)."""
        return json.dumps(self.get_metrics(), indent=2)

    def reset(self) -> None:
        """Reset all counters."""
        with self._lock:
            self._tool_metrics.clear()
            self._global_calls = 0
            self._global_errors = 0
            self._global_duration = 0.0


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_global_hooks: MCPObservabilityHooks | None = None


def get_mcp_observability_hooks() -> MCPObservabilityHooks:
    """Return the global MCPObservabilityHooks singleton."""
    global _global_hooks
    if _global_hooks is None:
        _global_hooks = MCPObservabilityHooks()
    return _global_hooks


__all__ = [
    "MCPObservabilityHooks",
    "ToolMetrics",
    "get_mcp_observability_hooks",
]
