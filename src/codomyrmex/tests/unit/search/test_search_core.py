"""Zero-mock tests for the search module core behavior.

Covers: engine.py (InMemoryIndex, create_index, quick_search),
        models.py (SimpleTokenizer, FuzzyMatcher, QueryParser),
        hybrid.py (BM25Index, HybridSearchEngine),
        mcp_tools.py (search_documents, search_index_query, search_fuzzy).

No mocks — all tests use real in-memory data.
"""

from __future__ import annotations

import pytest

try:
    from codomyrmex.search.engine import InMemoryIndex, create_index, quick_search
    from codomyrmex.search.hybrid import BM25Index, HybridSearchEngine
    from codomyrmex.search.models import (
        Document,
        FuzzyMatcher,
        QueryParser,
        SimpleTokenizer,
    )

    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False

if not HAS_SEARCH:
    pytest.skip("search module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# SimpleTokenizer — actual output verification
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimpleTokenizerBehavior:
    """Real tokenization output tests."""

    def test_tokenize_basic_words(self):
        tok = SimpleTokenizer()
        result = tok.tokenize("hello world")
        assert "hello" in result
        assert "world" in result

    def test_tokenize_lowercases_by_default(self):
        tok = SimpleTokenizer(lowercase=True)
        result = tok.tokenize("Hello WORLD")
        assert "hello" in result
        assert "world" in result
        assert "Hello" not in result

    def test_tokenize_no_lowercase(self):
        tok = SimpleTokenizer(lowercase=False)
        result = tok.tokenize("Hello WORLD")
        assert "Hello" in result
        assert "WORLD" in result

    def test_tokenize_respects_min_length(self):
        tok = SimpleTokenizer(min_length=4)
        result = tok.tokenize("a be cat dogs")
        assert "a" not in result
        assert "be" not in result
        assert "cat" not in result
        assert "dogs" in result

    def test_tokenize_punctuation_excluded(self):
        tok = SimpleTokenizer()
        result = tok.tokenize("hello, world!")
        # punctuation not included in tokens
        assert "," not in result
        assert "!" not in result

    def test_tokenize_empty_string_returns_empty(self):
        tok = SimpleTokenizer()
        result = tok.tokenize("")
        assert result == []

    def test_tokenize_numbers_included(self):
        tok = SimpleTokenizer()
        result = tok.tokenize("price is 42")
        assert "42" in result

    def test_tokenize_hyphenated_split(self):
        tok = SimpleTokenizer()
        result = tok.tokenize("state-of-the-art")
        # \b\w+\b splits on hyphens
        assert "state" in result
        assert "art" in result


# ---------------------------------------------------------------------------
# FuzzyMatcher — Levenshtein distance
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFuzzyMatcherLevenshtein:
    """Real edit distance value tests."""

    def test_identical_strings_distance_zero(self):
        assert FuzzyMatcher.levenshtein_distance("abc", "abc") == 0

    def test_empty_to_word_distance_equals_word_length(self):
        assert FuzzyMatcher.levenshtein_distance("", "hello") == 5

    def test_single_insertion(self):
        assert FuzzyMatcher.levenshtein_distance("abc", "abcd") == 1

    def test_single_deletion(self):
        assert FuzzyMatcher.levenshtein_distance("abcd", "abc") == 1

    def test_single_substitution(self):
        assert FuzzyMatcher.levenshtein_distance("abc", "axc") == 1

    def test_completely_different_strings(self):
        d = FuzzyMatcher.levenshtein_distance("abc", "xyz")
        assert d == 3

    def test_symmetric(self):
        d1 = FuzzyMatcher.levenshtein_distance("cat", "bat")
        d2 = FuzzyMatcher.levenshtein_distance("bat", "cat")
        assert d1 == d2


# ---------------------------------------------------------------------------
# FuzzyMatcher — similarity ratio
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFuzzyMatcherSimilarity:
    """Similarity ratio boundary tests."""

    def test_identical_strings_ratio_one(self):
        ratio = FuzzyMatcher.similarity_ratio("hello", "hello")
        assert ratio == 1.0

    def test_completely_different_ratio_low(self):
        ratio = FuzzyMatcher.similarity_ratio("abc", "xyz")
        assert ratio < 0.5

    def test_empty_strings_ratio_zero(self):
        ratio = FuzzyMatcher.similarity_ratio("", "abc")
        assert ratio == 0.0

    def test_both_empty_ratio_zero(self):
        ratio = FuzzyMatcher.similarity_ratio("", "")
        assert ratio == 0.0

    def test_ratio_between_zero_and_one(self):
        ratio = FuzzyMatcher.similarity_ratio("hello", "helo")
        assert 0.0 <= ratio <= 1.0

    def test_case_insensitive_comparison(self):
        ratio_lower = FuzzyMatcher.similarity_ratio("hello", "hello")
        ratio_mixed = FuzzyMatcher.similarity_ratio("hello", "HELLO")
        assert ratio_lower == ratio_mixed


# ---------------------------------------------------------------------------
# FuzzyMatcher — find_best_match
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFuzzyMatcherBestMatch:
    """Best match selection tests."""

    def test_exact_match_returned(self):
        result = FuzzyMatcher.find_best_match("apple", ["apple", "mango", "orange"])
        assert result == "apple"

    def test_close_match_returned(self):
        result = FuzzyMatcher.find_best_match(
            "helo", ["hello", "world", "python"], threshold=0.6
        )
        assert result == "hello"

    def test_no_match_returns_none_when_below_threshold(self):
        result = FuzzyMatcher.find_best_match("xyz", ["apple", "mango"], threshold=0.9)
        assert result is None

    def test_best_of_multiple_similar(self):
        # "helo" is closer to "hello" than to "help"
        result = FuzzyMatcher.find_best_match("helo", ["hello", "help"], threshold=0.5)
        assert result == "hello"


# ---------------------------------------------------------------------------
# QueryParser — operator parsing
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestQueryParserOperators:
    """Query operator parsing tests."""

    def test_plain_terms_parsed(self):
        parser = QueryParser()
        result = parser.parse("python programming")
        assert "python" in result["terms"]
        assert "programming" in result["terms"]

    def test_must_operator(self):
        parser = QueryParser()
        result = parser.parse("+required term")
        assert "required" in result["must"]

    def test_must_not_operator(self):
        parser = QueryParser()
        result = parser.parse("-excluded term")
        assert "excluded" in result["must_not"]

    def test_phrase_extraction(self):
        parser = QueryParser()
        result = parser.parse('"exact phrase" other')
        assert "exact phrase" in result["phrases"]

    def test_mixed_operators(self):
        parser = QueryParser()
        result = parser.parse("+must -exclude plain")
        assert "must" in result["must"]
        assert "exclude" in result["must_not"]
        assert "plain" in result["terms"]

    def test_empty_query_returns_empty_lists(self):
        parser = QueryParser()
        result = parser.parse("")
        assert result["terms"] == []
        assert result["must"] == []
        assert result["must_not"] == []
        assert result["phrases"] == []

    def test_result_keys_present(self):
        parser = QueryParser()
        result = parser.parse("test")
        assert "terms" in result
        assert "must" in result
        assert "must_not" in result
        assert "phrases" in result


# ---------------------------------------------------------------------------
# InMemoryIndex — real search and scoring behavior
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInMemoryIndexBehavior:
    """Real index/search/delete behavior tests."""

    def _make_index(self):
        idx = InMemoryIndex()
        idx.index(Document(id="d1", content="Python is a great programming language"))
        idx.index(Document(id="d2", content="Java is another programming language"))
        idx.index(Document(id="d3", content="Machine learning with Python and TensorFlow"))
        return idx

    def test_count_reflects_indexed_documents(self):
        idx = self._make_index()
        assert idx.count() == 3

    def test_search_returns_relevant_result(self):
        idx = self._make_index()
        results = idx.search("Python")
        doc_ids = [r.document.id for r in results]
        assert "d1" in doc_ids or "d3" in doc_ids

    def test_search_empty_query_returns_empty(self):
        idx = self._make_index()
        results = idx.search("")
        assert results == []

    def test_search_no_match_returns_empty(self):
        idx = self._make_index()
        results = idx.search("zzzzzzznomatch")
        assert results == []

    def test_search_results_have_positive_scores(self):
        idx = self._make_index()
        results = idx.search("Python")
        for r in results:
            assert r.score > 0

    def test_search_top_k_limits_results(self):
        idx = self._make_index()
        results = idx.search("programming", k=1)
        assert len(results) <= 1

    def test_delete_removes_document(self):
        idx = self._make_index()
        deleted = idx.delete("d1")
        assert deleted is True
        assert idx.count() == 2

    def test_delete_nonexistent_returns_false(self):
        idx = self._make_index()
        deleted = idx.delete("nonexistent")
        assert deleted is False

    def test_get_returns_document_by_id(self):
        idx = self._make_index()
        doc = idx.get("d1")
        assert doc is not None
        assert doc.id == "d1"

    def test_get_nonexistent_returns_none(self):
        idx = self._make_index()
        assert idx.get("missing") is None

    def test_reindex_document_replaces_old(self):
        idx = InMemoryIndex()
        idx.index(Document(id="doc", content="original content"))
        idx.index(Document(id="doc", content="updated content"))
        assert idx.count() == 1
        doc = idx.get("doc")
        assert "updated" in doc.content

    def test_search_results_sorted_by_score_desc(self):
        idx = self._make_index()
        results = idx.search("Python programming")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_highlights_generated(self):
        idx = self._make_index()
        results = idx.search("Python")
        # At least one result should have highlights
        has_highlights = any(len(r.highlights) > 0 for r in results)
        assert has_highlights


# ---------------------------------------------------------------------------
# create_index factory
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCreateIndexFactory:
    """Factory function tests."""

    def test_memory_backend_returns_in_memory_index(self):
        idx = create_index(backend="memory")
        assert isinstance(idx, InMemoryIndex)

    def test_unknown_backend_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown backend"):
            create_index(backend="nonexistent_backend")


# ---------------------------------------------------------------------------
# quick_search convenience function
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestQuickSearchBehavior:
    """quick_search real behavior tests."""

    def test_finds_relevant_document(self):
        docs = ["alpha beta", "gamma delta", "alpha gamma"]
        results = quick_search(docs, "alpha")
        # Both docs containing alpha should rank above gamma-only doc
        assert len(results) >= 1
        content_snippets = [r.document.content for r in results]
        assert any("alpha" in s for s in content_snippets)

    def test_respects_k_limit(self):
        docs = ["a b", "a c", "a d", "a e"]
        results = quick_search(docs, "a", k=2)
        assert len(results) <= 2

    def test_empty_docs_returns_empty(self):
        results = quick_search([], "query")
        assert results == []

    def test_no_match_returns_empty(self):
        results = quick_search(["hello world", "foo bar"], "zzznomatch")
        assert results == []


# ---------------------------------------------------------------------------
# BM25Index — hybrid search engine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBM25Index:
    """BM25 keyword index real scoring tests."""

    def _make_index(self):
        idx = BM25Index()
        idx.add_document("d1", "python programming language tutorial")
        idx.add_document("d2", "java programming enterprise application")
        idx.add_document("d3", "machine learning neural network python")
        return idx

    def test_search_returns_tuples(self):
        idx = self._make_index()
        results = idx.search("python")
        assert isinstance(results, list)
        for item in results:
            assert len(item) == 2  # (doc_id, score)

    def test_python_docs_rank_above_java(self):
        idx = self._make_index()
        results = idx.search("python")
        ids_in_order = [item[0] for item in results]
        # d1 and d3 both have python; d2 does not
        assert "d2" not in ids_in_order or ids_in_order.index("d2") > min(
            ids_in_order.index("d1") if "d1" in ids_in_order else 99,
            ids_in_order.index("d3") if "d3" in ids_in_order else 99,
        )

    def test_no_match_returns_empty(self):
        idx = self._make_index()
        results = idx.search("zzznomatch")
        assert results == []

    def test_top_k_limits_results(self):
        idx = self._make_index()
        results = idx.search("programming", top_k=1)
        assert len(results) <= 1

    def test_scores_positive(self):
        idx = self._make_index()
        results = idx.search("python")
        for _, score in results:
            assert score > 0


# ---------------------------------------------------------------------------
# HybridSearchEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHybridSearchEngine:
    """Hybrid keyword + semantic search engine tests."""

    def _make_engine(self):
        engine = HybridSearchEngine(keyword_weight=0.5, semantic_weight=0.5)
        engine.add_document("d1", "Python is a great programming language")
        engine.add_document("d2", "Java enterprise development patterns")
        engine.add_document("d3", "Python data science machine learning")
        return engine

    def test_search_returns_results(self):
        engine = self._make_engine()
        results = engine.search("python")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_results_have_required_fields(self):
        engine = self._make_engine()
        results = engine.search("python")
        for r in results:
            assert hasattr(r, "doc_id")
            assert hasattr(r, "score")
            assert hasattr(r, "keyword_score")
            assert hasattr(r, "semantic_score")

    def test_semantic_scores_passed_through(self):
        engine = self._make_engine()
        sem_scores = {"d2": 0.9, "d3": 0.1}
        results = engine.search("python", semantic_scores=sem_scores)
        # d2 should have semantic_score > 0
        d2_result = next((r for r in results if r.doc_id == "d2"), None)
        assert d2_result is not None
        assert d2_result.semantic_score > 0

    def test_top_k_limits_results(self):
        engine = self._make_engine()
        results = engine.search("python", top_k=1)
        assert len(results) <= 1

    def test_results_sorted_by_score_desc(self):
        engine = self._make_engine()
        results = engine.search("python")
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_no_semantic_scores_still_works(self):
        engine = self._make_engine()
        results = engine.search("python", semantic_scores=None)
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# MCP tools — real return shape verification
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSearchMcpTools:
    """MCP tool return shape and value tests."""

    def test_search_documents_success(self):
        from codomyrmex.search.mcp_tools import search_documents

        result = search_documents(
            query="python",
            documents=["python is great", "java is also good"],
            top_k=5,
        )
        assert result["status"] == "success"
        assert result["query"] == "python"
        assert isinstance(result["results"], list)

    def test_search_documents_result_fields(self):
        from codomyrmex.search.mcp_tools import search_documents

        result = search_documents(query="hello", documents=["hello world"])
        assert len(result["results"]) >= 1
        item = result["results"][0]
        assert "doc_id" in item
        assert "score" in item
        assert "snippet" in item
        assert "highlights" in item

    def test_search_documents_no_match(self):
        from codomyrmex.search.mcp_tools import search_documents

        result = search_documents(query="zzznomatch", documents=["hello world"])
        assert result["status"] == "success"
        assert result["results"] == []

    def test_search_index_query_returns_index_size(self):
        from codomyrmex.search.mcp_tools import search_index_query

        docs = ["doc one", "doc two", "doc three"]
        result = search_index_query(query="doc", documents=docs)
        assert result["status"] == "success"
        assert result["index_size"] == 3

    def test_search_fuzzy_success(self):
        from codomyrmex.search.mcp_tools import search_fuzzy

        result = search_fuzzy(
            query="helo",
            candidates=["hello", "world"],
            threshold=0.6,
        )
        assert result["status"] == "success"
        assert result["query"] == "helo"

    def test_search_fuzzy_best_match(self):
        from codomyrmex.search.mcp_tools import search_fuzzy

        result = search_fuzzy(
            query="apple",
            candidates=["apple", "orange", "banana"],
            threshold=0.8,
        )
        assert result["best_match"] == "apple"

    def test_search_fuzzy_below_threshold_no_match(self):
        from codomyrmex.search.mcp_tools import search_fuzzy

        result = search_fuzzy(
            query="xyz",
            candidates=["apple", "orange"],
            threshold=0.9,
        )
        assert result["status"] == "success"
        assert result["best_match"] is None
        assert result["matches"] == []

    def test_search_fuzzy_matches_sorted_by_score(self):
        from codomyrmex.search.mcp_tools import search_fuzzy

        result = search_fuzzy(
            query="python",
            candidates=["python", "pythan", "ruby"],
            threshold=0.5,
        )
        scores = [m["score"] for m in result["matches"]]
        assert scores == sorted(scores, reverse=True)
