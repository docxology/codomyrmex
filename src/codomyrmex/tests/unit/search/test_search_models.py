"""
Unit tests for search.models — Zero-Mock compliant.

Covers: Document (dataclass), SearchResult (dataclass + __lt__),
SimpleTokenizer (lowercase/min_length branches), FuzzyMatcher
(levenshtein_distance, similarity_ratio, find_best_match),
QueryParser.parse (terms/must/must_not/phrases).
"""

import pytest

from codomyrmex.search.models import (
    Document,
    FuzzyMatcher,
    QueryParser,
    SearchResult,
    SimpleTokenizer,
)

# ── Document ───────────────────────────────────────────────────────────


@pytest.mark.unit
class TestDocument:
    def test_id_and_content_stored(self):
        doc = Document(id="doc1", content="Hello world")
        assert doc.id == "doc1"
        assert doc.content == "Hello world"

    def test_metadata_default_empty(self):
        doc = Document(id="doc1", content="text")
        assert doc.metadata == {}

    def test_indexed_at_set_automatically(self):
        doc = Document(id="doc1", content="text")
        assert doc.indexed_at is not None

    def test_metadata_stored(self):
        doc = Document(id="d1", content="text", metadata={"author": "Alice"})
        assert doc.metadata["author"] == "Alice"


# ── SearchResult ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestSearchResult:
    def _make_doc(self, doc_id: str = "d1") -> Document:
        return Document(id=doc_id, content="sample content")

    def test_document_and_score_stored(self):
        doc = self._make_doc()
        result = SearchResult(document=doc, score=0.9)
        assert result.document is doc
        assert result.score == pytest.approx(0.9)

    def test_highlights_default_empty(self):
        result = SearchResult(document=self._make_doc(), score=0.5)
        assert result.highlights == []

    def test_highlights_stored(self):
        result = SearchResult(
            document=self._make_doc(), score=0.8, highlights=["match here"]
        )
        assert "match here" in result.highlights

    def test_lt_by_score_true(self):
        r1 = SearchResult(document=self._make_doc("d1"), score=0.5)
        r2 = SearchResult(document=self._make_doc("d2"), score=0.9)
        assert r1 < r2

    def test_lt_by_score_false(self):
        r1 = SearchResult(document=self._make_doc("d1"), score=0.9)
        r2 = SearchResult(document=self._make_doc("d2"), score=0.5)
        assert not (r1 < r2)

    def test_sortable(self):
        docs = [
            SearchResult(document=self._make_doc(f"d{i}"), score=float(3 - i))
            for i in range(3)
        ]
        sorted_results = sorted(docs)
        assert sorted_results[0].score < sorted_results[-1].score


# ── SimpleTokenizer ────────────────────────────────────────────────────


