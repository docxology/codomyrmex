# Personal AI Infrastructure — Vector Store Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Vector Store module provides embedding-based vector storage and similarity search for AI agent memory and retrieval. It supports multiple backends and enables semantic search over code, documents, and knowledge artifacts.

## PAI Capabilities

### Vector Operations

```python
from codomyrmex.vector_store import SearchResult, create_vector_store

store = create_vector_store(backend="memory")  # or "namespaced", "chroma" (needs chromadb)

# Store embeddings (produced by your embedding model) with metadata
store.add("auth-endpoint", embedding=[0.12, 0.85, 0.31], metadata={"module": "auth"})

# Similarity search with a query embedding
results: list[SearchResult] = store.search([0.10, 0.80, 0.35], k=5)
for r in results:
    print(r.id, r.score, r.metadata)
```

### Data Models

```python
from codomyrmex.vector_store.models import (
    DistanceMetric,
    SearchResult,
    VectorEntry,
    batch_cosine_similarity,
    normalize_embedding,
)
```

## Key Exports

| Export | Type | Purpose |
| --- | --- | --- |
| `VectorStore` | Class | Abstract vector storage and retrieval interface (`add`, `search`, `get`, `delete`) |
| `InMemoryVectorStore` / `NamespacedVectorStore` / `ChromaVectorStore` | Class | Backends returned by `create_vector_store()` |
| `create_vector_store()` | Function | Backend factory (`memory`, `namespaced`, `chroma`) |
| `VectorEntry` | Model | Stored embedding with id, metadata and timestamps |
| `SearchResult` | Model | Similarity search result (id, score, embedding, metadata) |
| `DistanceMetric` | Class | Static `cosine`, `euclidean` and `dot_product` functions |
| `normalize_embedding()` | Function | L2-normalise an embedding |
| `cli_commands` | Function | CLI commands for vector operations |

## PAI Algorithm Phase Mapping

| Phase | Vector Store Contribution |
| --- | --- |
| **OBSERVE** | Semantic search for relevant code/docs using vector similarity |
| **THINK** | Retrieve contextually similar past experiences for reasoning |
| **LEARN** | Store embeddings of work outcomes for future retrieval |

## Architecture Role

**Core Layer** — Central embedding infrastructure. Consumed by `graph_rag/` (hybrid search), `agentic_memory/` (semantic memory), `search/` (augmented search), and `cerebrum/` (similarity-based reasoning).

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
