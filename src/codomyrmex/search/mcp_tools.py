"""MCP tool definitions for the search module.

Exposes full-text search, fuzzy matching, and query parsing as
MCP tools for agent consumption.
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

from . import Document, FuzzyMatcher, create_index, quick_search


@mcp_tool(
    category="search",
    description="Perform a quick full-text search across a list of text strings.",
)
def search_documents(
    query: str,
    documents: list[str],
    top_k: int = 5,
) -> dict[str, Any]:
    """Search across documents with TF-IDF scoring.

    Args:
        query: Search query string.
        documents: List of plain-text strings to search.
        top_k: Maximum number of results to return.
    """
    try:
        results = quick_search(documents, query, k=top_k)
        return {
            "status": "ok",
            "query": query,
            "results": [
                {
                    "doc_id": r.document.id,
                    "score": r.score,
                    "snippet": r.document.content[:200],
                    "highlights": r.highlights,
                }
                for r in results
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="search",
    description="Create a search index from documents, then query it.",
)
def search_index_query(
    query: str,
    documents: list[str],
    top_k: int = 10,
) -> dict[str, Any]:
    """Build an index from document strings and search it.

    Args:
        query: Search query string.
        documents: List of plain-text strings to index.
        top_k: Maximum number of results to return.
    """
    try:
        index = create_index(backend="memory")
        for i, content in enumerate(documents):
            index.index(Document(id=str(i), content=content))
        results = index.search(query, k=top_k)
        return {
            "status": "ok",
            "query": query,
            "index_size": len(documents),
            "results": [
                {
                    "doc_id": r.document.id,
                    "score": r.score,
                    "snippet": r.document.content[:200],
                    "highlights": r.highlights,
                }
                for r in results
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="search",
    description="Find the best fuzzy match for a query string among candidates.",
)
def search_fuzzy(
    query: str,
    candidates: list[str],
    threshold: float = 0.6,
) -> dict[str, Any]:
    """Find fuzzy matches using Levenshtein distance.

    Args:
        query: String to match against.
        candidates: List of candidate strings.
        threshold: Minimum similarity score (0.0–1.0).
    """
    try:
        scored = []
        for c in candidates:
            score = FuzzyMatcher.similarity_ratio(query, c)
            if score >= threshold:
                scored.append({"candidate": c, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        best = FuzzyMatcher.find_best_match(query, candidates, threshold=threshold)
        return {
            "status": "ok",
            "query": query,
            "best_match": best,
            "matches": scored,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