@pytest.mark.unit
class TestSimpleTokenizer:
    def test_basic_tokenization(self):
        t = SimpleTokenizer()
        tokens = t.tokenize("hello world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_lowercase_default_true(self):
        t = SimpleTokenizer()
        tokens = t.tokenize("Hello World")
        assert "hello" in tokens
        assert "world" in tokens
        assert "Hello" not in tokens

    def test_lowercase_false(self):
        t = SimpleTokenizer(lowercase=False)
        tokens = t.tokenize("Hello World")
        assert "Hello" in tokens
        assert "World" in tokens

    def test_min_length_filters_short_tokens(self):
        t = SimpleTokenizer(min_length=3)
        tokens = t.tokenize("a bb ccc dddd")
        assert "a" not in tokens
        assert "bb" not in tokens
        assert "ccc" in tokens
        assert "dddd" in tokens

    def test_min_length_one(self):
        t = SimpleTokenizer(min_length=1)
        tokens = t.tokenize("a bb")
        assert "a" in tokens
        assert "bb" in tokens

    def test_punctuation_stripped(self):
        t = SimpleTokenizer()
        tokens = t.tokenize("hello, world!")
        assert "hello" in tokens
        assert "world" in tokens

    def test_empty_string_returns_empty_list(self):
        t = SimpleTokenizer()
        assert t.tokenize("") == []

    def test_default_min_length_two(self):
        t = SimpleTokenizer()
        tokens = t.tokenize("I am a great programmer")
        # "I" and "a" (length 1) should be filtered
        assert "I" not in tokens
        assert "a" not in tokens
        assert "am" in tokens
        assert "great" in tokens


# ── FuzzyMatcher ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestFuzzyMatcher:
    def test_identical_strings_distance_zero(self):
        assert FuzzyMatcher.levenshtein_distance("hello", "hello") == 0

    def test_completely_different_strings(self):
        dist = FuzzyMatcher.levenshtein_distance("abc", "xyz")
        assert dist == 3

    def test_one_insertion(self):
        # "abc" → "abcd" is 1 insertion
        dist = FuzzyMatcher.levenshtein_distance("abc", "abcd")
        assert dist == 1

    def test_one_deletion(self):
        dist = FuzzyMatcher.levenshtein_distance("abcd", "abc")
        assert dist == 1

    def test_one_substitution(self):
        dist = FuzzyMatcher.levenshtein_distance("abc", "axc")
        assert dist == 1

    def test_empty_first_string(self):
        dist = FuzzyMatcher.levenshtein_distance("", "hello")
        assert dist == 5

    def test_empty_second_string(self):
        dist = FuzzyMatcher.levenshtein_distance("hello", "")
        assert dist == 5

    def test_both_empty(self):
        assert FuzzyMatcher.levenshtein_distance("", "") == 0

    def test_shorter_first_triggers_swap(self):
        """If len(s1) < len(s2), recurse with swapped args."""
        d1 = FuzzyMatcher.levenshtein_distance("hi", "hello")
        d2 = FuzzyMatcher.levenshtein_distance("hello", "hi")
        assert d1 == d2

    def test_similarity_ratio_identical(self):
        ratio = FuzzyMatcher.similarity_ratio("hello", "hello")
        assert ratio == pytest.approx(1.0)

    def test_similarity_ratio_completely_different(self):
        ratio = FuzzyMatcher.similarity_ratio("abc", "xyz")
        assert ratio == pytest.approx(0.0)

    def test_similarity_ratio_empty_first(self):
        assert FuzzyMatcher.similarity_ratio("", "hello") == pytest.approx(0.0)

    def test_similarity_ratio_empty_second(self):
        assert FuzzyMatcher.similarity_ratio("hello", "") == pytest.approx(0.0)

    def test_similarity_ratio_between_0_and_1(self):
        ratio = FuzzyMatcher.similarity_ratio("python", "cython")
        assert 0.0 <= ratio <= 1.0

    def test_similarity_ratio_case_insensitive(self):
        r1 = FuzzyMatcher.similarity_ratio("Hello", "hello")
        assert r1 == pytest.approx(1.0)

    def test_find_best_match_exact(self):
        candidates = ["python", "java", "javascript"]
        result = FuzzyMatcher.find_best_match("python", candidates)
        assert result == "python"

    def test_find_best_match_fuzzy(self):
        candidates = ["python", "java", "javascript"]
        result = FuzzyMatcher.find_best_match("pythn", candidates, threshold=0.5)
        # "pythn" is closest to "python"
        assert result == "python"

    def test_find_best_match_no_match_returns_none(self):
        candidates = ["apple", "banana"]
        result = FuzzyMatcher.find_best_match("xyz123", candidates, threshold=0.9)
        assert result is None

    def test_find_best_match_empty_candidates(self):
        assert FuzzyMatcher.find_best_match("query", []) is None


# ── QueryParser ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestQueryParser:
    def test_simple_terms(self):
        qp = QueryParser()
        result = qp.parse("python programming")
        assert "python" in result["terms"]
        assert "programming" in result["terms"]

    def test_must_term(self):
        qp = QueryParser()
        result = qp.parse("+required term")
        assert "required" in result["must"]

    def test_must_not_term(self):
        qp = QueryParser()
        result = qp.parse("-excluded term")
        assert "excluded" in result["must_not"]

    def test_phrase_extraction(self):
        qp = QueryParser()
        result = qp.parse('"hello world" query')
        assert "hello world" in result["phrases"]

    def test_mixed_query(self):
        qp = QueryParser()
        result = qp.parse('+required -excluded "exact phrase" term')
        assert "required" in result["must"]
        assert "excluded" in result["must_not"]
        assert "exact phrase" in result["phrases"]
        assert "term" in result["terms"]

    def test_empty_query(self):
        qp = QueryParser()
        result = qp.parse("")
        assert result["terms"] == []
        assert result["must"] == []
        assert result["must_not"] == []
        assert result["phrases"] == []

    def test_result_has_all_keys(self):
        qp = QueryParser()
        result = qp.parse("test")
        for key in ("terms", "must", "must_not", "phrases"):
            assert key in result

    def test_phrase_removed_from_main_query(self):
        qp = QueryParser()
        result = qp.parse('"exact match" other')
        # "exact" and "match" should not appear in terms (they're in phrase)
        assert "exact" not in result["terms"]
        assert "match" not in result["terms"]
        assert "other" in result["terms"]

    def test_multiple_must_terms(self):
        qp = QueryParser()
        result = qp.parse("+first +second")
        assert "first" in result["must"]
        assert "second" in result["must"]

    def test_multiple_must_not_terms(self):
        qp = QueryParser()
        result = qp.parse("-bad -worse")
        assert "bad" in result["must_not"]
        assert "worse" in result["must_not"]
