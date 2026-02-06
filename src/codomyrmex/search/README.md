# Search Module

Full-text search, semantic search, and indexing.

## Quick Start

```python
from codomyrmex.search import InMemoryIndex, Document

index = InMemoryIndex()
index.index(Document("1", "Python programming guide"))
index.index(Document("2", "JavaScript tutorial"))

results = index.search("python", k=5)
for r in results:
    print(f"{r.document.id}: {r.score:.2f}")
```

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
