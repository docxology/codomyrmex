# Technical Specification - Vector Store

**Module**: `codomyrmex.vector_store`  
**Version**: v0.1.7  
**Last Updated**: February 2026

## 1. Purpose

Embeddings storage with pluggable backends for similarity search, supporting multiple distance metrics and namespace isolation.

## 2. Architecture

```
vector_store/
├── __init__.py          # Core implementation
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
└── PAI.md               # Personal AI context
```

## 3. Public API

```python
from codomyrmex.vector_store import (
    VectorStore,           # ABC for all backends
    InMemoryVectorStore,   # In-memory implementation
    NamespacedVectorStore, # Namespace-aware wrapper
    VectorEntry,           # Single vector entry
    SearchResult,          # Search result with score
    DistanceMetric,        # Static distance functions
    create_vector_store,   # Factory function
    normalize_embedding,   # Utility
)
```

## 4. Distance Metrics

| Metric | Range | Interpretation |
|--------|-------|----------------|
| `cosine` | 0-1 | Higher = more similar |
| `euclidean` | 0-∞ | Lower = more similar |
| `dot_product` | -∞ to ∞ | Higher = more similar |

## 5. Testing

```bash
pytest tests/unit/test_vector_store.py -v
```

## 6. Future Considerations

- Chroma integration
- Pinecone client
- FAISS backend for large-scale
- Persistent SQLite storage

## Dependencies

See `src/codomyrmex/vector_store/__init__.py` for import dependencies.
