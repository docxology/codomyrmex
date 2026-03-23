"""MCP tool call-graph collector.

Records every ``@mcp_tool`` invocation with tool name, latency, caller,
and result status.  Provides query methods for building call-graph DAGs.

Example::

    collector = MCPCallGraphCollector()
    collector.record("search_documents", caller="hermes", latency_ms=42.5)

    graph = collector.get_call_graph()
    # {"nodes": [...], "edges": [...]}
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """A recorded MCP tool invocation.

    Attributes:
        tool_name: Name of the invoked tool.
        caller: Identity of the caller (agent name, session ID).
        latency_ms: Wall-clock time in milliseconds.
        timestamp: Unix timestamp of the call.
        success: Whether the call completed without error.
        metadata: Optional extra context.
    """

    tool_name: str
    caller: str = ""
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CallGraphNode:
    """A node in the MCP call graph.

    Attributes:
        name: Tool or caller name.
        node_type: ``"tool"`` or ``"caller"``.
        call_count: Total invocations.
        avg_latency_ms: Mean latency.
        error_count: Number of failed calls.
    """

    name: str
    node_type: str  # "tool" or "caller"
    call_count: int = 0
    avg_latency_ms: float = 0.0
    error_count: int = 0


class MCPCallGraphCollector:
    """Collects MCP tool invocations and builds call-graph DAGs.

    Thread-safe. Designed to run as a singleton within the MCP server process.

    Example::

        collector = MCPCallGraphCollector()
        with collector.trace("search_documents", caller="hermes") as ctx:
            result = do_search(query)
            ctx.set_metadata({"results": len(result)})
    """

    def __init__(self, max_history: int = 10_000) -> None:
        self._history: list[ToolCall] = []
        self._max_history = max_history
        self._lock = threading.Lock()

        # Aggregates
        self._tool_counts: dict[str, int] = defaultdict(int)
        self._tool_latencies: dict[str, list[float]] = defaultdict(list)
        self._tool_errors: dict[str, int] = defaultdict(int)
        self._caller_tools: dict[str, set[str]] = defaultdict(set)

    def record(
        self,
        tool_name: str,
        *,
        caller: str = "",
        latency_ms: float = 0.0,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> ToolCall:
        """Record a tool invocation.

        Args:
            tool_name: Name of the MCP tool.
            caller: Caller identity (agent name).
            latency_ms: Call duration in milliseconds.
            success: Whether the call succeeded.
            metadata: Optional extra context.

        Returns:
            The recorded :class:`ToolCall`.
        """
        call = ToolCall(
            tool_name=tool_name,
            caller=caller,
            latency_ms=latency_ms,
            success=success,
            metadata=metadata or {},
        )

        with self._lock:
            self._history.append(call)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]

            self._tool_counts[tool_name] += 1
            self._tool_latencies[tool_name].append(latency_ms)
            if not success:
                self._tool_errors[tool_name] += 1
            if caller:
                self._caller_tools[caller].add(tool_name)

        return call

    def trace(self, tool_name: str, caller: str = "") -> _TraceContext:
        """Context manager that records a tool invocation with auto-timing.

        Args:
            tool_name: MCP tool name.
            caller: Caller identity.

        Returns:
            A context manager that records the call on exit.
        """
        return _TraceContext(self, tool_name, caller)

    def get_call_graph(self) -> dict[str, Any]:
        """Build a call-graph JSON structure.

        Returns:
            dict with ``nodes`` (list of node dicts) and ``edges``
            (list of ``{source, target, weight}`` dicts).
        """
        with self._lock:
            nodes: list[dict[str, Any]] = []
            edges: list[dict[str, Any]] = []

            # Tool nodes
            for tool, count in sorted(self._tool_counts.items()):
                latencies = self._tool_latencies.get(tool, [])
                avg = sum(latencies) / len(latencies) if latencies else 0.0
                nodes.append(
                    {
                        "id": f"tool:{tool}",
                        "name": tool,
                        "type": "tool",
                        "call_count": count,
                        "avg_latency_ms": round(avg, 2),
                        "error_count": self._tool_errors.get(tool, 0),
                    }
                )

            # Caller nodes and edges
            for caller, tools in sorted(self._caller_tools.items()):
                caller_total = sum(self._tool_counts.get(t, 0) for t in tools)
                nodes.append(
                    {
                        "id": f"caller:{caller}",
                        "name": caller,
                        "type": "caller",
                        "call_count": caller_total,
                    }
                )
                for tool in sorted(tools):
                    edges.append(
                        {
                            "source": f"caller:{caller}",
                            "target": f"tool:{tool}",
                            "weight": self._tool_counts.get(tool, 0),
                        }
                    )

            return {"nodes": nodes, "edges": edges}

    def get_stats(self) -> dict[str, Any]:
        """Return aggregate statistics.

        Returns:
            dict with ``total_calls``, ``unique_tools``, ``unique_callers``,
            ``error_rate``, and ``top_tools``.
        """
        with self._lock:
            total = sum(self._tool_counts.values())
            errors = sum(self._tool_errors.values())
            top = sorted(
                self._tool_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]

            return {
                "total_calls": total,
                "unique_tools": len(self._tool_counts),
                "unique_callers": len(self._caller_tools),
                "error_rate": errors / total if total else 0.0,
                "top_tools": [{"name": name, "count": count} for name, count in top],
            }

    def get_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent tool calls.

        Args:
            limit: Maximum number of calls to return.

        Returns:
            list of call dicts (most recent first).
        """
        with self._lock:
            recent = self._history[-limit:][::-1]
            return [
                {
                    "tool_name": c.tool_name,
                    "caller": c.caller,
                    "latency_ms": c.latency_ms,
                    "timestamp": c.timestamp,
                    "success": c.success,
                }
                for c in recent
            ]

    def clear(self) -> None:
        """Clear all recorded data."""
        with self._lock:
            self._history.clear()
            self._tool_counts.clear()
            self._tool_latencies.clear()
            self._tool_errors.clear()
            self._caller_tools.clear()


class _TraceContext:
    """Context manager for auto-timed tool call recording."""

    def __init__(
        self,
        collector: MCPCallGraphCollector,
        tool_name: str,
        caller: str,
    ) -> None:
        self._collector = collector
        self._tool_name = tool_name
        self._caller = caller
        self._start: float = 0.0
        self._metadata: dict[str, Any] = {}
        self._success = True

    def set_metadata(self, metadata: dict[str, Any]) -> None:
        """set additional metadata for the call."""
        self._metadata.update(metadata)

    def set_error(self) -> None:
        """Mark the call as failed."""
        self._success = False

    def __enter__(self) -> _TraceContext:  # noqa: PYI034
        self._start = time.monotonic()
        return self

    def __exit__(self, exc_type: type | None, *_args: object) -> None:
        latency_ms = (time.monotonic() - self._start) * 1000
        if exc_type is not None:
            self._success = False
        self._collector.record(
            self._tool_name,
            caller=self._caller,
            latency_ms=latency_ms,
            success=self._success,
            metadata=self._metadata,
        )


# Module-level singleton
_default_collector: MCPCallGraphCollector | None = None
_collector_lock = threading.Lock()


def get_collector() -> MCPCallGraphCollector:
    """Get or create the module-level singleton collector."""
    global _default_collector
    with _collector_lock:
        if _default_collector is None:
            _default_collector = MCPCallGraphCollector()
        return _default_collector


__all__ = [
    "CallGraphNode",
    "MCPCallGraphCollector",
    "ToolCall",
    "get_collector",
]
