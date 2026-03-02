"""
Unit tests for model_ops.evaluation.scorers — Zero-Mock compliant.

Covers: ExactMatchScorer, ContainsScorer, LengthScorer, RegexScorer,
WeightedScorer, CompositeScorer, create_default_scorer, score_batch.
"""

import pytest

from codomyrmex.model_ops.evaluation.scorers import (
    CompositeScorer,
    ContainsScorer,
    ExactMatchScorer,
    LengthScorer,
    RegexScorer,
    WeightedScorer,
    create_default_scorer,
)

# ── ExactMatchScorer ──────────────────────────────────────────────────


@pytest.mark.unit
class TestExactMatchScorer:
    def test_name(self):
        assert ExactMatchScorer().name == "exact_match"

    def test_exact_match_returns_one(self):
        s = ExactMatchScorer()
        assert s.score("hello", "hello") == 1.0

    def test_mismatch_returns_zero(self):
        s = ExactMatchScorer()
        assert s.score("hello", "world") == 0.0

    def test_strips_whitespace_by_default(self):
        s = ExactMatchScorer()
        assert s.score("  hello  ", "hello") == 1.0

    def test_no_strip_whitespace(self):
        s = ExactMatchScorer(strip_whitespace=False)
        assert s.score("  hello  ", "hello") == 0.0

    def test_case_sensitive_default(self):
        s = ExactMatchScorer()
        assert s.score("Hello", "hello") == 0.0

    def test_case_insensitive(self):
        s = ExactMatchScorer(case_sensitive=False)
        assert s.score("Hello", "hello") == 1.0

    def test_empty_strings_match(self):
        s = ExactMatchScorer()
        assert s.score("", "") == 1.0

    def test_score_batch(self):
        s = ExactMatchScorer()
        pairs = [("a", "a"), ("b", "c"), ("d", "d")]
        scores = s.score_batch(pairs)
        assert scores == [1.0, 0.0, 1.0]


# ── ContainsScorer ────────────────────────────────────────────────────


@pytest.mark.unit
class TestContainsScorer:
    def test_name(self):
        assert ContainsScorer().name == "contains"

    def test_contains_returns_one(self):
        s = ContainsScorer()
        assert s.score("hello world", "world") == 1.0

    def test_not_contains_returns_zero(self):
        s = ContainsScorer()
        assert s.score("hello", "world") == 0.0

    def test_case_insensitive_by_default(self):
        s = ContainsScorer()
        assert s.score("Hello World", "hello") == 1.0

    def test_case_sensitive(self):
        s = ContainsScorer(case_sensitive=True)
        assert s.score("Hello World", "hello") == 0.0
        assert s.score("Hello World", "Hello") == 1.0

    def test_empty_reference_always_contained(self):
        s = ContainsScorer()
        assert s.score("anything", "") == 1.0

    def test_score_batch_multiple(self):
        s = ContainsScorer()
        pairs = [("cat in hat", "cat"), ("no animals", "dog")]
        scores = s.score_batch(pairs)
        assert scores == [1.0, 0.0]


# ── LengthScorer ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestLengthScorer:
    def test_name(self):
        assert LengthScorer().name == "length"

    def test_within_range_returns_one(self):
        s = LengthScorer(min_length=5, max_length=20)
        assert s.score("hello world") == 1.0

    def test_too_short_partial_score(self):
        s = LengthScorer(min_length=10, max_length=20)
        # "hi" is length 2, min_length=10 → 8 below
        score = s.score("hi")
        assert 0.0 <= score < 1.0

    def test_too_long_partial_score(self):
        s = LengthScorer(min_length=1, max_length=5)
        score = s.score("a very long string that exceeds max")
        assert 0.0 <= score < 1.0

    def test_exactly_min_length(self):
        s = LengthScorer(min_length=5, max_length=10)
        assert s.score("hello") == 1.0

    def test_exactly_max_length(self):
        s = LengthScorer(min_length=1, max_length=5)
        assert s.score("hello") == 1.0

    def test_reference_ignored(self):
        s = LengthScorer(min_length=1, max_length=100)
        assert s.score("hello", "ignored reference") == 1.0

    def test_negative_min_length_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            LengthScorer(min_length=-1)

    def test_max_less_than_min_raises(self):
        with pytest.raises(ValueError, match="max_length"):
            LengthScorer(min_length=10, max_length=5)

    def test_empty_output_when_min_is_zero(self):
        s = LengthScorer(min_length=0, max_length=100)
        assert s.score("") == 1.0


