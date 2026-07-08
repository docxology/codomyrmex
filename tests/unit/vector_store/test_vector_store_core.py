from __future__ import annotations

"""Zero-mock tests for vector_store.models, vector_store.store, vector_store._search_mixin.

Coverage targets (all at 0%):
  - vector_store/models.py        (87 stmts)
  - vector_store/store.py         (100 stmts)
  - vector_store/_search_mixin.py (16 stmts)
"""

import importlib.util
import math
import threading

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
from codomyrmex.vector_store.store import (
    InMemoryVectorStore,
    NamespacedVectorStore,
    VectorStore,
    create_vector_store,
)

_CHROMADB_AVAILABLE = importlib.util.find_spec("chromadb") is not None


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def store() -> InMemoryVectorStore:
    return InMemoryVectorStore(distance_metric="cosine")


@pytest.fixture
def populated_store() -> InMemoryVectorStore:
    s = InMemoryVectorStore(distance_metric="cosine")
    s.add("a", [1.0, 0.0, 0.0], {"tag": "alpha"})
    s.add("b", [0.0, 1.0, 0.0], {"tag": "beta"})
    s.add("c", [0.0, 0.0, 1.0], {"tag": "gamma"})
    return s


# ─── TestSearchResult ─────────────────────────────────────────────────────────


class TestSearchResult:
    def test_lt_ordering(self) -> None:
        """ISC-3: __lt__ returns True when score is less."""
        low = SearchResult(id="low", score=0.1, embedding=[1.0])
        high = SearchResult(id="high", score=0.9, embedding=[1.0])
        assert low < high
        assert not (high < low)

    def test_repr_format(self) -> None:
        """ISC-4: __repr__ contains id, formatted score and dim."""
        r = SearchResult(id="foo", score=0.5678, embedding=[0.1, 0.2, 0.3])
        text = repr(r)
        assert "foo" in text
        assert "0.5678" in text
        assert "dim=3" in text

    def test_default_metadata_is_empty_dict(self) -> None:
        """ISC-5: metadata defaults to {}."""
        r = SearchResult(id="x", score=1.0, embedding=[1.0])
        assert r.metadata == {}

    def test_explicit_metadata_stored(self) -> None:
        r = SearchResult(id="x", score=1.0, embedding=[1.0], metadata={"k": "v"})
        assert r.metadata["k"] == "v"

    def test_sort_by_score(self) -> None:
        """Sorting a list of SearchResult uses __lt__ correctly."""
        results = [
            SearchResult(id="c", score=0.3, embedding=[]),
            SearchResult(id="a", score=0.9, embedding=[]),
            SearchResult(id="b", score=0.6, embedding=[]),
        ]
        results.sort()
        assert [r.id for r in results] == ["c", "b", "a"]


# ─── TestVectorEntry ──────────────────────────────────────────────────────────


