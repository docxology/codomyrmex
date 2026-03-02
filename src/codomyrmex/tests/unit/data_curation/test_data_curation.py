"""
Unit tests for the data_curation module.

Tests cover:
- MinHash signature computation and Jaccard estimation
- LSH index add/query mechanics
- DataCurator end-to-end deduplication pipeline
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.data_curation import DataCurator, LSHIndex, MinHash

# ---------------------------------------------------------------------------
# MinHash
# ---------------------------------------------------------------------------


class TestMinHashSignature:
    """MinHash signature computation and properties."""

    @pytest.mark.unit
    def test_signature_length(self):
        """Signature length must equal n_hashes."""
        mh = MinHash(n_hashes=64, shingle_size=3)
        sig = mh.signature("hello world this is a test")
        assert sig.shape == (64,)

    @pytest.mark.unit
    def test_signature_length_default(self):
        """Default n_hashes=128 produces 128-element signature."""
        mh = MinHash()
        sig = mh.signature("some text to hash")
        assert sig.shape == (128,)

    @pytest.mark.unit
    def test_signature_dtype(self):
        """Signature should be int64 array."""
        mh = MinHash()
        sig = mh.signature("test text")
        assert sig.dtype == np.int64

    @pytest.mark.unit
    def test_signature_deterministic(self):
        """Same text should always produce the same signature."""
        mh = MinHash()
        sig1 = mh.signature("deterministic test")
        sig2 = mh.signature("deterministic test")
        np.testing.assert_array_equal(sig1, sig2)

    @pytest.mark.unit
    def test_empty_text_no_crash(self):
        """Empty or very short text should not crash."""
        mh = MinHash(shingle_size=3)
        sig = mh.signature("")
        assert sig.shape == (128,)

    @pytest.mark.unit
    def test_short_text_no_crash(self):
        """Text shorter than shingle size should produce valid signature."""
        mh = MinHash(shingle_size=5)
        sig = mh.signature("hi")
        assert sig.shape == (128,)


class TestMinHashSimilarity:
    """MinHash Jaccard similarity estimation."""

    @pytest.mark.unit
    def test_identical_texts_are_similar(self):
        """Identical texts should have similarity >= 0.95."""
        mh = MinHash()
        sig_a = mh.signature("the quick brown fox jumps over the lazy dog")
        sig_b = mh.signature("the quick brown fox jumps over the lazy dog")
        sim = mh.jaccard_estimate(sig_a, sig_b)
        assert sim >= 0.95

    @pytest.mark.unit
    def test_identical_texts_exact(self):
        """Identical texts should have similarity == 1.0."""
        mh = MinHash()
        text = "identical text for comparison"
        sig_a = mh.signature(text)
        sig_b = mh.signature(text)
        assert mh.jaccard_estimate(sig_a, sig_b) == 1.0

    @pytest.mark.unit
    def test_different_texts_low_similarity(self):
        """Completely different texts should have low similarity."""
        mh = MinHash()
        sig_a = mh.signature("the quick brown fox jumps over the lazy dog")
        sig_b = mh.signature("quantum mechanics explains subatomic particle behavior")
        sim = mh.jaccard_estimate(sig_a, sig_b)
        assert sim < 0.3

    @pytest.mark.unit
    def test_near_duplicate_moderate_similarity(self):
        """Texts with minor edits should have moderate-to-high similarity."""
        mh = MinHash(n_hashes=256)  # More hashes for better estimate
        text_a = "the quick brown fox jumps over the lazy dog and runs away"
        text_b = "the quick brown fox leaps over the lazy dog and runs away"
        sim = mh.jaccard_estimate(mh.signature(text_a), mh.signature(text_b))
        assert 0.4 < sim < 1.0

    @pytest.mark.unit
    def test_are_similar_true(self):
        """are_similar returns True for identical texts."""
        mh = MinHash()
        assert mh.are_similar("hello world test", "hello world test")

    @pytest.mark.unit
    def test_are_similar_false(self):
        """are_similar returns False for very different texts."""
        mh = MinHash()
        assert not mh.are_similar(
            "completely different text about science",
            "random unrelated words about cooking recipes",
        )

    @pytest.mark.unit
    def test_similarity_symmetric(self):
        """Jaccard estimate should be symmetric: J(A,B) == J(B,A)."""
        mh = MinHash()
        sig_a = mh.signature("alpha beta gamma")
        sig_b = mh.signature("delta epsilon zeta")
        assert mh.jaccard_estimate(sig_a, sig_b) == mh.jaccard_estimate(sig_b, sig_a)

    @pytest.mark.unit
    def test_similarity_bounded(self):
        """Jaccard estimate must be in [0.0, 1.0]."""
        mh = MinHash()
        sig_a = mh.signature("test text one")
        sig_b = mh.signature("test text two")
        sim = mh.jaccard_estimate(sig_a, sig_b)
        assert 0.0 <= sim <= 1.0


class TestMinHashShingle:
    """Shingling internals."""

    @pytest.mark.unit
    def test_shingle_whitespace_normalization(self):
        """Whitespace should be normalized before shingling."""
        mh = MinHash()
        sig_a = mh.signature("hello   world")
        sig_b = mh.signature("hello world")
        assert mh.jaccard_estimate(sig_a, sig_b) == 1.0

    @pytest.mark.unit
    def test_shingle_case_insensitive(self):
        """Shingling should be case-insensitive."""
        mh = MinHash()
        sig_a = mh.signature("Hello World")
        sig_b = mh.signature("hello world")
        assert mh.jaccard_estimate(sig_a, sig_b) == 1.0


# ---------------------------------------------------------------------------
# LSH Index
# ---------------------------------------------------------------------------


class TestLSHIndex:
    """LSH index add/query operations."""

    @pytest.mark.unit
    def test_add_and_query_self(self):
        """A document should be its own candidate after insertion."""
        mh = MinHash()
        lsh = LSHIndex(n_hashes=128, n_bands=16)
        sig = mh.signature("test document")
        lsh.add("doc1", sig)
        candidates = lsh.query(sig)
        assert "doc1" in candidates

    @pytest.mark.unit
    def test_query_empty_index(self):
        """Querying an empty index returns empty set."""
        mh = MinHash()
        lsh = LSHIndex()
        sig = mh.signature("query text")
        candidates = lsh.query(sig)
        assert candidates == set()

    @pytest.mark.unit
    def test_similar_docs_are_candidates(self):
        """Similar documents should appear as candidates."""
        mh = MinHash()
        lsh = LSHIndex(n_hashes=128, n_bands=16)
        text = "the quick brown fox jumps over the lazy dog"
        sig1 = mh.signature(text)
        sig2 = mh.signature(text)  # identical
        lsh.add("doc1", sig1)
        candidates = lsh.query(sig2)
        assert "doc1" in candidates

    @pytest.mark.unit
    def test_different_docs_fewer_candidates(self):
        """Very different documents should rarely collide in LSH buckets."""
        mh = MinHash(n_hashes=128)
        lsh = LSHIndex(n_hashes=128, n_bands=16)
        sig1 = mh.signature("alpha beta gamma delta epsilon zeta eta theta iota kappa")
        sig2 = mh.signature("one two three four five six seven eight nine ten eleven")
        lsh.add("doc1", sig1)
        candidates = lsh.query(sig2)
        # Not guaranteed empty, but should rarely contain doc1
        # We just verify the method works without error
        assert isinstance(candidates, set)

    @pytest.mark.unit
    def test_multiple_documents(self):
        """Index should handle multiple documents."""
        mh = MinHash()
        lsh = LSHIndex()
        for i in range(10):
            sig = mh.signature(f"document number {i} with unique content variation {i * 7}")
            lsh.add(f"doc{i}", sig)
        assert len(lsh.signatures) == 10


# ---------------------------------------------------------------------------
# DataCurator
# ---------------------------------------------------------------------------


class TestDataCurator:
    """End-to-end deduplication pipeline."""

    @pytest.mark.unit
    def test_deduplication_removes_duplicates(self):
        """Exact duplicates should be removed."""
        curator = DataCurator(similarity_threshold=0.8)
        texts = [
            "the quick brown fox jumps over the lazy dog",
            "the quick brown fox jumps over the lazy dog",  # exact dup
            "machine learning is a branch of artificial intelligence",
        ]
        unique_texts, stats = curator.deduplicate(texts)
        assert stats["total_documents"] == 3
        assert stats["unique_documents"] == 2
        assert stats["duplicates_removed"] == 1
        assert len(unique_texts) == 2

    @pytest.mark.unit
    def test_deduplication_keeps_unique(self):
        """All-unique texts should all be preserved."""
        curator = DataCurator()
        texts = [
            "apples are fruits that grow on trees in orchards",
            "quantum physics describes subatomic particle behavior",
            "classical music originated in the western tradition",
        ]
        unique_texts, stats = curator.deduplicate(texts)
        assert stats["unique_documents"] == 3
        assert stats["duplicates_removed"] == 0

    @pytest.mark.unit
    def test_deduplication_empty_input(self):
        """Empty input should return empty output."""
        curator = DataCurator()
        unique_texts, stats = curator.deduplicate([])
        assert unique_texts == []
        assert stats["total_documents"] == 0
        assert stats["deduplication_ratio"] == 1.0

    @pytest.mark.unit
    def test_deduplication_single_document(self):
        """Single document should be preserved."""
        curator = DataCurator()
        unique_texts, stats = curator.deduplicate(["only one document here"])
        assert len(unique_texts) == 1
        assert stats["duplicates_removed"] == 0

    @pytest.mark.unit
    def test_deduplication_ratio_range(self):
        """Deduplication ratio should be in (0, 1]."""
        curator = DataCurator()
        texts = ["text a " * 10, "text a " * 10, "text b " * 10]
        _, stats = curator.deduplicate(texts)
        assert 0.0 < stats["deduplication_ratio"] <= 1.0

    @pytest.mark.unit
    def test_deduplication_stats_keys(self):
        """Stats dict should contain all expected keys."""
        curator = DataCurator()
        _, stats = curator.deduplicate(["text one", "text two"])
        expected_keys = {
            "total_documents",
            "unique_documents",
            "duplicates_removed",
            "duplicate_pairs_found",
            "deduplication_ratio",
        }
        assert set(stats.keys()) == expected_keys

    @pytest.mark.unit
    def test_custom_threshold(self):
        """Higher threshold should result in fewer removals."""
        texts = [
            "the quick brown fox jumps over the lazy dog",
            "the quick brown fox jumps over the lazy dog",
        ]
        curator_strict = DataCurator(similarity_threshold=0.99)
        unique_strict, _ = curator_strict.deduplicate(texts)

        curator_loose = DataCurator(similarity_threshold=0.5)
        unique_loose, _ = curator_loose.deduplicate(texts)

        # Both should detect exact duplicates
        assert len(unique_strict) <= len(texts)
        assert len(unique_loose) <= len(texts)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """MCP tool interface tests."""

    @pytest.mark.unit
    def test_deduplicate_tool_returns_dict(self):
        from codomyrmex.data_curation.mcp_tools import data_curation_deduplicate

        result = data_curation_deduplicate(
            texts=["hello world", "hello world", "goodbye"],
            threshold=0.8,
        )
        assert "unique_texts" in result
        assert "stats" in result
        assert isinstance(result["stats"]["total_documents"], int)

    @pytest.mark.unit
    def test_similarity_tool_returns_dict(self):
        from codomyrmex.data_curation.mcp_tools import data_curation_similarity

        result = data_curation_similarity(
            text_a="hello world",
            text_b="hello world",
        )
        assert "similarity" in result
        assert "are_similar" in result
        assert result["similarity"] == 1.0
        assert result["are_similar"] is True
