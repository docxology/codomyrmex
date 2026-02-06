"""Tests for vector_store module."""

import math

import pytest

try:
    from codomyrmex.vector_store import (
        DistanceMetric,
        InMemoryVectorStore,
        NamespacedVectorStore,
        SearchResult,
        VectorEntry,
        VectorStore,
        create_vector_store,
        normalize_embedding,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("vector_store module not available", allow_module_level=True)


@pytest.mark.unit
class TestDistanceMetric:
    def test_cosine_metric(self):
        score = DistanceMetric.cosine([1.0, 0.0], [1.0, 0.0])
        assert abs(score - 1.0) < 1e-6

    def test_euclidean_metric(self):
        score = DistanceMetric.euclidean([0.0, 0.0], [3.0, 4.0])
        assert abs(score - 5.0) < 1e-6

    def test_dot_product_metric(self):
        score = DistanceMetric.dot_product([1.0, 2.0], [3.0, 4.0])
        assert abs(score - 11.0) < 1e-6


@pytest.mark.unit
class TestVectorEntry:
    def test_create_entry(self):
        entry = VectorEntry(id="doc-1", embedding=[0.1, 0.2, 0.3], metadata={"text": "hello"})
        assert entry.id == "doc-1"
        assert len(entry.embedding) == 3

    def test_entry_metadata(self):
        entry = VectorEntry(id="doc-2", embedding=[1.0], metadata={"key": "value"})
        assert entry.metadata["key"] == "value"


@pytest.mark.unit
class TestNormalizeEmbedding:
    def test_normalize_unit_vector(self):
        result = normalize_embedding([1.0, 0.0, 0.0])
        assert abs(result[0] - 1.0) < 1e-6
        assert abs(result[1]) < 1e-6

    def test_normalize_scales_to_unit(self):
        result = normalize_embedding([3.0, 4.0])
        magnitude = math.sqrt(sum(x * x for x in result))
        assert abs(magnitude - 1.0) < 1e-6

    def test_normalize_zero_vector(self):
        result = normalize_embedding([0.0, 0.0, 0.0])
        assert all(x == 0.0 for x in result)


@pytest.mark.unit
class TestInMemoryVectorStore:
    def test_create_store(self):
        store = InMemoryVectorStore()
        assert store is not None

    def test_add_entry(self):
        store = InMemoryVectorStore()
        store.add(id="doc-1", embedding=[1.0, 0.0], metadata={})
        assert store.count() == 1

    def test_search_returns_results(self):
        store = InMemoryVectorStore()
        store.add(id="doc-1", embedding=[1.0, 0.0], metadata={})
        store.add(id="doc-2", embedding=[0.0, 1.0], metadata={})
        results = store.search([1.0, 0.0], k=1)
        assert len(results) == 1
        assert results[0].id == "doc-1"

    def test_search_top_k(self):
        store = InMemoryVectorStore()
        for i in range(10):
            store.add(id=f"doc-{i}", embedding=[float(i), 0.0], metadata={})
        results = store.search([5.0, 0.0], k=3)
        assert len(results) == 3

    def test_delete_entry(self):
        store = InMemoryVectorStore()
        store.add(id="doc-1", embedding=[1.0], metadata={})
        store.delete("doc-1")
        assert store.count() == 0

    def test_get_entry(self):
        store = InMemoryVectorStore()
        store.add(id="doc-1", embedding=[1.0, 2.0], metadata={"text": "hello"})
        entry = store.get("doc-1")
        assert entry is not None
        assert entry.id == "doc-1"

    def test_get_nonexistent(self):
        store = InMemoryVectorStore()
        entry = store.get("nonexistent")
        assert entry is None


@pytest.mark.unit
class TestNamespacedVectorStore:
    def test_create_namespaced_store(self):
        store = NamespacedVectorStore()
        assert store is not None

    def test_namespace_isolation(self):
        store = NamespacedVectorStore()
        store.use_namespace("ns1").add(id="doc-1", embedding=[1.0], metadata={})
        store.use_namespace("ns2").add(id="doc-2", embedding=[1.0], metadata={})
        results_ns1 = store.use_namespace("ns1").search([1.0], k=10)
        assert len(results_ns1) == 1


@pytest.mark.unit
class TestCreateVectorStore:
    def test_factory_creates_store(self):
        store = create_vector_store()
        assert store is not None
        assert isinstance(store, InMemoryVectorStore)
