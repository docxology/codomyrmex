"""Zero-mock tests for vector_store.models — SearchResult, VectorEntry, DistanceMetric,
and utility functions (normalize, random_embedding, batch_cosine_similarity, centroid)."""

import math
import time

import pytest

from codomyrmex.vector_store.models import (
    DistanceMetric,
    SearchResult,
    VectorEntry,
    batch_cosine_similarity,
    embedding_centroid,
    normalize_embedding,
    random_embedding,
)

# ──────────────────────────── SearchResult ────────────────────────────────


@pytest.mark.unit
class TestSearchResult:
    """Tests for the SearchResult dataclass."""

    def test_basic_construction(self):
        sr = SearchResult(id="doc-1", score=0.95, embedding=[0.1, 0.2, 0.3])
        assert sr.id == "doc-1"
        assert sr.score == pytest.approx(0.95)
        assert len(sr.embedding) == 3

    def test_metadata_default_empty(self):
        sr = SearchResult(id="x", score=0.5, embedding=[1.0])
        assert sr.metadata == {}

    def test_metadata_populated(self):
        sr = SearchResult(id="y", score=0.8, embedding=[0.0], metadata={"src": "wiki"})
        assert sr.metadata["src"] == "wiki"

    def test_lt_operator_lower_score(self):
        low = SearchResult(id="a", score=0.3, embedding=[0.0])
        high = SearchResult(id="b", score=0.9, embedding=[0.0])
        assert low < high

    def test_lt_operator_not_reversed(self):
        low = SearchResult(id="a", score=0.3, embedding=[0.0])
        high = SearchResult(id="b", score=0.9, embedding=[0.0])
        assert not (high < low)

    def test_sorting_by_score(self):
        results = [
            SearchResult(id="c", score=0.5, embedding=[]),
            SearchResult(id="a", score=0.9, embedding=[]),
            SearchResult(id="b", score=0.1, embedding=[]),
        ]
        sorted_results = sorted(results)
        assert [r.id for r in sorted_results] == ["b", "c", "a"]

    def test_repr_contains_id(self):
        sr = SearchResult(id="abc", score=0.75, embedding=[1.0, 2.0])
        assert "abc" in repr(sr)

    def test_repr_contains_score(self):
        sr = SearchResult(id="x", score=0.1234, embedding=[0.0])
        assert "0.1234" in repr(sr)

    def test_repr_contains_dim(self):
        sr = SearchResult(id="y", score=0.5, embedding=[0.1, 0.2, 0.3, 0.4])
        assert "dim=4" in repr(sr)


# ──────────────────────────── VectorEntry ─────────────────────────────────


@pytest.mark.unit
class TestVectorEntry:
    """Tests for VectorEntry dataclass."""

    def test_basic_construction(self):
        ve = VectorEntry(id="entry-1", embedding=[1.0, 0.0, 0.0])
        assert ve.id == "entry-1"
        assert ve.embedding == [1.0, 0.0, 0.0]

    def test_metadata_default_empty(self):
        ve = VectorEntry(id="e", embedding=[0.5])
        assert ve.metadata == {}

    def test_created_at_auto_set(self):
        before = time.time()
        ve = VectorEntry(id="e", embedding=[1.0])
        after = time.time()
        assert before <= ve.created_at.timestamp() <= after

    def test_updated_at_defaults_none(self):
        ve = VectorEntry(id="e", embedding=[1.0])
        assert ve.updated_at is None

    def test_dimension_property(self):
        ve = VectorEntry(id="e", embedding=[0.1, 0.2, 0.3, 0.4, 0.5])
        assert ve.dimension == 5

    def test_magnitude_unit_vector(self):
        # [1, 0, 0] has magnitude 1.0
        ve = VectorEntry(id="e", embedding=[1.0, 0.0, 0.0])
        assert ve.magnitude == pytest.approx(1.0)

    def test_magnitude_known_value(self):
        # [3, 4] -> sqrt(9+16) = 5
        ve = VectorEntry(id="e", embedding=[3.0, 4.0])
        assert ve.magnitude == pytest.approx(5.0)

    def test_update_embedding_changes_data(self):
        ve = VectorEntry(id="e", embedding=[1.0, 0.0])
        before_update = ve.updated_at
        ve.update_embedding([0.0, 1.0])
        assert ve.embedding == [0.0, 1.0]
        assert before_update is None
        assert ve.updated_at is not None

    def test_update_embedding_sets_timestamp(self):
        ve = VectorEntry(id="e", embedding=[1.0])
        t_before = time.time()
        ve.update_embedding([2.0])
        t_after = time.time()
        assert t_before <= ve.updated_at.timestamp() <= t_after

    def test_to_dict_keys(self):
        ve = VectorEntry(id="doc-7", embedding=[0.5, -0.5])
        d = ve.to_dict()
        assert "id" in d
        assert "embedding" in d
        assert "metadata" in d
        assert "dimension" in d
        assert "magnitude" in d
        assert "created_at" in d

    def test_to_dict_values(self):
        ve = VectorEntry(id="doc-7", embedding=[0.5, -0.5])
        d = ve.to_dict()
        assert d["id"] == "doc-7"
        assert d["dimension"] == 2

    def test_from_dict_round_trip(self):
        original = VectorEntry(
            id="vec-42", embedding=[0.1, 0.2, 0.3], metadata={"tag": "test"}
        )
        d = original.to_dict()
        restored = VectorEntry.from_dict(d)
        assert restored.id == original.id
        assert restored.embedding == original.embedding

    def test_from_dict_no_metadata(self):
        data = {"id": "x", "embedding": [1.0, 2.0]}
        ve = VectorEntry.from_dict(data)
        assert ve.metadata == {}


