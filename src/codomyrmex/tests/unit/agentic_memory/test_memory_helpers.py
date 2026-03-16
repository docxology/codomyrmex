"""Unit tests for agentic_memory/memory.py helper functions: _relevance, _recency_score.

These functions power the AgentMemory retrieval scoring but had no direct tests.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.agentic_memory.memory import _recency_score, _relevance


class TestRelevance:
    """Tests for _relevance token-overlap scorer."""

    def test_empty_query_returns_zero(self) -> None:
        assert _relevance("", "some content here") == 0.0

    def test_empty_content_returns_zero(self) -> None:
        assert _relevance("query", "") == 0.0

    def test_both_empty_returns_zero(self) -> None:
        assert _relevance("", "") == 0.0

    def test_exact_match_returns_one(self) -> None:
        """When every query token appears in content, relevance is 1.0."""
        assert _relevance("python programming", "python programming rocks") == 1.0

    def test_partial_match(self) -> None:
        """Only some query tokens overlap."""
        score = _relevance("python java rust", "python is great")
        # Only 1 of 3 query tokens overlaps
        assert score == pytest.approx(1 / 3, rel=1e-6)

    def test_no_overlap_returns_zero(self) -> None:
        assert _relevance("python programming", "rust golang swift") == 0.0

    def test_case_insensitive(self) -> None:
        """Implementation lowercases tokens, so case doesn't matter."""
        score = _relevance("Python", "python")
        assert score == 1.0

    def test_duplicate_tokens_deduplicated(self) -> None:
        """Duplicate query tokens don't inflate the denominator."""
        score = _relevance("python python python", "python java")
        assert score == 1.0  # unique query tokens = {"python"} → 1/1

    def test_special_characters(self) -> None:
        """Tokens with special chars are treated literally."""
        score = _relevance("C++ C#", "C++ is fast but C# is easy")
        assert score == 1.0


class TestRecencyScore:
    """Tests for _recency_score exponential-decay scorer."""

    def test_now_returns_high_score(self) -> None:
        """A memory created right now should score close to 1.0."""
        score = _recency_score(time.time())
        assert score > 0.9

    def test_very_old_returns_low_score(self) -> None:
        """A memory from far in the past scores near zero."""
        score = _recency_score(time.time() - 1_000_000)
        assert score < 0.01

    def test_half_life_at_one_period(self) -> None:
        """After one half-life, score should be ~1/e ≈ 0.368."""
        half_life = 3600.0  # 1 hour default
        score = _recency_score(time.time() - half_life, half_life=half_life)
        assert score == pytest.approx(0.36787944117144233, rel=1e-6)

    def test_two_half_lives(self) -> None:
        """After two half-lives, score ≈ 1/e² ≈ 0.135."""
        half_life = 3600.0
        score = _recency_score(time.time() - 2 * half_life, half_life=half_life)
        assert score == pytest.approx(0.1353352832366127, rel=1e-6)

    def test_custom_half_life(self) -> None:
        """Half-life parameter changes the decay rate."""
        now = time.time()
        # With half_life=100, after 100 seconds we get 1/e
        score = _recency_score(now - 100, half_life=100.0)
        assert score == pytest.approx(0.36787944117144233, rel=1e-6)

    def test_negative_age_clamped(self) -> None:
        """Future timestamps (negative age) are clamped to 0 age → score 1.0."""
        score = _recency_score(time.time() + 1000)
        assert score == pytest.approx(1.0, rel=1e-6)

    def test_very_small_half_life(self) -> None:
        """Very small half_life produces near-zero score for any age > 0."""
        score = _recency_score(time.time() - 100, half_life=0.001)
        assert score < 0.01

    def test_zero_age_with_any_half_life(self) -> None:
        """Zero age (created now) always returns 1.0 regardless of half_life."""
        score = _recency_score(time.time(), half_life=1.0)
        assert score == pytest.approx(1.0, rel=1e-6)
