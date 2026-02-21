"""MCP tool definitions for the agentic_memory module.

Exposes memory CRUD and search as MCP tools discoverable by
Claude Code and other MCP-compatible agents.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


def _agent_memory():
    """Lazy import AgentMemory to avoid circular imports."""
    from codomyrmex.agentic_memory.memory import AgentMemory
    return AgentMemory


def _stores():
    """Lazy import stores."""
    from codomyrmex.agentic_memory import stores
    return stores


@mcp_tool(
    category="agentic_memory",
    description="Store a new memory entry with content, optional type, and importance.",
)
def memory_put(
    content: str,
    memory_type: str = "episodic",
    importance: str = "medium",
) -> dict[str, Any]:
    """Save a memory. Returns the created memory as a dict."""
    from codomyrmex.agentic_memory.models import MemoryImportance, MemoryType

    agent = _agent_memory()()
    mem = agent.remember(
        content,
        memory_type=MemoryType(memory_type),
        importance=MemoryImportance[importance.upper()],
    )
    return mem.to_dict()


@mcp_tool(
    category="agentic_memory",
    description="Retrieve a memory by its ID.",
)
def memory_get(memory_id: str) -> dict[str, Any] | None:
    """Fetch a single memory. Returns None if not found."""
    from codomyrmex.agentic_memory.stores import InMemoryStore

    store = InMemoryStore()
    mem = store.get(memory_id)
    return mem.to_dict() if mem else None


@mcp_tool(
    category="agentic_memory",
    description="Search memories by a text query. Returns ranked results.",
)
def memory_search(
    query: str,
    k: int = 5,
) -> list[dict[str, Any]]:
    """Search across stored memories. Returns top-k results."""
    agent = _agent_memory()()
    results = agent.search(query, k=k)
    return [
        {
            "memory": r.memory.to_dict(),
            "relevance": r.relevance_score,
            "combined_score": r.combined_score,
        }
        for r in results
    ]