# ── RegexScorer ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestRegexScorer:
    def test_name(self):
        assert RegexScorer().name == "regex"

    def test_match_found_returns_one(self):
        s = RegexScorer()
        assert s.score("hello world", r"\w+") == 1.0

    def test_no_match_returns_zero(self):
        s = RegexScorer()
        assert s.score("hello", r"^\d+$") == 0.0

    def test_full_match_mode(self):
        s = RegexScorer(full_match=True)
        assert s.score("12345", r"\d+") == 1.0
        assert s.score("hello 12345", r"\d+") == 0.0

    def test_partial_match_default(self):
        s = RegexScorer(full_match=False)
        assert s.score("abc 123 xyz", r"\d+") == 1.0

    def test_invalid_regex_returns_zero(self):
        s = RegexScorer()
        assert s.score("hello", r"[invalid(") == 0.0

    def test_case_insensitive_flag(self):
        import re
        s = RegexScorer(flags=re.IGNORECASE)
        assert s.score("Hello World", r"hello") == 1.0

    def test_digit_pattern(self):
        s = RegexScorer()
        assert s.score("abc123", r"\d{3}") == 1.0
        assert s.score("abc", r"\d{3}") == 0.0


# ── WeightedScorer ────────────────────────────────────────────────────


@pytest.mark.unit
class TestWeightedScorer:
    def test_fields(self):
        scorer = ExactMatchScorer()
        ws = WeightedScorer(scorer=scorer, weight=2.0)
        assert ws.scorer is scorer
        assert ws.weight == 2.0

    def test_default_weight_one(self):
        ws = WeightedScorer(scorer=ExactMatchScorer())
        assert ws.weight == 1.0


# ── CompositeScorer ───────────────────────────────────────────────────


@pytest.mark.unit
class TestCompositeScorer:
    def test_name(self):
        assert CompositeScorer().name == "composite"

    def test_empty_returns_zero(self):
        s = CompositeScorer()
        assert s.score("anything", "reference") == 0.0

    def test_single_exact_match(self):
        s = CompositeScorer([WeightedScorer(ExactMatchScorer(), weight=1.0)])
        assert s.score("hello", "hello") == 1.0
        assert s.score("hello", "world") == 0.0

    def test_add_scorer_chaining(self):
        s = CompositeScorer()
        result = s.add_scorer(ExactMatchScorer(), weight=1.0)
        assert result is s

    def test_add_scorer_negative_weight_raises(self):
        s = CompositeScorer()
        with pytest.raises(ValueError, match="positive"):
            s.add_scorer(ExactMatchScorer(), weight=-1.0)

    def test_add_scorer_zero_weight_raises(self):
        s = CompositeScorer()
        with pytest.raises(ValueError, match="positive"):
            s.add_scorer(ExactMatchScorer(), weight=0.0)

    def test_scorer_count(self):
        s = CompositeScorer()
        assert s.scorer_count == 0
        s.add_scorer(ExactMatchScorer())
        assert s.scorer_count == 1

    def test_weighted_average(self):
        # ExactMatch (weight=2): score=1.0 → contributes 2.0
        # Contains (weight=1): score=0.0 (no "world" in "hi") → contributes 0.0
        # Total weight=3, weighted_sum=2.0 → avg = 2/3
        s = CompositeScorer([
            WeightedScorer(ExactMatchScorer(), weight=2.0),
            WeightedScorer(ContainsScorer(), weight=1.0),
        ])
        score = s.score("hi", "hi")
        # exact=1.0 (weight=2), contains=1.0 (weight=1) → 3/3 = 1.0
        assert score == 1.0

    def test_weighted_average_partial(self):
        s = CompositeScorer([
            WeightedScorer(ExactMatchScorer(), weight=1.0),
            WeightedScorer(ContainsScorer(), weight=1.0),
        ])
        # "hello world" vs "world": exact=0, contains=1
        score = s.score("hello world", "world")
        assert score == 0.5

    def test_score_detailed_empty(self):
        s = CompositeScorer()
        d = s.score_detailed("a", "b")
        assert d["overall"] == 0.0
        assert d["scorers"] == []

    def test_score_detailed_with_scorers(self):
        s = CompositeScorer([WeightedScorer(ExactMatchScorer(), weight=1.0)])
        d = s.score_detailed("hello", "hello")
        assert d["overall"] == 1.0
        assert len(d["scorers"]) == 1
        assert d["scorers"][0]["name"] == "exact_match"
        assert d["scorers"][0]["score"] == 1.0

    def test_score_batch(self):
        s = CompositeScorer([WeightedScorer(ExactMatchScorer())])
        pairs = [("a", "a"), ("b", "c")]
        scores = s.score_batch(pairs)
        assert scores == [1.0, 0.0]


# ── create_default_scorer ─────────────────────────────────────────────


@pytest.mark.unit
class TestCreateDefaultScorer:
    def test_returns_composite(self):
        s = create_default_scorer()
        assert isinstance(s, CompositeScorer)

    def test_has_three_scorers(self):
        s = create_default_scorer()
        assert s.scorer_count == 3

    def test_exact_match_scores_one(self):
        s = create_default_scorer()
        score = s.score("hello", "hello")
        assert score > 0.8

    def test_different_outputs_score_lower(self):
        s = create_default_scorer()
        score = s.score("completely different", "hello world")
        assert score < 0.5
