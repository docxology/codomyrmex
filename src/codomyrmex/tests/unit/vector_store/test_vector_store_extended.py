"""
Unit tests for vector_store.models and vector_store.store — Zero-Mock compliant.

Covers missing lines in models.py: SearchResult.__lt__/__repr__, VectorEntry
(dimension/magnitude/update_embedding/to_dict/from_dict), DistanceMetric
(mismatched-dimension fallbacks, chebyshev), utility functions
(random_embedding, batch_cosine_similarity, embedding_centroid).

Covers missing lines in store.py: euclidean/dot_product/unknown InMemoryVectorStore
init, add_batch, delete fallback, filter_fn search, list_ids,
NamespacedVectorStore (full API), create_vector_store.
"""

import math

import pytest

from codomyrmex.vector_store.models import (
    DistanceMetric,
    SearchResult,
    VectorEntry,
    batch_cosine_similarity,
    embedding_centroid,
    random_embedding,
)
from codomyrmex.vector_store.store import (
    InMemoryVectorStore,
    NamespacedVectorStore,
    create_vector_store,
)

# ── SearchResult ──────────────────────────────────────────────────────


@pytest.mark.unit
class TestSearchResult:
    def test_lt_lower_score_less_than(self):
        a = SearchResult(id="a", score=0.5, embedding=[1.0])
        b = SearchResult(id="b", score=0.9, embedding=[1.0])
        assert a < b

    def test_lt_higher_score_not_less(self):
        a = SearchResult(id="a", score=0.9, embedding=[1.0])
        b = SearchResult(id="b", score=0.5, embedding=[1.0])
        assert not (a < b)

    def test_repr_contains_id(self):
        r = SearchResult(id="doc-42", score=0.75, embedding=[1.0, 0.0])
        assert "doc-42" in repr(r)

    def test_repr_contains_score(self):
        r = SearchResult(id="x", score=0.8765, embedding=[1.0])
        assert "0.8765" in repr(r)

    def test_repr_contains_dimension(self):
        r = SearchResult(id="x", score=0.5, embedding=[1.0, 2.0, 3.0])
        assert "3" in repr(r)


# ── VectorEntry ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestVectorEntry:
    def test_dimension_property(self):
        e = VectorEntry(id="v1", embedding=[1.0, 2.0, 3.0])
        assert e.dimension == 3

    def test_magnitude_property(self):
        e = VectorEntry(id="v1", embedding=[3.0, 4.0])
        assert math.isclose(e.magnitude, 5.0)

    def test_magnitude_zero_vector(self):
        e = VectorEntry(id="v0", embedding=[0.0, 0.0, 0.0])
        assert e.magnitude == 0.0

    def test_update_embedding_changes_vector(self):
        e = VectorEntry(id="v1", embedding=[1.0, 0.0])
        e.update_embedding([0.0, 1.0])
        assert e.embedding == [0.0, 1.0]

    def test_update_embedding_sets_updated_at(self):
        e = VectorEntry(id="v1", embedding=[1.0])
        assert e.updated_at is None
        e.update_embedding([2.0])
        assert e.updated_at is not None

    def test_to_dict_keys(self):
        e = VectorEntry(id="v1", embedding=[1.0, 2.0])
        d = e.to_dict()
        for key in ("id", "embedding", "metadata", "dimension", "magnitude", "created_at"):
            assert key in d

    def test_to_dict_values(self):
        e = VectorEntry(id="vec", embedding=[1.0, 0.0], metadata={"tag": "test"})
        d = e.to_dict()
        assert d["id"] == "vec"
        assert d["embedding"] == [1.0, 0.0]
        assert d["metadata"]["tag"] == "test"
        assert d["dimension"] == 2

    def test_from_dict_reconstructs_entry(self):
        data = {"id": "v99", "embedding": [0.5, 0.5], "metadata": {"src": "test"}}
        e = VectorEntry.from_dict(data)
        assert e.id == "v99"
        assert e.embedding == [0.5, 0.5]
        assert e.metadata["src"] == "test"

    def test_from_dict_default_metadata(self):
        data = {"id": "bare", "embedding": [1.0]}
        e = VectorEntry.from_dict(data)
        assert e.metadata == {}


