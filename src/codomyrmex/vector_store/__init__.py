"""
Vector Store Module

Embeddings storage with pluggable backends for similarity search.
"""

__version__ = "0.1.0"

import hashlib
import heapq
import math
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class SearchResult:
    """Result from vector similarity search."""
    id: str
    score: float
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other: "SearchResult") -> bool:
        return self.score < other.score


@dataclass
class VectorEntry:
    """A vector entry in the store."""
    id: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return len(self.embedding)


class DistanceMetric:
    """Distance metrics for similarity computation."""
    
    @staticmethod
    def cosine(vec1: List[float], vec2: List[float]) -> float:
        """Cosine similarity (returns 0-1, higher = more similar)."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(x * x for x in vec1))
        mag2 = math.sqrt(sum(x * x for x in vec2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot / (mag1 * mag2)
    
    @staticmethod
    def euclidean(vec1: List[float], vec2: List[float]) -> float:
        """Euclidean distance (returns 0+, lower = more similar)."""
        if len(vec1) != len(vec2):
            return float('inf')
        
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))
    
    @staticmethod
    def dot_product(vec1: List[float], vec2: List[float]) -> float:
        """Dot product similarity."""
        if len(vec1) != len(vec2):
            return 0.0
        
        return sum(a * b for a, b in zip(vec1, vec2))


class VectorStore(ABC):
    """Abstract base class for vector storage backends."""
    
    @abstractmethod
    def add(
        self,
        id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a vector to the store.
        
        Args:
            id: Unique identifier for the vector
            embedding: The embedding vector
            metadata: Optional metadata dictionary
        """
        pass
    
    @abstractmethod
    def get(self, id: str) -> Optional[VectorEntry]:
        """Get a vector by ID."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a vector by ID."""
        pass
    
    @abstractmethod
    def search(
        self,
        query: List[float],
        k: int = 10,
        filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            query: Query embedding vector
            k: Number of results to return
            filter_fn: Optional filter function for metadata
            
        Returns:
            List of SearchResult ordered by similarity
        """
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
    
    def __init__(
        self,
        distance_metric: str = "cosine",
    ):
        self._vectors: Dict[str, VectorEntry] = {}
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
    
    def add(
        self,
        id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a vector to the store."""
        entry = VectorEntry(
            id=id,
            embedding=embedding,
            metadata=metadata or {},
        )
        with self._lock:
            self._vectors[id] = entry
    
    def add_batch(
        self,
        entries: List[Tuple[str, List[float], Optional[Dict[str, Any]]]],
    ) -> int:
        """Add multiple vectors at once."""
        count = 0
        with self._lock:
            for item in entries:
                id_val = item[0]
                embedding = item[1]
                metadata = item[2] if len(item) > 2 else None
                self._vectors[id_val] = VectorEntry(
                    id=id_val,
                    embedding=embedding,
                    metadata=metadata or {},
                )
                count += 1
        return count
    
    def get(self, id: str) -> Optional[VectorEntry]:
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
        query: List[float],
        k: int = 10,
        filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        results = []
        
        for entry in self._vectors.values():
            # Apply metadata filter
            if filter_fn and not filter_fn(entry.metadata):
                continue
            
            score = self._distance_fn(query, entry.embedding)
            results.append(SearchResult(
                id=entry.id,
                score=score,
                embedding=entry.embedding,
                metadata=entry.metadata,
            ))
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=self._higher_is_better)
        return results[:k]
    
    def count(self) -> int:
        """Get total number of vectors."""
        return len(self._vectors)
    
    def clear(self) -> None:
        """Clear all vectors."""
        with self._lock:
            self._vectors.clear()
    
    def list_ids(self) -> List[str]:
        """List all vector IDs."""
        return list(self._vectors.keys())


class NamespacedVectorStore(VectorStore):
    """Vector store with namespace support."""
    
    def __init__(self, base_store: Optional[VectorStore] = None):
        self._namespaces: Dict[str, VectorStore] = {}
        self._default_store = base_store or InMemoryVectorStore()
        self._current_namespace: Optional[str] = None
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
    
    def add(
        self,
        id: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add to current namespace."""
        self._get_store().add(id, embedding, metadata)
    
    def get(self, id: str) -> Optional[VectorEntry]:
        """Get from current namespace."""
        return self._get_store().get(id)
    
    def delete(self, id: str) -> bool:
        """Delete from current namespace."""
        return self._get_store().delete(id)
    
    def search(
        self,
        query: List[float],
        k: int = 10,
        filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> List[SearchResult]:
        """Search in current namespace."""
        return self._get_store().search(query, k, filter_fn)
    
    def count(self) -> int:
        """Count in current namespace."""
        return self._get_store().count()
    
    def clear(self) -> None:
        """Clear current namespace."""
        self._get_store().clear()
    
    def list_namespaces(self) -> List[str]:
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


# Convenience functions
def create_vector_store(
    backend: str = "memory",
    **kwargs,
) -> VectorStore:
    """
    Create a vector store with the specified backend.
    
    Args:
        backend: Backend type ("memory", "namespaced")
        **kwargs: Backend-specific arguments
        
    Returns:
        VectorStore instance
    """
    if backend == "memory":
        return InMemoryVectorStore(**kwargs)
    elif backend == "namespaced":
        return NamespacedVectorStore(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def normalize_embedding(embedding: List[float]) -> List[float]:
    """Normalize an embedding to unit length."""
    magnitude = math.sqrt(sum(x * x for x in embedding))
    if magnitude == 0:
        return embedding
    return [x / magnitude for x in embedding]


__all__ = [
    # Core classes
    "VectorStore",
    "InMemoryVectorStore",
    "NamespacedVectorStore",
    # Data classes
    "VectorEntry",
    "SearchResult",
    # Utilities
    "DistanceMetric",
    "create_vector_store",
    "normalize_embedding",
]