class TestVectorEntry:
    def test_dimension_property(self) -> None:
        """ISC-6: dimension returns len(embedding)."""
        entry = VectorEntry(id="v1", embedding=[1.0, 2.0, 3.0])
        assert entry.dimension == 3

    def test_magnitude_property_known_vector(self) -> None:
        """ISC-7: magnitude returns correct L2 norm."""
        entry = VectorEntry(id="v1", embedding=[3.0, 4.0])
        assert entry.magnitude == pytest.approx(5.0)

    def test_magnitude_unit_vector(self) -> None:
        entry = VectorEntry(id="u", embedding=[1.0, 0.0, 0.0])
        assert entry.magnitude == pytest.approx(1.0)

    def test_magnitude_zero_vector(self) -> None:
        entry = VectorEntry(id="z", embedding=[0.0, 0.0])
        assert entry.magnitude == pytest.approx(0.0)

    def test_update_embedding_changes_values(self) -> None:
        """ISC-8: update_embedding replaces embedding."""
        entry = VectorEntry(id="e1", embedding=[1.0, 2.0])
        entry.update_embedding([9.0, 8.0])
        assert entry.embedding == [9.0, 8.0]

    def test_update_embedding_sets_updated_at(self) -> None:
        """ISC-9: update_embedding sets updated_at."""
        entry = VectorEntry(id="e1", embedding=[1.0])
        assert entry.updated_at is None
        entry.update_embedding([2.0])
        assert entry.updated_at is not None

    def test_to_dict_keys(self) -> None:
        """ISC-10: to_dict has expected keys."""
        entry = VectorEntry(id="d1", embedding=[1.0, 2.0], metadata={"x": 1})
        d = entry.to_dict()
        assert set(d.keys()) == {
            "id",
            "embedding",
            "metadata",
            "dimension",
            "magnitude",
            "created_at",
        }

    def test_to_dict_values(self) -> None:
        entry = VectorEntry(id="d1", embedding=[3.0, 4.0], metadata={"tag": "t"})
        d = entry.to_dict()
        assert d["id"] == "d1"
        assert d["embedding"] == [3.0, 4.0]
        assert d["metadata"] == {"tag": "t"}
        assert d["dimension"] == 2
        assert d["magnitude"] == pytest.approx(5.0)

    def test_to_dict_created_at_is_isoformat(self) -> None:
        entry = VectorEntry(id="ts", embedding=[1.0])
        d = entry.to_dict()
        # ISO format strings contain "T"
        assert "T" in d["created_at"]

    def test_from_dict_roundtrip_id_embedding(self) -> None:
        """ISC-11: from_dict reconstructs id and embedding correctly."""
        original = VectorEntry(id="orig", embedding=[0.5, 0.5], metadata={"m": 1})
        d = original.to_dict()
        restored = VectorEntry.from_dict(d)
        assert restored.id == "orig"
        assert restored.embedding == [0.5, 0.5]

    def test_from_dict_metadata_preserved(self) -> None:
        d = {"id": "m1", "embedding": [1.0], "metadata": {"k": "v"}}
        entry = VectorEntry.from_dict(d)
        assert entry.metadata == {"k": "v"}

    def test_from_dict_no_metadata_defaults_to_empty(self) -> None:
        """ISC-12: from_dict defaults metadata to {} when absent."""
        d = {"id": "bare", "embedding": [1.0, 0.0]}
        entry = VectorEntry.from_dict(d)
        assert entry.metadata == {}

    def test_default_metadata_is_empty_dict(self) -> None:
        entry = VectorEntry(id="e", embedding=[1.0])
        assert entry.metadata == {}

    def test_created_at_is_set_on_construction(self) -> None:
        entry = VectorEntry(id="e", embedding=[1.0])
        assert entry.created_at is not None

    def test_updated_at_is_none_by_default(self) -> None:
        entry = VectorEntry(id="e", embedding=[1.0])
        assert entry.updated_at is None


# ─── TestDistanceMetric ───────────────────────────────────────────────────────


