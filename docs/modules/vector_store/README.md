# Vector Store Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Embeddings storage with pluggable backends for similarity search.

## Key Features

- **SearchResult** — Result from vector similarity search.
- **VectorEntry** — A vector entry in the store.
- **DistanceMetric** — Distance metrics for similarity computation.
- **VectorStore** — Abstract base class for vector storage backends.
- **InMemoryVectorStore** — In-memory vector store implementation.
- **NamespacedVectorStore** — Vector store with namespace support.
- `create_vector_store()` — Create a vector store with the specified backend.
- `normalize_embedding()` — Normalize an embedding to unit length.
- `dimension()` — Get embedding dimension.
- `cosine()` — Cosine similarity (returns 0-1, higher = more similar).

## Quick Start

```python
from codomyrmex.vector_store import SearchResult, VectorEntry, DistanceMetric

# Initialize
instance = SearchResult()
```


## Installation

```bash
pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `SearchResult` | Result from vector similarity search. |
| `VectorEntry` | A vector entry in the store. |
| `DistanceMetric` | Distance metrics for similarity computation. |
| `VectorStore` | Abstract base class for vector storage backends. |
| `InMemoryVectorStore` | In-memory vector store implementation. |
| `NamespacedVectorStore` | Vector store with namespace support. |

### Functions

| Function | Description |
|----------|-------------|
| `create_vector_store()` | Create a vector store with the specified backend. |
| `normalize_embedding()` | Normalize an embedding to unit length. |
| `dimension()` | Get embedding dimension. |
| `cosine()` | Cosine similarity (returns 0-1, higher = more similar). |
| `euclidean()` | Euclidean distance (returns 0+, lower = more similar). |
| `dot_product()` | Dot product similarity. |
| `add()` | Add a vector to the store. |
| `get()` | Get a vector by ID. |
| `delete()` | Delete a vector by ID. |
| `search()` | Search for similar vectors. |
| `count()` | Get total number of vectors. |
| `clear()` | Clear all vectors. |
| `add_batch()` | Add multiple vectors at once. |
| `list_ids()` | List all vector IDs. |
| `use_namespace()` | Set the current namespace. |
| `list_namespaces()` | List all namespaces. |
| `delete_namespace()` | Delete an entire namespace. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k vector_store -v
```

## Navigation

- **Source**: [src/codomyrmex/vector_store/](../../../src/codomyrmex/vector_store/)
- **Parent**: [Modules](../README.md)
