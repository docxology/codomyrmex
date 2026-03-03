"""Strictly zero-mock unit tests for search module's MCP tools."""

import pytest

from codomyrmex.search.mcp_tools import (
    search_documents,
    search_fuzzy,
    search_index_query,
)


@pytest.mark.unit
class TestSearchDocuments:
    """Test suite for search_documents MCP tool."""

    def test_search_documents_success(self):
        """Test search_documents successfully finds documents."""
        docs = [
            "The quick brown fox jumps over the lazy dog.",
            "Python programming is fun.",
            "Learning to code is a great skill.",
        ]
        result = search_documents(query="Python", documents=docs, top_k=2)

        assert result["status"] == "ok"
        assert result["query"] == "Python"
        assert len(result["results"]) == 1
        assert result["results"][0]["doc_id"] == "1"  # Index of "Python programming is fun."

    def test_search_documents_empty_query(self):
        """Test search_documents with an empty query."""
        docs = ["Apple", "Banana", "Cherry"]
        result = search_documents(query="", documents=docs)

        assert result["status"] == "ok"
        assert len(result["results"]) == 0

    def test_search_documents_invalid_input(self):
        """Test search_documents handles exception gracefully."""
        # Pass an invalid type for documents to naturally trigger an exception
        result = search_documents(query="test", documents=None) # type: ignore

        assert result["status"] == "error"
        assert "error" in result


@pytest.mark.unit
class TestSearchIndexQuery:
    """Test suite for search_index_query MCP tool."""

    def test_search_index_query_success(self):
        """Test search_index_query successfully builds index and searches."""
        docs = [
            "Data science involves machine learning and statistics.",
            "Web development requires HTML, CSS, and JavaScript.",
            "Machine learning is a subset of artificial intelligence.",
        ]
        result = search_index_query(query="machine learning", documents=docs, top_k=5)

        assert result["status"] == "ok"
        assert result["index_size"] == 3
        # Should return two documents matching "machine learning"
        assert len(result["results"]) >= 1

    def test_search_index_query_no_results(self):
        """Test search_index_query with no matching results."""
        docs = ["One", "Two", "Three"]
        result = search_index_query(query="Four", documents=docs)

        assert result["status"] == "ok"
        assert len(result["results"]) == 0

    def test_search_index_query_invalid_input(self):
        """Test search_index_query handles exception gracefully."""
        # Trigger an exception natively
        result = search_index_query(query="test", documents=None) # type: ignore

        assert result["status"] == "error"
        assert "error" in result


@pytest.mark.unit
class TestSearchFuzzy:
    """Test suite for search_fuzzy MCP tool."""

    def test_search_fuzzy_success(self):
        """Test search_fuzzy correctly finds fuzzy matches."""
        candidates = ["apple", "banana", "aple", "application"]
        result = search_fuzzy(query="appl", candidates=candidates, threshold=0.5)

        assert result["status"] == "ok"
        assert result["best_match"] == "apple"
        assert len(result["matches"]) > 0
        assert result["matches"][0]["candidate"] == "apple"

    def test_search_fuzzy_no_matches(self):
        """Test search_fuzzy with no matches meeting the threshold."""
        candidates = ["zebra", "xylophone"]
        result = search_fuzzy(query="apple", candidates=candidates, threshold=0.8)

        assert result["status"] == "ok"
        assert result["best_match"] is None
        assert len(result["matches"]) == 0

    def test_search_fuzzy_invalid_input(self):
        """Test search_fuzzy handles exception gracefully."""
        # Trigger an exception natively
        result = search_fuzzy(query="test", candidates=None) # type: ignore

        assert result["status"] == "error"
        assert "error" in result
