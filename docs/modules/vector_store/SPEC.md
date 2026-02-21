# Vector Store — Functional Specification

**Module**: `codomyrmex.vector_store`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Embeddings storage with pluggable backends for similarity search.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `SearchResult` | Class | Result from vector similarity search. |
| `VectorEntry` | Class | A vector entry in the store. |
| `DistanceMetric` | Class | Distance metrics for similarity computation. |
| `VectorStore` | Class | Abstract base class for vector storage backends. |
| `InMemoryVectorStore` | Class | In-memory vector store implementation. |
| `NamespacedVectorStore` | Class | Vector store with namespace support. |
| `create_vector_store()` | Function | Create a vector store with the specified backend. |
| `normalize_embedding()` | Function | Normalize an embedding to unit length. |
| `dimension()` | Function | Get embedding dimension. |
| `cosine()` | Function | Cosine similarity (returns 0-1, higher = more similar). |
| `euclidean()` | Function | Euclidean distance (returns 0+, lower = more similar). |

### Source Files

- `persistent.py`

## 3. Dependencies

See `src/codomyrmex/vector_store/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.vector_store import SearchResult, VectorEntry, DistanceMetric, VectorStore, InMemoryVectorStore
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k vector_store -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/vector_store/)
