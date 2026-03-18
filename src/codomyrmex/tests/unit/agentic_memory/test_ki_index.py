"""Tests for KnowledgeItemIndex — incremental TF-IDF index.

Zero-mock policy: all tests use the real KnowledgeItemIndex class.
"""

from __future__ import annotations

import pytest

from codomyrmex.agentic_memory.ki_index import KnowledgeItemIndex


class TestKnowledgeItemIndexAdd:
    """Tests for KnowledgeItemIndex.add / remove."""

    def test_initial_size_zero(self) -> None:
        idx = KnowledgeItemIndex()
        assert idx.size == 0

    def test_add_increments_size(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("a1", "machine learning model training")
        assert idx.size == 1

    def test_add_multiple(self) -> None:
        idx = KnowledgeItemIndex()
        for i in range(5):
            idx.add(f"ki-{i}", f"document content {i} for indexing")
        assert idx.size == 5

    def test_add_replaces_existing(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("ki-1", "original content about oauth")
        idx.add("ki-1", "updated content about jwt")
        assert idx.size == 1

    def test_remove_existing_returns_true(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("ki-x", "some document")
        assert idx.remove("ki-x") is True
        assert idx.size == 0

    def test_remove_missing_returns_false(self) -> None:
        idx = KnowledgeItemIndex()
        assert idx.remove("nonexistent") is False

    def test_empty_content_not_indexed(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("ki-empty", "")
        assert idx.size == 0


class TestKnowledgeItemIndexSearch:
    """Tests for KnowledgeItemIndex.search scoring and ranking."""

    @pytest.fixture
    def populated_index(self) -> KnowledgeItemIndex:
        idx = KnowledgeItemIndex()
        idx.add("auth", "OAuth2 refresh token authentication patterns for APIs")
        idx.add("docker", "Docker multi-stage build guide for Python applications")
        idx.add("ml", "Machine learning model training pipeline and hyperparameters")
        idx.add("bm25", "BM25 full-text search scoring and ranking algorithm")
        return idx

    def test_search_returns_top_match(self, populated_index: KnowledgeItemIndex) -> None:
        results = populated_index.search("OAuth2 authentication", limit=1)
        assert len(results) == 1
        assert results[0][0] == "auth"

    def test_search_returns_scored_tuples(
        self, populated_index: KnowledgeItemIndex
    ) -> None:
        results = populated_index.search("Docker build")
        assert all(isinstance(doc_id, str) for doc_id, _ in results)
        assert all(isinstance(score, float) for _, score in results)

    def test_search_respects_limit(self, populated_index: KnowledgeItemIndex) -> None:
        results = populated_index.search("algorithm model pipeline", limit=2)
        assert len(results) <= 2

    def test_search_returns_empty_on_no_match(
        self, populated_index: KnowledgeItemIndex
    ) -> None:
        results = populated_index.search("quantum entanglement")
        assert results == []

    def test_search_on_empty_index(self) -> None:
        idx = KnowledgeItemIndex()
        assert idx.search("anything") == []

    def test_search_empty_query_returns_empty(
        self, populated_index: KnowledgeItemIndex
    ) -> None:
        assert populated_index.search("") == []

    def test_higher_score_for_more_term_overlap(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("hi", "token token token authentication token refresh")
        idx.add("lo", "unrelated database transaction content")
        results = idx.search("token authentication")
        assert results[0][0] == "hi"

    def test_search_bm25_idf_penalises_common_words(self) -> None:
        idx = KnowledgeItemIndex()
        # "the" appears in every document → very low IDF
        for i in range(10):
            idx.add(f"doc{i}", f"the document number {i}")
        idx.add("target", "the special unique xyzzy keyword")
        results = idx.search("xyzzy keyword")
        assert results[0][0] == "target"

    def test_scores_are_descending(self, populated_index: KnowledgeItemIndex) -> None:
        results = populated_index.search("machine learning model")
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)


class TestKnowledgeItemIndexSnippet:
    """Tests for KnowledgeItemIndex.snippet."""

    def test_snippet_returns_content(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("ki-s", "Hello world this is the content.")
        assert idx.snippet("ki-s") == "Hello world this is the content."

    def test_snippet_truncates_at_length(self) -> None:
        idx = KnowledgeItemIndex()
        idx.add("ki-long", "A" * 500)
        snip = idx.snippet("ki-long", length=50)
        assert len(snip) == 50

    def test_snippet_unknown_id_returns_empty(self) -> None:
        idx = KnowledgeItemIndex()
        assert idx.snippet("missing") == ""
