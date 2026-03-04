"""Tests for meme MCP tools.

Zero-mock tests exercising memetic dissection, fitness computation,
and synthesis using real MemeticEngine instances.
"""

from __future__ import annotations

from codomyrmex.meme.mcp_tools import (
    meme_dissect,
    meme_fitness,
    meme_synthesize,
)


class TestMemeDissect:
    """Tests for meme_dissect."""

    def test_single_sentence(self):
        """A single sentence produces one meme."""
        result = meme_dissect("We believe in open science.")
        assert result["status"] == "success"
        assert result["count"] == 1
        meme = result["memes"][0]
        assert "believe" in meme["content"].lower() or len(meme["content"]) > 0
        assert "fitness" in meme

    def test_multiple_sentences(self):
        """Multiple sentences produce multiple memes."""
        text = "This is true. We should act. The plan is ready."
        result = meme_dissect(text)
        assert result["status"] == "success"
        assert result["count"] == 3

    def test_empty_text(self):
        """Empty text returns error."""
        result = meme_dissect("")
        assert result["status"] == "error"
        assert "empty" in result["message"].lower()

    def test_meme_fields_present(self):
        """Each meme dict has all expected fields."""
        result = meme_dissect("We know this to be a fact.")
        meme = result["memes"][0]
        expected_keys = {"id", "content", "meme_type", "fitness", "fidelity", "fecundity", "longevity"}
        assert expected_keys.issubset(set(meme.keys()))


class TestMemeFitness:
    """Tests for meme_fitness."""

    def test_default_scores(self):
        """Default scores produce a valid fitness."""
        result = meme_fitness(content="Test meme")
        assert result["status"] == "success"
        assert 0.0 <= result["fitness"] <= 1.0
        assert len(result["meme_id"]) > 0

    def test_perfect_scores(self):
        """All 1.0 scores yield fitness = 1.0."""
        result = meme_fitness(content="Perfect", fidelity=1.0, fecundity=1.0, longevity=1.0)
        assert result["status"] == "success"
        assert abs(result["fitness"] - 1.0) < 1e-6

    def test_zero_score(self):
        """A zero in any dimension yields fitness = 0."""
        result = meme_fitness(content="Zero", fidelity=0.0, fecundity=0.5, longevity=0.5)
        assert result["status"] == "success"
        assert result["fitness"] == 0.0

    def test_clamping(self):
        """Values above 1.0 are clamped."""
        result = meme_fitness(content="Over", fidelity=2.0, fecundity=1.5, longevity=3.0)
        assert result["status"] == "success"
        assert result["fidelity"] == 1.0
        assert result["fecundity"] == 1.0
        assert result["longevity"] == 1.0


class TestMemeSynthesize:
    """Tests for meme_synthesize."""

    def test_join_fragments(self):
        """Fragments are joined with separator."""
        result = meme_synthesize(["Hello", "World"], separator=" ")
        assert result["status"] == "success"
        assert result["text"] == "Hello World"
        assert result["fragment_count"] == 2

    def test_custom_separator(self):
        """Custom separator is respected."""
        result = meme_synthesize(["A", "B", "C"], separator=" | ")
        assert result["status"] == "success"
        assert result["text"] == "A | B | C"

    def test_empty_fragments(self):
        """Empty fragment list returns error."""
        result = meme_synthesize([])
        assert result["status"] == "error"
        assert "empty" in result["message"].lower()
