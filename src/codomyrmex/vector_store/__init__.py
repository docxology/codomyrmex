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

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the vector_store module."""

    def _backends():
        """List available vector store backends."""
        print("Vector Store Backends")
        print(f"  InMemoryVectorStore - In-process memory store")
        print(f"  NamespacedVectorStore - Namespace-partitioned store")
        print(f"  Distance Metrics: {[dm.value for dm in DistanceMetric]}")

    def _stats():
        """Show vector store statistics."""
        store = create_vector_store()
        print("Vector Store Statistics")
        print(f"  Backend: {store.__class__.__name__}")
        print(f"  Distance Metrics: {[dm.value for dm in DistanceMetric]}")
        count = len(store) if hasattr(store, '__len__') else 'N/A'
        print(f"  Stored Vectors: {count}")

    return {
        "backends": _backends,
        "stats": _stats,
    }


__all__ = [
    "SearchResult",
    "VectorEntry",
    "DistanceMetric",
    "normalize_embedding",
    "VectorStore",
    "InMemoryVectorStore",
    "NamespacedVectorStore",
    "create_vector_store",
    "cli_commands",
]
