"""MCP tool definitions for the agentic_memory module.

Exposes memory CRUD and search as MCP tools discoverable by
Claude Code and other MCP-compatible agents.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)


def _agent_memory():
    """Lazy import AgentMemory to avoid circular imports."""
    from codomyrmex.agentic_memory.memory import AgentMemory
    return AgentMemory



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
    context_rules: str = "",
) -> list[dict[str, Any]]:
    """Search across stored memories. Returns top-k results.

    Args:
        query: Text query to search for.
        k: Maximum number of memory results to return.
        context_rules: Optional file_path or module_name context. If provided,
                       applicable rules will be prepended to the results.
    """
    agent = _agent_memory()()
    results = agent.search(query, k=k)

    formatted_results = [
        {
            "memory": r.memory.to_dict(),
            "relevance": r.relevance_score,
            "combined_score": r.combined_score,
        }
        for r in results
    ]

    if context_rules:
        try:
            from codomyrmex.agentic_memory.rules.engine import RuleEngine
            engine = RuleEngine()
            # Heuristic: if it has a period or slash, assume file_path, else module_name
            file_path = context_rules if "." in context_rules or "/" in context_rules else None
            module_name = context_rules if not file_path else None

            rule_set = engine.get_applicable_rules(file_path=file_path, module_name=module_name)

            # Prepend rules as critical-importance semantic memories
            for rule in reversed(list(rule_set.resolved())):
                formatted_results.insert(0, {
                    "memory": {
                        "id": f"rule-{rule.name}",
                        "content": rule.raw_content,
                        "memory_type": "semantic",
                        "importance": 4,  # CRITICAL
                        "metadata": {
                            "source": "rule_engine",
                            "priority": rule.priority.name,
                            "rule_name": rule.name,
                        },
                        "tags": ["rule", rule.priority.name.lower()],
                    },
                    "relevance": 1.0,
                    "combined_score": 1.0,
                })
        except Exception:
            logger.warning("Rule injection failed during memory_search", exc_info=True)

    return formatted_results