# ── DistanceMetric — mismatched dimensions ────────────────────────────


@pytest.mark.unit
class TestDistanceMetricMismatched:
    def test_cosine_mismatched_returns_zero(self):
        assert DistanceMetric.cosine([1.0, 0.0], [1.0, 0.0, 0.0]) == 0.0

    def test_cosine_zero_vector_returns_zero(self):
        assert DistanceMetric.cosine([0.0, 0.0], [1.0, 0.0]) == 0.0

    def test_euclidean_mismatched_returns_inf(self):
        result = DistanceMetric.euclidean([1.0, 2.0], [1.0])
        assert result == float("inf")

    def test_dot_product_mismatched_returns_zero(self):
        assert DistanceMetric.dot_product([1.0, 2.0], [3.0]) == 0.0

    def test_manhattan_mismatched_returns_inf(self):
        result = DistanceMetric.manhattan([1.0, 2.0], [1.0])
        assert result == float("inf")

    def test_manhattan_matched_correct(self):
        result = DistanceMetric.manhattan([0.0, 0.0], [3.0, 4.0])
        assert math.isclose(result, 7.0)


@pytest.mark.unit
class TestDistanceMetricChebyshev:
    def test_chebyshev_mismatched_returns_inf(self):
        result = DistanceMetric.chebyshev([1.0, 2.0], [1.0])
        assert result == float("inf")

    def test_chebyshev_matched_max_diff(self):
        result = DistanceMetric.chebyshev([0.0, 0.0], [3.0, 1.0])
        assert math.isclose(result, 3.0)

    def test_chebyshev_equal_vectors_zero(self):
        result = DistanceMetric.chebyshev([1.0, 2.0], [1.0, 2.0])
        assert result == 0.0


# ── Utility Functions ─────────────────────────────────────────────────


@pytest.mark.unit
class TestRandomEmbedding:
    def test_correct_dimension(self):
        emb = random_embedding(8)
        assert len(emb) == 8

    def test_unit_magnitude(self):
        emb = random_embedding(16)
        mag = math.sqrt(sum(x * x for x in emb))
        assert math.isclose(mag, 1.0, abs_tol=1e-6)

    def test_seed_reproducible(self):
        emb1 = random_embedding(4, seed=42)
        emb2 = random_embedding(4, seed=42)
        assert emb1 == emb2

    def test_different_seeds_different(self):
        emb1 = random_embedding(4, seed=1)
        emb2 = random_embedding(4, seed=2)
        assert emb1 != emb2


@pytest.mark.unit
class TestBatchCosineSimilarity:
    def test_returns_correct_length(self):
        query = [1.0, 0.0]
        candidates = [[1.0, 0.0], [0.0, 1.0], [0.5, 0.5]]
        scores = batch_cosine_similarity(query, candidates)
        assert len(scores) == 3

    def test_perfect_match_score_one(self):
        query = [1.0, 0.0]
        scores = batch_cosine_similarity(query, [[1.0, 0.0]])
        assert math.isclose(scores[0], 1.0, abs_tol=1e-6)

    def test_orthogonal_score_zero(self):
        query = [1.0, 0.0]
        scores = batch_cosine_similarity(query, [[0.0, 1.0]])
        assert math.isclose(scores[0], 0.0, abs_tol=1e-6)

    def test_empty_candidates(self):
        scores = batch_cosine_similarity([1.0, 0.0], [])
        assert scores == []


@pytest.mark.unit
class TestEmbeddingCentroid:
    def test_single_embedding_returns_itself(self):
        emb = [1.0, 2.0, 3.0]
        centroid = embedding_centroid([emb])
        assert centroid == pytest.approx(emb)

    def test_two_embeddings_mean(self):
        centroid = embedding_centroid([[0.0, 0.0], [2.0, 4.0]])
        assert centroid == pytest.approx([1.0, 2.0])

    def test_empty_list_returns_empty(self):
        assert embedding_centroid([]) == []

    def test_three_embeddings_mean(self):
        centroid = embedding_centroid([[0.0], [3.0], [6.0]])
        assert centroid == pytest.approx([3.0])


