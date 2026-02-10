"""
Vector Store Module

Vector similarity search with in-memory and namespaced backends.
"""

from .models import (
    DistanceMetric,
    SearchResult,
    VectorEntry,
    normalize_embedding,
)
from .store import (
    InMemoryVectorStore,
    NamespacedVectorStore,
    VectorStore,
    create_vector_store,
)

__all__ = [
    "SearchResult",
    "VectorEntry",
    "DistanceMetric",
    "normalize_embedding",
    "VectorStore",
    "InMemoryVectorStore",
    "NamespacedVectorStore",
    "create_vector_store",
]
