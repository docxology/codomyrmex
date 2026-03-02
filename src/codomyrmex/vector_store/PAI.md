# Personal AI Infrastructure — Vector Store Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Vector Store module provides embedding-based vector storage and similarity search for AI agent memory and retrieval. It supports multiple backends and enables semantic search over code, documents, and knowledge artifacts.

## PAI Capabilities

### Vector Operations

```python
from codomyrmex.vector_store import VectorStore, VectorDocument, SearchResult

store = VectorStore(backend="local")

# Store documents as vectors
doc = VectorDocument(content="Authentication endpoint using JWT", metadata={"module": "auth"})
store.upsert(doc)

# Semantic search
results: list[SearchResult] = store.search("login API", top_k=5)
```

### Data Models

```python
from codomyrmex.vector_store.models import Embedding, VectorIndex, SimilarityMetric
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `VectorStore` | Class | Vector storage and retrieval engine |
| `VectorDocument` | Model | Document with embedding metadata |
| `SearchResult` | Model | Similarity search result |
| `Embedding` | Model | Vector embedding data model |
| `VectorIndex` | Model | Index configuration |
| `SimilarityMetric` | Enum | Cosine, euclidean, dot product |
| `cli_commands` | Function | CLI commands for vector operations |

## PAI Algorithm Phase Mapping

| Phase | Vector Store Contribution |
|-------|---------------------------|
| **OBSERVE** | Semantic search for relevant code/docs using vector similarity |
| **THINK** | Retrieve contextually similar past experiences for reasoning |
| **LEARN** | Store embeddings of work outcomes for future retrieval |

## Architecture Role

**Core Layer** — Central embedding infrastructure. Consumed by `graph_rag/` (hybrid search), `agentic_memory/` (semantic memory), `search/` (augmented search), and `cerebrum/` (similarity-based reasoning).

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.vector_store import ...`
- CLI: `codomyrmex vector_store <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