# ── InMemoryVectorStore — distance metric selection ───────────────────


@pytest.mark.unit
class TestInMemoryVectorStoreMetrics:
    def test_euclidean_metric_selected(self):
        store = InMemoryVectorStore(distance_metric="euclidean")
        store.add("a", [1.0, 0.0])
        store.add("b", [0.0, 1.0])
        results = store.search([1.0, 0.0], k=2)
        # With euclidean, lower distance is better (result[0] should be "a")
        assert results[0].id == "a"

    def test_dot_product_metric_selected(self):
        store = InMemoryVectorStore(distance_metric="dot_product")
        store.add("high", [10.0, 10.0])
        store.add("low", [0.1, 0.1])
        results = store.search([1.0, 1.0], k=2)
        assert results[0].id == "high"

    def test_unknown_metric_raises(self):
        with pytest.raises(ValueError, match="Unknown distance metric"):
            InMemoryVectorStore(distance_metric="hamming")


# ── InMemoryVectorStore — add_batch ───────────────────────────────────


@pytest.mark.unit
class TestInMemoryVectorStoreAddBatch:
    def test_add_batch_returns_count(self):
        store = InMemoryVectorStore()
        n = store.add_batch([
            ("a", [1.0, 0.0], {"tag": "first"}),
            ("b", [0.0, 1.0], {"tag": "second"}),
        ])
        assert n == 2

    def test_add_batch_vectors_searchable(self):
        store = InMemoryVectorStore()
        store.add_batch([
            ("doc1", [1.0, 0.0], None),
            ("doc2", [0.0, 1.0], None),
        ])
        assert store.count() == 2

    def test_add_batch_metadata_stored(self):
        store = InMemoryVectorStore()
        store.add_batch([("x", [1.0], {"src": "test"})])
        entry = store.get("x")
        assert entry.metadata["src"] == "test"

    def test_add_batch_empty_returns_zero(self):
        store = InMemoryVectorStore()
        n = store.add_batch([])
        assert n == 0


# ── InMemoryVectorStore — delete fallback ────────────────────────────


@pytest.mark.unit
class TestInMemoryVectorStoreDelete:
    def test_delete_existing_returns_true(self):
        store = InMemoryVectorStore()
        store.add("k1", [1.0])
        assert store.delete("k1") is True

    def test_delete_missing_returns_false(self):
        store = InMemoryVectorStore()
        assert store.delete("nonexistent") is False

    def test_delete_removes_entry(self):
        store = InMemoryVectorStore()
        store.add("k1", [1.0])
        store.delete("k1")
        assert store.get("k1") is None


# ── InMemoryVectorStore — filter_fn in search ────────────────────────


@pytest.mark.unit
class TestInMemoryVectorStoreFilter:
    def test_filter_fn_excludes_entries(self):
        store = InMemoryVectorStore()
        store.add("tagged", [1.0, 0.0], metadata={"keep": True})
        store.add("untagged", [1.0, 0.0], metadata={"keep": False})
        results = store.search([1.0, 0.0], k=10, filter_fn=lambda m: m.get("keep") is True)
        ids = [r.id for r in results]
        assert "tagged" in ids
        assert "untagged" not in ids

    def test_filter_fn_none_returns_all(self):
        store = InMemoryVectorStore()
        store.add("a", [1.0, 0.0])
        store.add("b", [0.0, 1.0])
        results = store.search([1.0, 0.0], k=10, filter_fn=None)
        assert len(results) == 2


# ── InMemoryVectorStore — list_ids ───────────────────────────────────


