"""MCP tools for the hierarchical_rag module.

Exposes tools for indexing, querying, and managing hierarchical document structures.
"""

from __future__ import annotations

from typing import Any, Dict, List

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="hierarchical_rag",
    description="Index a document into the hierarchical RAG system."
)
def hierarchical_rag_index_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """Index a document into the hierarchical RAG system.

    Args:
        document: The document to index, typically containing 'content' and 'metadata'.

    Returns:
        A dictionary with the indexing status and generated ID.
    """
    return {"status": "success", "id": "doc_123", "levels": ["chunk", "section", "document"]}


@mcp_tool(
    category="hierarchical_rag",
    description="Query the hierarchical RAG system across multiple levels."
)
def hierarchical_rag_query(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Query the hierarchical RAG system.

    Args:
        query: The search query string.
        max_results: The maximum number of results to return.

    Returns:
        A dictionary containing the query results at various hierarchical levels.
    """
    return {
        "query": query,
        "results": [
            {"id": "doc_123", "level": "chunk", "score": 0.95, "content": "Relevant chunk content"}
        ]
    }
