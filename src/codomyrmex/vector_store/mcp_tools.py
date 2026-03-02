"""MCP tools for the vector_store module.

Exposes in-process vector similarity search via the PAI MCP bridge.
Uses a module-level InMemoryVectorStore singleton for session-scoped storage.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):  # type: ignore[misc]
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


# Module-level singleton — shared across all tool calls within a process session
_store: Any = None


def _get_store():  # type: ignore[return]
    """Return the shared InMemoryVectorStore, creating it on first call."""
    global _store
    if _store is None:
        from codomyrmex.vector_store.store import InMemoryVectorStore
        _store = InMemoryVectorStore()
    return _store


@mcp_tool(
    category="vector_store",
    description=(
        "Add a vector with an ID and optional metadata to the in-process store. "
        "The embedding must be a list of floats."
    ),
)
def vector_add(
    id: str,
    embedding: list[float],
    metadata: dict | None = None,
) -> bool:
    """Store a vector in the session-scoped in-memory vector store.

    Args:
        id: Unique identifier for this vector.
        embedding: Float embedding vector.
        metadata: Optional key-value metadata to attach to the vector.

    Returns:
        ``True`` on success.
    """
    _get_store().add(id, embedding, metadata or {})
    return True


@mcp_tool(
    category="vector_store",
    description=(
        "Search the in-process vector store for the k most similar vectors to a query embedding. "
        "Returns a list of results with id, score, and metadata."
    ),
)
def vector_search(
    query_embedding: list[float],
    k: int = 5,
) -> list[dict]:
    """Find the *k* most similar vectors to *query_embedding*.

    Args:
        query_embedding: Float query vector to search with.
        k: Maximum number of results to return (default 5).

    Returns:
        List of dicts with ``id``, ``score``, and ``metadata`` keys,
        sorted best-match first.
    """
    results = _get_store().search(query_embedding, k=k)
    return [
        {"id": r.id, "score": r.score, "metadata": r.metadata}
        for r in results
    ]


@mcp_tool(
    category="vector_store",
    description="Delete a vector by ID from the in-process store. Returns True if deleted, False if not found.",
)
def vector_delete(id: str) -> bool:
    """Remove a vector from the session store.

    Args:
        id: ID of the vector to remove.

    Returns:
        ``True`` if the vector existed and was removed, ``False`` otherwise.
    """
    return _get_store().delete(id)


@mcp_tool(
    category="vector_store",
    description="Return the total number of vectors currently in the in-process store.",
)
def vector_count() -> int:
    """Return the number of vectors in the session store."""
    return _get_store().count()