@pytest.mark.unit
class TestInMemoryVectorStoreListIds:
    def test_list_ids_empty_store(self):
        store = InMemoryVectorStore()
        assert store.list_ids() == []

    def test_list_ids_after_add(self):
        store = InMemoryVectorStore()
        store.add("id1", [1.0])
        store.add("id2", [0.0])
        ids = store.list_ids()
        assert "id1" in ids
        assert "id2" in ids
        assert len(ids) == 2

    def test_list_ids_after_delete(self):
        store = InMemoryVectorStore()
        store.add("x", [1.0])
        store.delete("x")
        assert store.list_ids() == []


# ── NamespacedVectorStore ─────────────────────────────────────────────


@pytest.mark.unit
class TestNamespacedVectorStore:
    def test_default_store_empty(self):
        ns = NamespacedVectorStore()
        assert ns.count() == 0

    def test_add_to_default_namespace(self):
        ns = NamespacedVectorStore()
        ns.add("v1", [1.0, 0.0])
        assert ns.count() == 1

    def test_get_from_default_namespace(self):
        ns = NamespacedVectorStore()
        ns.add("v1", [1.0], {"k": "v"})
        entry = ns.get("v1")
        assert entry is not None
        assert entry.id == "v1"

    def test_delete_from_default_namespace(self):
        ns = NamespacedVectorStore()
        ns.add("v1", [1.0])
        assert ns.delete("v1") is True
        assert ns.get("v1") is None

    def test_search_in_default_namespace(self):
        ns = NamespacedVectorStore()
        ns.add("a", [1.0, 0.0])
        results = ns.search([1.0, 0.0], k=1)
        assert len(results) == 1
        assert results[0].id == "a"

    def test_clear_default_namespace(self):
        ns = NamespacedVectorStore()
        ns.add("v1", [1.0])
        ns.clear()
        assert ns.count() == 0

    def test_use_namespace_creates_store(self):
        ns = NamespacedVectorStore()
        ns.use_namespace("alpha")
        ns.add("v1", [1.0, 0.0])
        assert ns.count() == 1

    def test_namespaces_isolated(self):
        ns = NamespacedVectorStore()
        ns.use_namespace("ns1")
        ns.add("shared_id", [1.0, 0.0])
        ns.use_namespace("ns2")
        assert ns.count() == 0

    def test_list_namespaces(self):
        ns = NamespacedVectorStore()
        ns.use_namespace("ns-a")
        ns.use_namespace("ns-b")
        namespaces = ns.list_namespaces()
        assert "ns-a" in namespaces
        assert "ns-b" in namespaces

    def test_delete_namespace_returns_true(self):
        ns = NamespacedVectorStore()
        ns.use_namespace("temp")
        assert ns.delete_namespace("temp") is True

    def test_delete_namespace_removes_it(self):
        ns = NamespacedVectorStore()
        ns.use_namespace("temp")
        ns.delete_namespace("temp")
        assert "temp" not in ns.list_namespaces()

    def test_delete_namespace_clears_current(self):
        ns = NamespacedVectorStore()
        ns.use_namespace("temp")
        ns.delete_namespace("temp")
        # After deleting active namespace, current resets to None (default store)
        ns.add("v1", [1.0])
        assert ns.count() == 1

    def test_delete_nonexistent_namespace_returns_false(self):
        ns = NamespacedVectorStore()
        assert ns.delete_namespace("phantom") is False

    def test_use_namespace_returns_self(self):
        ns = NamespacedVectorStore()
        result = ns.use_namespace("x")
        assert result is ns


# ── create_vector_store ───────────────────────────────────────────────


@pytest.mark.unit
class TestCreateVectorStore:
    def test_memory_backend_returns_in_memory(self):
        store = create_vector_store("memory")
        assert isinstance(store, InMemoryVectorStore)

    def test_namespaced_backend_returns_namespaced(self):
        store = create_vector_store("namespaced")
        assert isinstance(store, NamespacedVectorStore)

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError, match="Unknown backend"):
            create_vector_store("redis")

    def test_default_backend_is_memory(self):
        store = create_vector_store()
        assert isinstance(store, InMemoryVectorStore)

    def test_kwargs_passed_to_backend(self):
        store = create_vector_store("memory", distance_metric="euclidean")
        assert isinstance(store, InMemoryVectorStore)
