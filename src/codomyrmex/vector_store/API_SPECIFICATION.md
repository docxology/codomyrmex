# Vector Store API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `vector_store` module provides embedding storage with pluggable backends for similarity search. Ships with in-memory and namespaced implementations, supporting cosine, euclidean, and dot-product distance metrics.

## Core API

### VectorEntry (dataclass)

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | `str` | Unique vector identifier |
| `embedding` | `list[float]` | The embedding vector |
| `metadata` | `dict[str, Any]` | Arbitrary metadata |
| `created_at` | `datetime` | Creation timestamp |
| `dimension` | `int` | Embedding dimensionality (property) |

### SearchResult (dataclass)

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | `str` | Vector identifier |
| `score` | `float` | Similarity/distance score |
| `embedding` | `list[float]` | The matched embedding |
| `metadata` | `dict[str, Any]` | Associated metadata |

### DistanceMetric (static methods)

```python
from codomyrmex.vector_store import DistanceMetric

DistanceMetric.cosine(vec1, vec2)       # 0-1, higher = more similar
DistanceMetric.euclidean(vec1, vec2)    # 0+, lower = more similar
DistanceMetric.dot_product(vec1, vec2)  # unbounded, higher = more similar
```

### VectorStore (ABC)

All backends implement this interface:

| Method | Signature | Description |
|:-------|:----------|:------------|
| `add` | `(id, embedding, metadata=None) -> None` | Store a vector |
| `get` | `(id) -> VectorEntry \| None` | Retrieve by ID |
| `delete` | `(id) -> bool` | Remove by ID |
| `search` | `(query, k=10, filter_fn=None) -> list[SearchResult]` | Similarity search |
| `count` | `() -> int` | Total stored vectors |
| `clear` | `() -> None` | Remove all vectors |

### InMemoryVectorStore

```python
from codomyrmex.vector_store import InMemoryVectorStore

store = InMemoryVectorStore(distance_metric="cosine")  # or "euclidean", "dot_product"

store.add("doc-1", [0.1, 0.2, 0.3], metadata={"source": "paper"})
store.add_batch([("doc-2", [0.4, 0.5, 0.6], {"source": "web"})])

results = store.search([0.1, 0.2, 0.3], k=5)
results = store.search([0.1, 0.2, 0.3], k=5, filter_fn=lambda m: m.get("source") == "paper")

ids = store.list_ids()  # -> ["doc-1", "doc-2"]
```

### NamespacedVectorStore

Wraps multiple stores behind namespace isolation.

```python
from codomyrmex.vector_store import NamespacedVectorStore

ns_store = NamespacedVectorStore()
ns_store.use_namespace("project-a").add("vec-1", [0.1, 0.2, 0.3])
ns_store.use_namespace("project-b").add("vec-1", [0.4, 0.5, 0.6])

ns_store.list_namespaces()           # -> ["project-a", "project-b"]
ns_store.delete_namespace("project-b")
```

### Factory and Utilities

```python
from codomyrmex.vector_store import create_vector_store, normalize_embedding

store = create_vector_store(backend="memory", distance_metric="cosine")
store = create_vector_store(backend="namespaced")

unit_vec = normalize_embedding([3.0, 4.0])  # -> [0.6, 0.8]
```

`backend` accepts: `"memory"`, `"namespaced"`.

## Error Handling

| Exception | Raised When |
|:----------|:------------|
| `ValueError` | Unknown `distance_metric` or `backend` in factory functions |

Dimension mismatches in distance calculations return `0.0` (cosine/dot) or `inf` (euclidean) without raising.

## Thread Safety

Both `InMemoryVectorStore` and `NamespacedVectorStore` use `threading.Lock` for all mutations. Read operations on immutable snapshots are safe without locking.

## Integration Points

- `search` -- Combine with full-text search for hybrid retrieval
- `llm` -- Use LLM embedding outputs as input vectors
- `cache` -- Cache frequently searched query results

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
