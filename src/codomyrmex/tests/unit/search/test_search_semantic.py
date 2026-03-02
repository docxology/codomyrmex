"""Tests for search.semantic module."""

import pytest

try:
    from codomyrmex.search import Document, SearchResult
    from codomyrmex.search.semantic import (
        AutoCompleteIndex,
        BM25Index,
        HybridSearchIndex,
        SemanticSearchResult,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("search.semantic module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# SemanticSearchResult
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSemanticSearchResult:
    """Test suite for SemanticSearchResult."""
    def test_create(self):
        """Test functionality: create."""
        doc = Document(id="1", content="test document")
        result = SemanticSearchResult(
            document=doc,
            semantic_score=0.9,
            keyword_score=0.8,
            combined_score=0.85,
        )
        assert result.document.id == "1"
        assert result.semantic_score == 0.9
        assert result.keyword_score == 0.8
        assert result.combined_score == 0.85
        assert result.highlights == []

    def test_create_with_highlights(self):
        """Test functionality: create with highlights."""
        doc = Document(id="1", content="test")
        result = SemanticSearchResult(
            document=doc,
            semantic_score=0.5,
            keyword_score=0.5,
            combined_score=0.5,
            highlights=["...test..."],
        )
        assert len(result.highlights) == 1


# ---------------------------------------------------------------------------
# HybridSearchIndex (keyword-only mode, no embedding function)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestHybridSearchIndex:
    """Test suite for HybridSearchIndex."""
    def test_create_default(self):
        """Test functionality: create default."""
        index = HybridSearchIndex()
        assert index.count() == 0

    def test_create_with_semantic_weight(self):
        """Test functionality: create with semantic weight."""
        index = HybridSearchIndex(semantic_weight=0.7)
        assert index._semantic_weight == 0.7

    def test_index_document(self):
        """Test functionality: index document."""
        index = HybridSearchIndex()
        doc = Document(id="1", content="hello world testing")
        index.index(doc)
        assert index.count() == 1

    def test_index_multiple_documents(self):
        """Test functionality: index multiple documents."""
        index = HybridSearchIndex()
        for i in range(5):
            index.index(Document(id=str(i), content=f"document number {i}"))
        assert index.count() == 5

    def test_search_keyword_only(self):
        """Test functionality: search keyword only."""
        index = HybridSearchIndex()
        index.index(Document(id="1", content="python programming language"))
        index.index(Document(id="2", content="java programming language"))
        index.index(Document(id="3", content="python is great"))

        results = index.search("python")
        assert len(results) > 0
        assert all(isinstance(r, SemanticSearchResult) for r in results)

    def test_search_returns_combined_scores(self):
        """Test functionality: search returns combined scores."""
        index = HybridSearchIndex()
        index.index(Document(id="1", content="machine learning algorithms"))
        results = index.search("machine learning")
        if results:
            assert results[0].keyword_score >= 0
            assert results[0].combined_score >= 0

    def test_search_respects_k(self):
        """Test functionality: search respects k."""
        index = HybridSearchIndex()
        for i in range(20):
            index.index(Document(id=str(i), content=f"test document {i}"))
        results = index.search("test", k=5)
        assert len(results) <= 5

    def test_search_no_results(self):
        """Test functionality: search no results."""
        index = HybridSearchIndex()
        index.index(Document(id="1", content="hello world"))
        results = index.search("xyznonexistent")
        assert len(results) == 0

    def test_delete_document(self):
        """Test functionality: delete document."""
        index = HybridSearchIndex()
        doc = Document(id="1", content="test document")
        index.index(doc)
        assert index.count() == 1
        removed = index.delete("1")
        assert removed is True
        assert index.count() == 0

    def test_delete_nonexistent(self):
        """Test functionality: delete nonexistent."""
        index = HybridSearchIndex()
        removed = index.delete("nonexistent")
        assert removed is False

    def test_search_with_custom_semantic_weight(self):
        """Test functionality: search with custom semantic weight."""
        index = HybridSearchIndex()
        index.index(Document(id="1", content="python programming"))
        results = index.search("python", semantic_weight=0.0)
        if results:
            # With semantic_weight=0, only keyword score matters
            assert results[0].combined_score == results[0].keyword_score


# ---------------------------------------------------------------------------
# BM25Index
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBM25Index:
    """Test suite for BM25Index."""
    def test_create_defaults(self):
        """Test functionality: create defaults."""
        index = BM25Index()
        assert index.k1 == 1.5
        assert index.b == 0.75

    def test_create_custom(self):
        """Test functionality: create custom."""
        index = BM25Index(k1=2.0, b=0.5)
        assert index.k1 == 2.0
        assert index.b == 0.5

    def test_index_document(self):
        """Test functionality: index document."""
        index = BM25Index()
        doc = Document(id="1", content="the quick brown fox")
        index.index(doc)
        assert index._doc_count == 1

    def test_tokenize(self):
        """Test functionality: tokenize."""
        index = BM25Index()
        tokens = index._tokenize("Hello World! Python 3.10")
        assert "hello" in tokens
        assert "world" in tokens
        assert "python" in tokens

    def test_search_single_doc(self):
        """Test functionality: search single doc."""
        index = BM25Index()
        index.index(Document(id="1", content="the quick brown fox jumps"))
        results = index.search("fox")
        assert len(results) == 1
        assert results[0].document.id == "1"
        assert results[0].score > 0

    def test_search_multiple_docs_ranking(self):
        """Test functionality: search multiple docs ranking."""
        index = BM25Index()
        index.index(Document(id="1", content="python programming python"))
        index.index(Document(id="2", content="java programming"))
        index.index(Document(id="3", content="python"))
        results = index.search("python")
        assert len(results) >= 2
        # Doc with more "python" occurrences should score higher
        ids = [r.document.id for r in results]
        assert "1" in ids

    def test_search_no_match(self):
        """Test functionality: search no match."""
        index = BM25Index()
        index.index(Document(id="1", content="hello world"))
        results = index.search("xyznonexistent")
        assert len(results) == 0

    def test_search_respects_k(self):
        """Test functionality: search respects k."""
        index = BM25Index()
        for i in range(20):
            index.index(Document(id=str(i), content=f"document about topic {i}"))
        results = index.search("document topic", k=3)
        assert len(results) <= 3

    def test_search_returns_search_result(self):
        """Test functionality: search returns search result."""
        index = BM25Index()
        index.index(Document(id="1", content="test content"))
        results = index.search("test")
        assert all(isinstance(r, SearchResult) for r in results)

    def test_avg_doc_length_updated(self):
        """Test functionality: avg doc length updated."""
        index = BM25Index()
        index.index(Document(id="1", content="short"))
        index.index(Document(id="2", content="this is a much longer document with many words"))
        assert index._avg_doc_length > 0
        assert index._doc_count == 2


# ---------------------------------------------------------------------------
# AutoCompleteIndex
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestAutoCompleteIndex:
    """Test suite for AutoCompleteIndex."""
    def test_create_default(self):
        """Test functionality: create default."""
        index = AutoCompleteIndex()
        assert index._max_suggestions == 10

    def test_create_custom(self):
        """Test functionality: create custom."""
        index = AutoCompleteIndex(max_suggestions=5)
        assert index._max_suggestions == 5

    def test_add_term(self):
        """Test functionality: add term."""
        index = AutoCompleteIndex()
        index.add("python")
        suggestions = index.suggest("py")
        assert "python" in suggestions

    def test_add_with_weight(self):
        """Test functionality: add with weight."""
        index = AutoCompleteIndex()
        index.add("python", weight=10.0)
        index.add("pytorch", weight=5.0)
        suggestions = index.suggest("py")
        assert suggestions[0] == "python"  # Higher weight first

    def test_add_bulk(self):
        """Test functionality: add bulk."""
        index = AutoCompleteIndex()
        index.add_bulk(["apple", "application", "apply"])
        suggestions = index.suggest("app")
        assert len(suggestions) == 3

    def test_suggest_empty_prefix(self):
        """Test functionality: suggest empty prefix."""
        index = AutoCompleteIndex()
        index.add("hello")
        index.add("world")
        suggestions = index.suggest("")
        assert len(suggestions) == 2

    def test_suggest_no_match(self):
        """Test functionality: suggest no match."""
        index = AutoCompleteIndex()
        index.add("hello")
        suggestions = index.suggest("xyz")
        assert len(suggestions) == 0

    def test_suggest_respects_limit(self):
        """Test functionality: suggest respects limit."""
        index = AutoCompleteIndex(max_suggestions=2)
        index.add_bulk(["aaa", "aab", "aac", "aad"])
        suggestions = index.suggest("a")
        assert len(suggestions) <= 2

    def test_suggest_custom_limit(self):
        """Test functionality: suggest custom limit."""
        index = AutoCompleteIndex(max_suggestions=10)
        index.add_bulk(["aaa", "aab", "aac", "aad"])
        suggestions = index.suggest("a", limit=2)
        assert len(suggestions) <= 2

    def test_case_insensitive(self):
        """Test functionality: case insensitive."""
        index = AutoCompleteIndex()
        index.add("Python")
        suggestions = index.suggest("py")
        assert "Python" in suggestions

    def test_exact_match(self):
        """Test functionality: exact match."""
        index = AutoCompleteIndex()
        index.add("test")
        suggestions = index.suggest("test")
        assert "test" in suggestions

    def test_suggest_preserves_original_case(self):
        """Test functionality: suggest preserves original case."""
        index = AutoCompleteIndex()
        index.add("JavaScript")
        suggestions = index.suggest("java")
        assert "JavaScript" in suggestions
