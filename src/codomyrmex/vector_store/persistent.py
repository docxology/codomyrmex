"""
Persistent Vector Store

File-backed vector storage for persistence across restarts.
"""

import json
import logging
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from . import (
    DistanceMetric,
    SearchResult,
    VectorEntry,
    VectorStore,
)


class PersistentVectorStore(VectorStore):
    """Vector store with file persistence."""

    def __init__(
        self,
        path: str,
        distance_metric: str = "cosine",
        auto_save: bool = True,
        save_interval: int = 100,  # Save every N operations
    ):
        """Initialize this instance."""
        self._path = Path(path)
        self._auto_save = auto_save
        self._save_interval = save_interval
        self._operation_count = 0
        self._lock = threading.Lock()

        # Set up distance function
        if distance_metric == "cosine":
            self._distance_fn = DistanceMetric.cosine
            self._higher_is_better = True
        elif distance_metric == "euclidean":
            self._distance_fn = DistanceMetric.euclidean
            self._higher_is_better = False
        elif distance_metric == "dot_product":
            self._distance_fn = DistanceMetric.dot_product
            self._higher_is_better = True
        else:
            raise ValueError(f"Unknown distance metric: {distance_metric}")

        self._distance_metric = distance_metric
        self._vectors: dict[str, VectorEntry] = {}

        # Load existing data
        self._load()

    def _load(self) -> None:
        """Load vectors from file."""
        if self._path.exists():
            try:
                with open(self._path) as f:
                    data = json.load(f)

                for item in data.get("vectors", []):
                    entry = VectorEntry(
                        id=item["id"],
                        embedding=item["embedding"],
                        metadata=item.get("metadata", {}),
                    )
                    self._vectors[entry.id] = entry
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to load vector store from %s: %s", self._path, e)
                pass

    def _save(self) -> None:
        """Save vectors to file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "distance_metric": self._distance_metric,
            "vectors": [
                {
                    "id": e.id,
                    "embedding": e.embedding,
                    "metadata": e.metadata,
                }
                for e in self._vectors.values()
            ],
        }

        with open(self._path, 'w') as f:
            json.dump(data, f)

    def _maybe_save(self) -> None:
        """Save if auto-save is enabled and interval reached."""
        if self._auto_save:
            self._operation_count += 1
            if self._operation_count >= self._save_interval:
                self._save()
                self._operation_count = 0

    def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a vector."""
        with self._lock:
            self._vectors[id] = VectorEntry(
                id=id,
                embedding=embedding,
                metadata=metadata or {},
            )
            self._maybe_save()

    def get(self, id: str) -> VectorEntry | None:
        """Get a vector by ID."""
        return self._vectors.get(id)

    def delete(self, id: str) -> bool:
        """Delete a vector."""
        with self._lock:
            if id in self._vectors:
                del self._vectors[id]
                self._maybe_save()
                return True
        return False

    def search(
        self,
        query: list[float],
        k: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        results = []

        for entry in self._vectors.values():
            if filter_fn and not filter_fn(entry.metadata):
                continue

            score = self._distance_fn(query, entry.embedding)
            results.append(SearchResult(
                id=entry.id,
                score=score,
                embedding=entry.embedding,
                metadata=entry.metadata,
            ))

        results.sort(key=lambda x: x.score, reverse=self._higher_is_better)
        return results[:k]

    def count(self) -> int:
        """Get vector count."""
        return len(self._vectors)

    def clear(self) -> None:
        """Clear all vectors."""
        with self._lock:
            self._vectors.clear()
            if self._auto_save:
                self._save()

    def flush(self) -> None:
        """Force save to disk."""
        with self._lock:
            self._save()

    def compact(self) -> None:
        """Compact storage (re-save to remove any fragmentation)."""
        self.flush()


class CachedVectorStore(VectorStore):
    """Vector store with LRU caching for frequently accessed vectors."""

    def __init__(
        self,
        backend: VectorStore,
        cache_size: int = 1000,
    ):
        """Initialize this instance."""
        self._backend = backend
        self._cache_size = cache_size
        self._cache: dict[str, VectorEntry] = {}
        self._access_order: list[str] = []
        self._lock = threading.Lock()

    def _update_cache(self, entry: VectorEntry) -> None:
        """Update cache with LRU eviction."""
        if entry.id in self._cache:
            self._access_order.remove(entry.id)
        elif len(self._cache) >= self._cache_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]

        self._cache[entry.id] = entry
        self._access_order.append(entry.id)

    def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a vector."""
        self._backend.add(id, embedding, metadata)
        entry = VectorEntry(id=id, embedding=embedding, metadata=metadata or {})
        with self._lock:
            self._update_cache(entry)

    def get(self, id: str) -> VectorEntry | None:
        """Get with cache."""
        with self._lock:
            if id in self._cache:
                self._access_order.remove(id)
                self._access_order.append(id)
                return self._cache[id]

        entry = self._backend.get(id)
        if entry:
            with self._lock:
                self._update_cache(entry)
        return entry

    def delete(self, id: str) -> bool:
        """Delete from backend and cache."""
        with self._lock:
            if id in self._cache:
                del self._cache[id]
                self._access_order.remove(id)
        return self._backend.delete(id)

    def search(
        self,
        query: list[float],
        k: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[SearchResult]:
        """Search (not cached)."""
        return self._backend.search(query, k, filter_fn)

    def count(self) -> int:
        """count ."""
        return self._backend.count()

    def clear(self) -> None:
        """clear ."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
        self._backend.clear()

    def cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "max_size": self._cache_size,
            "hit_rate": 0.0,  # Would track hits/misses
        }
