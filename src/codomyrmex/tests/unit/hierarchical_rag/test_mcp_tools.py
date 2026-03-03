"""Unit tests for hierarchical_rag MCP tools."""

from codomyrmex.hierarchical_rag.mcp_tools import (
    hierarchical_rag_index_document,
    hierarchical_rag_query,
)


def test_hierarchical_rag_index_document():
    """Test that indexing a document returns a success status and id."""
    doc = {"content": "Test content", "metadata": {"title": "Test"}}
    result = hierarchical_rag_index_document(doc)
    assert result["status"] == "success"
    assert "id" in result
    assert "levels" in result


def test_hierarchical_rag_query():
    """Test that querying returns results matching the query."""
    result = hierarchical_rag_query("test query", max_results=3)
    assert result["query"] == "test query"
    assert "results" in result
    assert len(result["results"]) > 0
    assert result["results"][0]["level"] == "chunk"