class TestDistanceMetric:
    def test_cosine_identical_vectors(self) -> None:
        """ISC-13: cosine of identical non-zero vectors is 1.0."""
        v = [1.0, 2.0, 3.0]
        assert DistanceMetric.cosine(v, v) == pytest.approx(1.0)

    def test_cosine_orthogonal_vectors(self) -> None:
        """ISC-14: cosine of orthogonal vectors is 0.0."""
        assert DistanceMetric.cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_cosine_mismatched_dims_returns_zero(self) -> None:
        """ISC-15: cosine returns 0.0 on mismatched dims."""
        assert DistanceMetric.cosine([1.0], [1.0, 2.0]) == 0.0

    def test_cosine_zero_vector_returns_zero(self) -> None:
        """ISC-16: cosine with zero vector returns 0.0."""
        assert DistanceMetric.cosine([0.0, 0.0], [1.0, 1.0]) == 0.0

    def test_cosine_anti_parallel_vectors(self) -> None:
        """Opposite direction vectors have cosine of -1.0."""
        assert DistanceMetric.cosine([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_cosine_known_angle(self) -> None:
        """45-degree angle vectors have cosine ~0.7071."""
        v1 = [1.0, 0.0]
        v2 = [1.0, 1.0]
        expected = 1.0 / math.sqrt(2)
        assert DistanceMetric.cosine(v1, v2) == pytest.approx(expected, abs=1e-6)

    def test_euclidean_identical_vectors(self) -> None:
        """ISC-17: euclidean distance of identical vectors is 0.0."""
        v = [1.0, 2.0, 3.0]
        assert DistanceMetric.euclidean(v, v) == pytest.approx(0.0)

    def test_euclidean_known_distance(self) -> None:
        """3-4-5 right triangle gives distance 5.0."""
        assert DistanceMetric.euclidean([0.0, 0.0], [3.0, 4.0]) == pytest.approx(5.0)

    def test_euclidean_mismatched_dims_returns_inf(self) -> None:
        """ISC-18: euclidean returns inf on mismatched dims."""
        result = DistanceMetric.euclidean([1.0], [1.0, 2.0])
        assert result == float("inf")

    def test_dot_product_known_value(self) -> None:
        """ISC-19: dot product returns correct scalar."""
        assert DistanceMetric.dot_product(
            [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]
        ) == pytest.approx(32.0)

    def test_dot_product_orthogonal_zero(self) -> None:
        assert DistanceMetric.dot_product([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_dot_product_mismatched_dims_returns_zero(self) -> None:
        assert DistanceMetric.dot_product([1.0], [1.0, 2.0]) == 0.0

    def test_manhattan_known_distance(self) -> None:
        """ISC-20: manhattan distance is sum of absolute differences."""
        assert DistanceMetric.manhattan(
            [1.0, 2.0, 3.0], [4.0, 2.0, 1.0]
        ) == pytest.approx(5.0)

    def test_manhattan_identical_vectors(self) -> None:
        assert DistanceMetric.manhattan([1.0, 2.0], [1.0, 2.0]) == pytest.approx(0.0)

    def test_manhattan_mismatched_dims_returns_inf(self) -> None:
        result = DistanceMetric.manhattan([1.0], [1.0, 2.0])
        assert result == float("inf")

    def test_chebyshev_known_distance(self) -> None:
        """ISC-21: chebyshev distance is max of absolute differences."""
        assert DistanceMetric.chebyshev(
            [1.0, 5.0, 3.0], [4.0, 2.0, 3.0]
        ) == pytest.approx(3.0)

    def test_chebyshev_identical_vectors(self) -> None:
        assert DistanceMetric.chebyshev([1.0, 2.0], [1.0, 2.0]) == pytest.approx(0.0)

    def test_chebyshev_mismatched_dims_returns_inf(self) -> None:
        result = DistanceMetric.chebyshev([1.0], [1.0, 2.0])
        assert result == float("inf")


# ─── TestUtilityFunctions ─────────────────────────────────────────────────────


class TestUtilityFunctions:
    def test_normalize_embedding_produces_unit_vector(self) -> None:
        """ISC-22: normalized embedding has magnitude ~1.0."""
        v = [3.0, 4.0]
        normed = normalize_embedding(v)
        magnitude = math.sqrt(sum(x * x for x in normed))
        assert magnitude == pytest.approx(1.0)

    def test_normalize_embedding_direction_preserved(self) -> None:
        v = [1.0, 0.0]
        normed = normalize_embedding(v)
        assert normed[0] == pytest.approx(1.0)
        assert normed[1] == pytest.approx(0.0)

    def test_normalize_embedding_zero_vector_no_crash(self) -> None:
        """ISC-23: normalize of zero vector returns zero vector without error."""
        result = normalize_embedding([0.0, 0.0, 0.0])
        assert result == [0.0, 0.0, 0.0]

    def test_random_embedding_is_reproducible_with_seed(self) -> None:
        """ISC-24: same seed produces same embedding."""
        e1 = random_embedding(16, seed=42)
        e2 = random_embedding(16, seed=42)
        assert e1 == e2

    def test_random_embedding_different_seeds_differ(self) -> None:
        e1 = random_embedding(16, seed=1)
        e2 = random_embedding(16, seed=2)
        assert e1 != e2

    def test_random_embedding_is_unit_normalized(self) -> None:
        e = random_embedding(32, seed=99)
        magnitude = math.sqrt(sum(x * x for x in e))
        assert magnitude == pytest.approx(1.0, abs=1e-6)

    def test_random_embedding_correct_dimension(self) -> None:
        e = random_embedding(128, seed=7)
        assert len(e) == 128

    def test_batch_cosine_similarity_length(self) -> None:
        """ISC-25: batch result list has same length as candidates."""
        query = [1.0, 0.0, 0.0]
        candidates = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        scores = batch_cosine_similarity(query, candidates)
        assert len(scores) == 3

    def test_batch_cosine_similarity_values(self) -> None:
        query = [1.0, 0.0]
        candidates = [[1.0, 0.0], [0.0, 1.0]]
        scores = batch_cosine_similarity(query, candidates)
        assert scores[0] == pytest.approx(1.0)
        assert scores[1] == pytest.approx(0.0)

    def test_batch_cosine_similarity_empty_candidates(self) -> None:
        result = batch_cosine_similarity([1.0, 0.0], [])
        assert result == []

    def test_embedding_centroid_single_vector(self) -> None:
        """ISC-26: centroid of a single vector equals that vector."""
        v = [1.0, 2.0, 3.0]
        centroid = embedding_centroid([v])
        assert centroid == pytest.approx(v)

    def test_embedding_centroid_empty_returns_empty(self) -> None:
        """ISC-27: centroid of empty list returns []."""
        assert embedding_centroid([]) == []

    def test_embedding_centroid_two_vectors(self) -> None:
        a = [1.0, 3.0]
        b = [3.0, 1.0]
        centroid = embedding_centroid([a, b])
        assert centroid == pytest.approx([2.0, 2.0])

    def test_embedding_centroid_three_vectors(self) -> None:
        vecs = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
        centroid = embedding_centroid(vecs)
        assert centroid == pytest.approx([1 / 3, 1 / 3])


# ─── TestInMemoryVectorStore ──────────────────────────────────────────────────


class TestInMemoryVectorStore:
    def test_add_then_get_returns_entry(self, store: InMemoryVectorStore) -> None:
        """ISC-28: add then get returns the correct entry."""
        store.add("v1", [1.0, 0.0], {"tag": "x"})
        entry = store.get("v1")
        assert entry is not None
        assert entry.id == "v1"
        assert entry.embedding == [1.0, 0.0]

    def test_get_missing_id_returns_none(self, store: InMemoryVectorStore) -> None:
        """ISC-29: get on unknown id returns None."""
        assert store.get("nonexistent") is None

    def test_delete_existing_returns_true(self, store: InMemoryVectorStore) -> None:
        """ISC-30: delete on existing id returns True."""
        store.add("d1", [1.0])
        assert store.delete("d1") is True

    def test_delete_removes_entry(self, store: InMemoryVectorStore) -> None:
        store.add("d1", [1.0])
        store.delete("d1")
        assert store.get("d1") is None

    def test_delete_missing_returns_false(self, store: InMemoryVectorStore) -> None:
        """ISC-31: delete on missing id returns False."""
        assert store.delete("ghost") is False

    def test_count_increments_on_add(self, store: InMemoryVectorStore) -> None:
        """ISC-32: count increases with each add."""
        assert store.count() == 0
        store.add("x1", [1.0])
        assert store.count() == 1
        store.add("x2", [2.0])
        assert store.count() == 2

    def test_count_after_delete(self, store: InMemoryVectorStore) -> None:
        store.add("x1", [1.0])
        store.add("x2", [2.0])
        store.delete("x1")
        assert store.count() == 1

    def test_clear_resets_count_to_zero(self, store: InMemoryVectorStore) -> None:
        """ISC-33: clear() resets count to 0."""
        store.add("a", [1.0])
        store.add("b", [2.0])
        store.clear()
        assert store.count() == 0

    def test_clear_makes_get_return_none(self, store: InMemoryVectorStore) -> None:
        store.add("a", [1.0])
        store.clear()
        assert store.get("a") is None

    def test_list_ids_returns_all_ids(self, store: InMemoryVectorStore) -> None:
        """ISC-34: list_ids returns all added ids."""
        store.add("id1", [1.0])
        store.add("id2", [2.0])
        ids = store.list_ids()
        assert set(ids) == {"id1", "id2"}

    def test_list_ids_empty_store(self, store: InMemoryVectorStore) -> None:
        assert store.list_ids() == []

    def test_add_batch_returns_count(self, store: InMemoryVectorStore) -> None:
        """ISC-35: add_batch returns number of items added."""
        batch = [("b1", [1.0, 0.0], {"k": "v"}), ("b2", [0.0, 1.0], None)]
        count = store.add_batch(batch)
        assert count == 2

    def test_add_batch_entries_retrievable(self, store: InMemoryVectorStore) -> None:
        batch = [("b1", [1.0, 0.0], {"tag": "first"})]
        store.add_batch(batch)
        entry = store.get("b1")
        assert entry is not None
        assert entry.embedding == [1.0, 0.0]
        assert entry.metadata == {"tag": "first"}

    def test_add_batch_none_metadata_defaults_to_empty(
        self, store: InMemoryVectorStore
    ) -> None:
        store.add_batch([("b2", [1.0], None)])
        entry = store.get("b2")
        assert entry is not None
        assert entry.metadata == {}

    def test_add_overwrites_existing_id(self, store: InMemoryVectorStore) -> None:
        store.add("ov", [1.0, 0.0])
        store.add("ov", [0.0, 1.0])
        entry = store.get("ov")
        assert entry is not None
        assert entry.embedding == [0.0, 1.0]

    def test_search_returns_top_k_by_cosine(
        self, populated_store: InMemoryVectorStore
    ) -> None:
        """ISC-36: search with query [1,0,0] returns 'a' first."""
        results = populated_store.search([1.0, 0.0, 0.0], k=3)
        assert len(results) == 3
        assert results[0].id == "a"
        assert results[0].score == pytest.approx(1.0)

    def test_search_k_limits_results(
        self, populated_store: InMemoryVectorStore
    ) -> None:
        results = populated_store.search([1.0, 0.0, 0.0], k=1)
        assert len(results) == 1

    def test_search_k_larger_than_store_returns_all(
        self, populated_store: InMemoryVectorStore
    ) -> None:
        results = populated_store.search([1.0, 0.0, 0.0], k=100)
        assert len(results) == 3

    def test_search_empty_store_returns_empty_list(
        self, store: InMemoryVectorStore
    ) -> None:
        results = store.search([1.0, 0.0], k=5)
        assert results == []

    def test_search_with_filter_fn_excludes_non_matching(
        self, populated_store: InMemoryVectorStore
    ) -> None:
        """ISC-37: filter_fn excludes entries whose metadata doesn't match."""
        results = populated_store.search(
            [1.0, 0.0, 0.0],
            k=10,
            filter_fn=lambda meta: meta.get("tag") == "alpha",
        )
        assert len(results) == 1
        assert results[0].id == "a"

    def test_search_filter_fn_no_match_returns_empty(
        self, populated_store: InMemoryVectorStore
    ) -> None:
        results = populated_store.search(
            [1.0, 0.0, 0.0],
            k=10,
            filter_fn=lambda meta: meta.get("tag") == "zzz",
        )
        assert results == []

    def test_search_result_has_metadata(
        self, populated_store: InMemoryVectorStore
    ) -> None:
        results = populated_store.search([1.0, 0.0, 0.0], k=1)
        assert results[0].metadata == {"tag": "alpha"}

    def test_euclidean_metric_orders_by_distance(self) -> None:
        """ISC-38: euclidean metric returns lower-distance results first."""
        s = InMemoryVectorStore(distance_metric="euclidean")
        s.add("close", [1.0, 0.0])
        s.add("far", [100.0, 0.0])
        results = s.search([0.0, 0.0], k=2)
        assert results[0].id == "close"

    def test_dot_product_metric_orders_by_score(self) -> None:
        """ISC-39: dot_product metric returns higher scores first."""
        s = InMemoryVectorStore(distance_metric="dot_product")
        s.add("small", [0.1, 0.0])
        s.add("large", [10.0, 0.0])
        results = s.search([1.0, 0.0], k=2)
        assert results[0].id == "large"

    def test_unknown_metric_raises_value_error(self) -> None:
        """ISC-40: unknown distance metric raises ValueError."""
        with pytest.raises(ValueError, match="Unknown distance metric"):
            InMemoryVectorStore(distance_metric="hamming")

    def test_thread_safe_concurrent_adds(self, store: InMemoryVectorStore) -> None:
        """ISC-41: concurrent adds from 50 threads all succeed."""
        n_threads = 50

        def add_vector(idx: int) -> None:
            store.add(f"t{idx}", [float(idx)])

        threads = [
            threading.Thread(target=add_vector, args=(i,)) for i in range(n_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert store.count() == n_threads

    def test_thread_safe_concurrent_deletes(self, store: InMemoryVectorStore) -> None:
        """Concurrent deletes do not raise errors."""
        for i in range(20):
            store.add(f"del{i}", [float(i)])

        def delete_vector(idx: int) -> None:
            store.delete(f"del{idx}")

        threads = [threading.Thread(target=delete_vector, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert store.count() == 0

    def test_is_abstract_base_class(self) -> None:
        """VectorStore ABC cannot be instantiated directly."""
        import abc

        assert issubclass(VectorStore, abc.ABC)

    def test_search_results_sorted_descending_cosine(self) -> None:
        """Cosine search results are sorted highest score first."""
        s = InMemoryVectorStore(distance_metric="cosine")
        s.add("x", [1.0, 0.0])
        s.add("y", [0.707, 0.707])
        s.add("z", [0.0, 1.0])
        results = s.search([1.0, 0.0], k=3)
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_results_sorted_ascending_euclidean(self) -> None:
        """Euclidean search results are sorted lowest distance first."""
        s = InMemoryVectorStore(distance_metric="euclidean")
        s.add("near", [0.1, 0.0])
        s.add("mid", [1.0, 0.0])
        s.add("far", [5.0, 0.0])
        results = s.search([0.0, 0.0], k=3)
        scores = [r.score for r in results]
        assert scores == sorted(scores)


# ─── TestNamespacedVectorStore ────────────────────────────────────────────────


class TestNamespacedVectorStore:
    def test_use_namespace_returns_self(self) -> None:
        ns = NamespacedVectorStore()
        result = ns.use_namespace("ns1")
        assert result is ns

    def test_use_namespace_creates_isolated_store(self) -> None:
        """ISC-42: vectors added to ns-A are not visible in ns-B."""
        ns = NamespacedVectorStore()
        ns.use_namespace("ns-a")
        ns.add("vec1", [1.0, 0.0])

        ns.use_namespace("ns-b")
        assert ns.get("vec1") is None

    def test_data_in_ns_a_not_visible_in_ns_b(self) -> None:
        """ISC-43: separate namespace counts are independent."""
        ns = NamespacedVectorStore()
        ns.use_namespace("a")
        ns.add("a1", [1.0])
        ns.add("a2", [2.0])

        ns.use_namespace("b")
        assert ns.count() == 0

    def test_list_namespaces_returns_created(self) -> None:
        """ISC-44: list_namespaces returns all created namespaces."""
        ns = NamespacedVectorStore()
        ns.use_namespace("x")
        ns.use_namespace("y")
        namespaces = ns.list_namespaces()
        assert "x" in namespaces
        assert "y" in namespaces

    def test_delete_namespace_returns_true(self) -> None:
        """ISC-45: delete_namespace returns True on success."""
        ns = NamespacedVectorStore()
        ns.use_namespace("del-me")
        assert ns.delete_namespace("del-me") is True

    def test_delete_namespace_removes_from_list(self) -> None:
        ns = NamespacedVectorStore()
        ns.use_namespace("temp")
        ns.delete_namespace("temp")
        assert "temp" not in ns.list_namespaces()

    def test_delete_namespace_resets_current_to_none(self) -> None:
        """ISC-46: deleting current namespace resets current to None (falls back to default store)."""
        ns = NamespacedVectorStore()
        ns.use_namespace("current")
        ns.add("v1", [1.0])
        ns.delete_namespace("current")
        # Should not raise; falls back to default store
        assert ns.get("v1") is None

    def test_delete_nonexistent_namespace_returns_false(self) -> None:
        ns = NamespacedVectorStore()
        assert ns.delete_namespace("ghost") is False

    def test_default_store_used_when_no_namespace_set(self) -> None:
        """ISC-47: operations route to default store when no namespace is active."""
        ns = NamespacedVectorStore()
        ns.add("def1", [1.0, 0.0])
        assert ns.get("def1") is not None
        assert ns.count() == 1

    def test_namespace_store_operations_complete(self) -> None:
        """search, delete, clear all work within a namespace."""
        ns = NamespacedVectorStore()
        ns.use_namespace("ops")
        ns.add("o1", [1.0, 0.0])
        ns.add("o2", [0.0, 1.0])
        results = ns.search([1.0, 0.0], k=2)
        assert len(results) == 2
        ns.delete("o1")
        assert ns.count() == 1
        ns.clear()
        assert ns.count() == 0

    def test_multiple_namespaces_independent_after_switching(self) -> None:
        ns = NamespacedVectorStore()
        ns.use_namespace("first")
        ns.add("f1", [1.0])
        ns.use_namespace("second")
        ns.add("s1", [2.0])
        ns.add("s2", [3.0])

        ns.use_namespace("first")
        assert ns.count() == 1

        ns.use_namespace("second")
        assert ns.count() == 2

    def test_custom_base_store(self) -> None:
        base = InMemoryVectorStore()
        ns = NamespacedVectorStore(base_store=base)
        # With no namespace active, default store is base
        ns.add("b1", [1.0])
        assert ns.count() == 1


# ─── TestCreateVectorStore ────────────────────────────────────────────────────


class TestCreateVectorStore:
    def test_memory_backend_returns_in_memory_store(self) -> None:
        """ISC-48: memory backend returns InMemoryVectorStore."""
        s = create_vector_store("memory")
        assert isinstance(s, InMemoryVectorStore)

    def test_namespaced_backend_returns_namespaced_store(self) -> None:
        """ISC-49: namespaced backend returns NamespacedVectorStore."""
        s = create_vector_store("namespaced")
        assert isinstance(s, NamespacedVectorStore)

    def test_unknown_backend_raises_value_error(self) -> None:
        """ISC-50: unknown backend raises ValueError."""
        with pytest.raises(ValueError, match="Unknown backend"):
            create_vector_store("faiss")

    @pytest.mark.skipif(
        _CHROMADB_AVAILABLE,
        reason="chromadb IS installed — chroma backend would succeed",
    )
    def test_chroma_backend_raises_without_chromadb(self) -> None:
        """ISC-51: chroma backend raises ValueError when chromadb is not installed."""
        with pytest.raises(ValueError, match="chromadb"):
            create_vector_store("chroma")

    def test_memory_backend_default_metric_is_cosine(self) -> None:
        s = create_vector_store("memory")
        # cosine: higher_is_better == True
        assert s._higher_is_better is True

    def test_memory_backend_accepts_distance_metric_kwarg(self) -> None:
        s = create_vector_store("memory", distance_metric="euclidean")
        assert isinstance(s, InMemoryVectorStore)
        assert s._higher_is_better is False

    def test_created_memory_store_is_functional(self) -> None:
        s = create_vector_store("memory")
        s.add("func_test", [1.0, 2.0])
        assert s.count() == 1
        assert s.get("func_test") is not None

    def test_created_namespaced_store_is_functional(self) -> None:
        s = create_vector_store("namespaced")
        s.use_namespace("test_ns")
        s.add("ns_vec", [0.5, 0.5])
        assert s.count() == 1
