# Personal AI Infrastructure — Vector Store Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Vector Store module provides PAI integration for embedding storage and similarity search.

## PAI Capabilities

### Embedding Storage

Store and retrieve embeddings:

```python
from codomyrmex.vector_store import VectorStore

store = VectorStore()
store.add(id="doc_1", embedding=embedding_vector, metadata={"title": "Doc 1"})

results = store.search(query_embedding, limit=5)
```

### Namespace Management

Organize embeddings:

```python
from codomyrmex.vector_store import VectorStore

store = VectorStore(namespace="code_snippets")
store.add(id="func_1", embedding=code_embedding)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `VectorStore` | Store embeddings |
| `search` | Similarity search |
| `Namespace` | Organize data |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
