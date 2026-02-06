"""Tests for vector_store.persistent module."""

import json
import os

import pytest

try:
    from codomyrmex.vector_store import (
        InMemoryVectorStore,
        SearchResult,
        VectorEntry,
        VectorStore,
    )
    from codomyrmex.vector_store.persistent import (
        CachedVectorStore,
        PersistentVectorStore,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("vector_store.persistent module not available", allow_module_level=True)


# ---------------------------------------------------------------------------
# PersistentVectorStore
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPersistentVectorStore:
    def test_create(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        assert store.count() == 0

    def test_add_and_get(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        store.add("v1", [1.0, 0.0, 0.0], {"label": "test"})
        entry = store.get("v1")
        assert entry is not None
        assert entry.id == "v1"
        assert entry.embedding == [1.0, 0.0, 0.0]
        assert entry.metadata["label"] == "test"

    def test_get_nonexistent(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        assert store.get("nonexistent") is None

    def test_delete(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        store.add("v1", [1.0, 0.0])
        assert store.delete("v1") is True
        assert store.get("v1") is None
        assert store.count() == 0

    def test_delete_nonexistent(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        assert store.delete("nonexistent") is False

    def test_count(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        assert store.count() == 2

    def test_clear(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        store.clear()
        assert store.count() == 0

    def test_search_cosine(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path, distance_metric="cosine")
        store.add("v1", [1.0, 0.0, 0.0])
        store.add("v2", [0.0, 1.0, 0.0])
        store.add("v3", [1.0, 0.1, 0.0])

        results = store.search([1.0, 0.0, 0.0], k=2)
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        # v1 should be most similar (identical vector)
        assert results[0].id == "v1"

    def test_search_euclidean(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path, distance_metric="euclidean")
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        results = store.search([1.0, 0.0], k=2)
        assert len(results) == 2
        # Euclidean: lower is better, so v1 should be first
        assert results[0].id == "v1"

    def test_search_dot_product(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path, distance_metric="dot_product")
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        results = store.search([1.0, 0.0])
        assert len(results) >= 1

    def test_invalid_distance_metric(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        with pytest.raises(ValueError, match="Unknown distance metric"):
            PersistentVectorStore(path=path, distance_metric="invalid")

    def test_search_with_filter(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        store.add("v1", [1.0, 0.0], {"category": "a"})
        store.add("v2", [0.9, 0.1], {"category": "b"})
        results = store.search(
            [1.0, 0.0],
            filter_fn=lambda m: m.get("category") == "a",
        )
        assert len(results) == 1
        assert results[0].id == "v1"

    def test_flush_saves_to_disk(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path, auto_save=False)
        store.add("v1", [1.0, 0.0])
        store.flush()
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert len(data["vectors"]) == 1

    def test_compact(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store = PersistentVectorStore(path=path)
        store.add("v1", [1.0, 0.0])
        store.compact()  # Should not raise
        assert os.path.exists(path)

    def test_persistence_across_instances(self, tmp_path):
        path = str(tmp_path / "vectors.json")
        store1 = PersistentVectorStore(path=path, auto_save=False)
        store1.add("v1", [1.0, 0.0], {"name": "first"})
        store1.flush()

        store2 = PersistentVectorStore(path=path)
        entry = store2.get("v1")
        assert entry is not None
        assert entry.metadata["name"] == "first"

    def test_load_nonexistent_file(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        store = PersistentVectorStore(path=path)
        assert store.count() == 0

    def test_load_corrupt_file(self, tmp_path):
        path = str(tmp_path / "corrupt.json")
        with open(path, "w") as f:
            f.write("not valid json {{{")
        store = PersistentVectorStore(path=path)
        assert store.count() == 0  # Should gracefully handle


# ---------------------------------------------------------------------------
# CachedVectorStore
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCachedVectorStore:
    def _make_backend(self):
        return InMemoryVectorStore()

    def test_create(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend, cache_size=10)
        assert store._cache_size == 10

    def test_add_and_get(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        store.add("v1", [1.0, 0.0], {"label": "test"})
        entry = store.get("v1")
        assert entry is not None
        assert entry.id == "v1"

    def test_get_from_cache(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        store.add("v1", [1.0, 0.0])
        # First get populates cache
        store.get("v1")
        # Second get should hit cache
        entry = store.get("v1")
        assert entry is not None
        assert entry.id == "v1"

    def test_get_nonexistent(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        assert store.get("nonexistent") is None

    def test_delete(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        store.add("v1", [1.0, 0.0])
        store.get("v1")  # Populate cache
        result = store.delete("v1")
        assert result is True
        assert store.get("v1") is None

    def test_search_delegates_to_backend(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        results = store.search([1.0, 0.0])
        assert len(results) == 2

    def test_count(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        assert store.count() == 2

    def test_clear(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend)
        store.add("v1", [1.0, 0.0])
        store.get("v1")  # Populate cache
        store.clear()
        assert store.count() == 0
        assert len(store._cache) == 0

    def test_cache_eviction(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend, cache_size=2)
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        store.add("v3", [0.5, 0.5])
        store.get("v1")
        store.get("v2")
        store.get("v3")  # Should evict v1
        assert len(store._cache) == 2
        assert "v1" not in store._cache

    def test_cache_stats(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend, cache_size=100)
        store.add("v1", [1.0, 0.0])
        store.get("v1")
        stats = store.cache_stats()
        assert "cache_size" in stats
        assert "max_size" in stats
        assert stats["max_size"] == 100

    def test_cache_update_on_repeated_get(self):
        backend = self._make_backend()
        store = CachedVectorStore(backend=backend, cache_size=3)
        store.add("v1", [1.0, 0.0])
        store.add("v2", [0.0, 1.0])
        store.add("v3", [0.5, 0.5])
        store.get("v1")
        store.get("v2")
        store.get("v3")
        # Access v1 again to move it to end of LRU
        store.get("v1")
        # Now add v4, which should evict v2 (oldest)
        store.add("v4", [0.1, 0.9])
        store.get("v4")
        assert "v1" in store._cache
        assert "v2" not in store._cache
