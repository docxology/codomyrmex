"""
Vector Store Backends

Storage backends for vector similarity search.
"""

import threading
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from .models import DistanceMetric, SearchResult, VectorEntry


class VectorStore(ABC):
    """Abstract base class for vector storage backends."""

    @abstractmethod
    def add(self, id: str, embedding: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Add a vector to the store."""
        pass

    @abstractmethod
    def get(self, id: str) -> VectorEntry | None:
        """Get a vector by ID."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a vector by ID."""
        pass

    @abstractmethod
    def search(
        self,
        query: list[float],
        k: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get total number of vectors."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all vectors."""
        pass


class InMemoryVectorStore(VectorStore):
    """In-memory vector store implementation."""

    def __init__(self, distance_metric: str = "cosine"):
        self._vectors: dict[str, VectorEntry] = {}
        self._lock = threading.Lock()

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

    def add(self, id: str, embedding: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Add a vector to the store."""
        entry = VectorEntry(id=id, embedding=embedding, metadata=metadata or {})
        with self._lock:
            self._vectors[id] = entry

    def add_batch(self, entries: list[tuple[str, list[float], dict[str, Any] | None]]) -> int:
        """Add multiple vectors at once."""
        count = 0
        with self._lock:
            for item in entries:
                id_val = item[0]
                embedding = item[1]
                metadata = item[2] if len(item) > 2 else None
                self._vectors[id_val] = VectorEntry(
                    id=id_val, embedding=embedding, metadata=metadata or {},
                )
                count += 1
        return count

    def get(self, id: str) -> VectorEntry | None:
        """Get a vector by ID."""
        return self._vectors.get(id)

    def delete(self, id: str) -> bool:
        """Delete a vector by ID."""
        with self._lock:
            if id in self._vectors:
                del self._vectors[id]
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
                id=entry.id, score=score, embedding=entry.embedding, metadata=entry.metadata,
            ))
        results.sort(key=lambda x: x.score, reverse=self._higher_is_better)
        return results[:k]

    def count(self) -> int:
        """Get total number of vectors."""
        return len(self._vectors)

    def clear(self) -> None:
        """Clear all vectors."""
        with self._lock:
            self._vectors.clear()

    def list_ids(self) -> list[str]:
        """List all vector IDs."""
        return list(self._vectors.keys())


class NamespacedVectorStore(VectorStore):
    """Vector store with namespace support."""

    def __init__(self, base_store: VectorStore | None = None):
        self._namespaces: dict[str, VectorStore] = {}
        self._default_store = base_store or InMemoryVectorStore()
        self._current_namespace: str | None = None
        self._lock = threading.Lock()

    def use_namespace(self, namespace: str) -> "NamespacedVectorStore":
        """Set the current namespace."""
        with self._lock:
            if namespace not in self._namespaces:
                self._namespaces[namespace] = InMemoryVectorStore()
        self._current_namespace = namespace
        return self

    def _get_store(self) -> VectorStore:
        """Get the current namespace's store."""
        if self._current_namespace:
            return self._namespaces[self._current_namespace]
        return self._default_store

    def add(self, id: str, embedding: list[float], metadata: dict[str, Any] | None = None) -> None:
        """Add to current namespace."""
        self._get_store().add(id, embedding, metadata)

    def get(self, id: str) -> VectorEntry | None:
        """Get from current namespace."""
        return self._get_store().get(id)

    def delete(self, id: str) -> bool:
        """Delete from current namespace."""
        return self._get_store().delete(id)

    def search(
        self,
        query: list[float],
        k: int = 10,
        filter_fn: Callable[[dict[str, Any]], bool] | None = None,
    ) -> list[SearchResult]:
        """Search in current namespace."""
        return self._get_store().search(query, k, filter_fn)

    def count(self) -> int:
        """Count in current namespace."""
        return self._get_store().count()

    def clear(self) -> None:
        """Clear current namespace."""
        self._get_store().clear()

    def list_namespaces(self) -> list[str]:
        """List all namespaces."""
        return list(self._namespaces.keys())

    def delete_namespace(self, namespace: str) -> bool:
        """Delete an entire namespace."""
        with self._lock:
            if namespace in self._namespaces:
                del self._namespaces[namespace]
                if self._current_namespace == namespace:
                    self._current_namespace = None
                return True
        return False


def create_vector_store(backend: str = "memory", **kwargs) -> VectorStore:
    """Create a vector store with the specified backend."""
    if backend == "memory":
        return InMemoryVectorStore(**kwargs)
    elif backend == "namespaced":
        return NamespacedVectorStore(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")
