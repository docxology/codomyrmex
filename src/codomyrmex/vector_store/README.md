# Vector Store Module

**Version**: v0.1.0 | **Status**: Active

Embeddings storage with similarity search using cosine, euclidean, or dot product metrics.

## Installation

```bash
uv pip install codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`SearchResult`** — Result from vector similarity search.
- **`VectorEntry`** — A vector entry in the store.
- **`DistanceMetric`** — Distance metrics for similarity computation.
- **`VectorStore`** — Abstract base class for vector storage backends.
- **`InMemoryVectorStore`** — In-memory vector store implementation.
- **`NamespacedVectorStore`** — Vector store with namespace support.

### Functions

- **`create_vector_store()`** — Create a vector store with the specified backend.
- **`normalize_embedding()`** — Normalize an embedding to unit length.

## Quick Start

```python
from codomyrmex.vector_store import (
    InMemoryVectorStore, NamespacedVectorStore, DistanceMetric, normalize_embedding
)

# Create store with cosine similarity
store = InMemoryVectorStore(distance_metric="cosine")

# Add vectors with metadata
store.add("doc-1", [0.1, 0.2, 0.3], {"title": "Python Guide"})
store.add("doc-2", [0.2, 0.3, 0.4], {"title": "ML Tutorial"})
store.add("doc-3", [0.9, 0.1, 0.1], {"title": "Rust Manual"})

# Similarity search
query = [0.15, 0.25, 0.35]
results = store.search(query, k=2)

for r in results:
    print(f"{r.id}: score={r.score:.3f}, title={r.metadata['title']}")

# Filter by metadata
results = store.search(
    query,
    k=5,
    filter_fn=lambda m: "Python" in m.get("title", "")
)
```

## Namespaced Storage

```python
store = NamespacedVectorStore()

# Separate vector spaces
store.use_namespace("users").add("u1", user_embedding)
store.use_namespace("products").add("p1", product_embedding)

# Search within namespace
store.use_namespace("users")
results = store.search(query_embedding, k=10)

print(store.list_namespaces())  # ['users', 'products']
```

## Directory Structure

- `models.py` — Data models (VectorEntry, SearchResult, DistanceMetric)
- `store.py` — Store implementations (VectorStore, InMemoryVectorStore)
- `__init__.py` — Public API re-exports

## Exports

| Class | Description |
| :--- | :--- |
| `InMemoryVectorStore` | In-memory store with configurable distance |
| `NamespacedVectorStore` | Multi-namespace vector storage |
| `VectorEntry` | Vector with id, embedding, metadata |
| `SearchResult` | Result with id, score, metadata |
| `DistanceMetric` | Static methods: cosine, euclidean, dot_product |
| `create_vector_store(backend)` | Factory function |
| `normalize_embedding(vec)` | Normalize to unit length |

## Distance Metrics

| Metric | Higher = Better? | Use Case |
| :--- | :--- | :--- |
| cosine | Yes | Semantic similarity |
| euclidean | No (lower) | Spatial distance |
| dot_product | Yes | Magnitude-aware similarity |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k vector_store -v
```

## Documentation

- [Module Documentation](../../../docs/modules/vector_store/README.md)
- [Agent Guide](../../../docs/modules/vector_store/AGENTS.md)
- [Specification](../../../docs/modules/vector_store/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
