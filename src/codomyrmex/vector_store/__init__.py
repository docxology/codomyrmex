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
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    pass

try:
    from .chroma import ChromaVectorStore
except ImportError:
    ChromaVectorStore = None  # type: ignore


def cli_commands():
    """Return CLI commands for the vector_store module."""

    def _backends():
        """List available vector store backends."""
        print("Vector Store Backends")
        print("  InMemoryVectorStore - In-process memory store")
        print("  NamespacedVectorStore - Namespace-partitioned store")
        print(f"  Distance Metrics: {[dm.value for dm in DistanceMetric]}")  # type: ignore

    def _stats():
        """Show vector store statistics."""
        store = create_vector_store()
        print("Vector Store Statistics")
        print(f"  Backend: {store.__class__.__name__}")
        print(f"  Distance Metrics: {[dm.value for dm in DistanceMetric]}")  # type: ignore
        count = len(store) if hasattr(store, "__len__") else "N/A"
        print(f"  Stored Vectors: {count}")

    return {
        "backends": _backends,
        "stats": _stats,
    }


__all__ = [
    "ChromaVectorStore",
    "DistanceMetric",
    "InMemoryVectorStore",
    "NamespacedVectorStore",
    "SearchResult",
    "VectorEntry",
    "VectorStore",
    "cli_commands",
    "create_vector_store",
    "normalize_embedding",
]
