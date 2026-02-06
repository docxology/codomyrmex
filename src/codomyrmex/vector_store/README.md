# Vector Store Module

Embeddings storage with pluggable backends for similarity search.

## Features

- **Multiple Distance Metrics**: Cosine similarity, Euclidean distance, dot product
- **Namespace Support**: Organize vectors by namespace
- **Batch Operations**: Efficient bulk insertions
- **Metadata Filtering**: Filter search results by metadata

## Quick Start

```python
from codomyrmex.vector_store import (
    InMemoryVectorStore,
    VectorStore,
    SearchResult,
)

# Create store
store = InMemoryVectorStore(distance_metric="cosine")

# Add vectors
store.add("doc1", [0.1, 0.2, 0.3], metadata={"type": "article"})
store.add("doc2", [0.2, 0.3, 0.4], metadata={"type": "book"})

# Search
results = store.search([0.15, 0.25, 0.35], k=5)
for r in results:
    print(f"{r.id}: {r.score:.3f}")

# Filter by metadata
results = store.search(
    [0.1, 0.2, 0.3],
    k=10,
    filter_fn=lambda m: m.get("type") == "article"
)
```

## Navigation

- [Technical Spec](SPEC.md)
- [Agent Guidelines](AGENTS.md)
- [PAI Context](PAI.md)