# ──────────────────────────── DistanceMetric ──────────────────────────────


@pytest.mark.unit
class TestDistanceMetric:
    """Tests for DistanceMetric static methods."""

    def test_cosine_identical_vectors(self):
        v = [1.0, 0.0, 0.0]
        assert DistanceMetric.cosine(v, v) == pytest.approx(1.0)

    def test_cosine_orthogonal_vectors(self):
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        assert DistanceMetric.cosine(v1, v2) == pytest.approx(0.0)

    def test_cosine_mismatched_dims_returns_zero(self):
        assert DistanceMetric.cosine([1.0], [1.0, 2.0]) == pytest.approx(0.0)

    def test_cosine_zero_vector_returns_zero(self):
        assert DistanceMetric.cosine([0.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)

    def test_euclidean_identical_vectors(self):
        v = [3.0, 4.0]
        assert DistanceMetric.euclidean(v, v) == pytest.approx(0.0)

    def test_euclidean_known_value(self):
        v1 = [0.0, 0.0]
        v2 = [3.0, 4.0]
        assert DistanceMetric.euclidean(v1, v2) == pytest.approx(5.0)

    def test_euclidean_mismatched_dims_returns_inf(self):
        result = DistanceMetric.euclidean([1.0], [1.0, 2.0])
        assert result == float("inf")

    def test_dot_product_unit_vectors(self):
        v1 = [1.0, 0.0]
        v2 = [1.0, 0.0]
        assert DistanceMetric.dot_product(v1, v2) == pytest.approx(1.0)

    def test_dot_product_orthogonal(self):
        assert DistanceMetric.dot_product([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_dot_product_mismatched_dims_returns_zero(self):
        assert DistanceMetric.dot_product([1.0, 2.0], [1.0]) == pytest.approx(0.0)

    def test_manhattan_known_value(self):
        v1 = [0.0, 0.0]
        v2 = [1.0, 1.0]
        assert DistanceMetric.manhattan(v1, v2) == pytest.approx(2.0)

    def test_manhattan_identical(self):
        v = [5.0, -3.0]
        assert DistanceMetric.manhattan(v, v) == pytest.approx(0.0)

    def test_manhattan_mismatched_dims_returns_inf(self):
        assert DistanceMetric.manhattan([1.0], [1.0, 2.0]) == float("inf")

    def test_chebyshev_known_value(self):
        v1 = [0.0, 0.0]
        v2 = [3.0, 10.0]
        assert DistanceMetric.chebyshev(v1, v2) == pytest.approx(10.0)

    def test_chebyshev_identical(self):
        v = [7.0, -2.0]
        assert DistanceMetric.chebyshev(v, v) == pytest.approx(0.0)

    def test_chebyshev_mismatched_dims_returns_inf(self):
        assert DistanceMetric.chebyshev([1.0], [1.0, 2.0]) == float("inf")


# ──────────────────────────── Utility Functions ───────────────────────────


@pytest.mark.unit
class TestUtilityFunctions:
    """Tests for module-level utility functions."""

    def test_normalize_embedding_unit_length(self):
        raw = [3.0, 4.0]
        norm = normalize_embedding(raw)
        magnitude = math.sqrt(sum(x * x for x in norm))
        assert magnitude == pytest.approx(1.0)

    def test_normalize_embedding_direction_preserved(self):
        raw = [1.0, 0.0]
        norm = normalize_embedding(raw)
        assert norm == pytest.approx([1.0, 0.0])

    def test_normalize_zero_vector_returns_original(self):
        zero = [0.0, 0.0, 0.0]
        result = normalize_embedding(zero)
        assert result == [0.0, 0.0, 0.0]

    def test_random_embedding_dim(self):
        emb = random_embedding(64)
        assert len(emb) == 64

    def test_random_embedding_unit_length(self):
        emb = random_embedding(32, seed=42)
        magnitude = math.sqrt(sum(x * x for x in emb))
        assert magnitude == pytest.approx(1.0, abs=1e-9)

    def test_random_embedding_reproducible_with_seed(self):
        emb1 = random_embedding(16, seed=99)
        emb2 = random_embedding(16, seed=99)
        assert emb1 == emb2

    def test_random_embedding_different_seeds_differ(self):
        emb1 = random_embedding(16, seed=1)
        emb2 = random_embedding(16, seed=2)
        assert emb1 != emb2

    def test_batch_cosine_similarity_length(self):
        query = [1.0, 0.0]
        candidates = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]]
        scores = batch_cosine_similarity(query, candidates)
        assert len(scores) == 3

    def test_batch_cosine_similarity_values(self):
        query = [1.0, 0.0]
        candidates = [[1.0, 0.0], [0.0, 1.0]]
        scores = batch_cosine_similarity(query, candidates)
        assert scores[0] == pytest.approx(1.0)
        assert scores[1] == pytest.approx(0.0)

    def test_embedding_centroid_single(self):
        embs = [[2.0, 4.0, 6.0]]
        centroid = embedding_centroid(embs)
        assert centroid == pytest.approx([2.0, 4.0, 6.0])

    def test_embedding_centroid_two_vectors(self):
        embs = [[1.0, 0.0], [0.0, 1.0]]
        centroid = embedding_centroid(embs)
        assert centroid == pytest.approx([0.5, 0.5])

    def test_embedding_centroid_empty_returns_empty(self):
        result = embedding_centroid([])
        assert result == []
