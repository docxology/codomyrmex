# Agent Guidelines - Vector Store

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Embeddings storage for similarity search and RAG pipelines.

## Key Classes

- **VectorStore** — Abstract base class
- **InMemoryVectorStore** — Fast in-memory storage
- **NamespacedVectorStore** — Multi-tenant isolation

## Agent Instructions

1. **Normalize embeddings** — Use `normalize_embedding()` for consistent cosine similarity
2. **Use namespaces** — Isolate different embedding models or datasets
3. **Batch inserts** — Use `add_batch()` for large datasets
4. **Filter first** — Use metadata filters to reduce search space
5. **Choose distance metric** — Cosine for normalized, euclidean for raw

## Common Patterns

```python
from codomyrmex.vector_store import InMemoryVectorStore, normalize_embedding

store = InMemoryVectorStore(dimension=384)

# Add normalized embeddings
embedding = normalize_embedding(raw_embedding)
store.add("doc_1", embedding, metadata={"source": "wiki"})

# Search with filters
results = store.search(
    query_embedding,
    k=10,
    filter={"source": "wiki"}
)

# Namespaced storage for multi-tenant
from codomyrmex.vector_store import NamespacedVectorStore
ns_store = NamespacedVectorStore()
ns_store.add("doc_1", embedding, namespace="user_123")
```

## Testing Patterns

```python
# Verify storage and retrieval
store = InMemoryVectorStore(dimension=3)
store.add("a", [1.0, 0.0, 0.0])
store.add("b", [0.0, 1.0, 0.0])

results = store.search([1.0, 0.0, 0.0], k=1)
assert results[0].id == "a"

# Verify namespace isolation
ns_store = NamespacedVectorStore()
ns_store.add("a", [1, 0, 0], namespace="n1")
ns_store.add("a", [0, 1, 0], namespace="n2")
assert ns_store.count("n1") == 1
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
