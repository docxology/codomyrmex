# Personal AI Infrastructure — Search Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Search module provides PAI integration for codebase search and retrieval, enabling AI agents to find relevant code and documentation.

## PAI Capabilities

### Codebase Search

Enable AI agents to search code:

```python
from codomyrmex.search import SearchIndex, FuzzyMatcher

# Create index
index = SearchIndex()
index.add_documents(code_files)

# Search for relevant code
results = index.search(
    "authentication middleware",
    limit=10
)

for result in results:
    print(f"{result.file}:{result.line} (score: {result.score:.2f})")
```

### Semantic Search

Combine with embeddings for semantic search:

```python
from codomyrmex.search import SemanticSearcher
from codomyrmex.vector_store import VectorStore

# Semantic search
searcher = SemanticSearcher(
    vector_store=VectorStore(),
    embedding_model="code-bert"
)

# Find semantically similar code
similar = searcher.find_similar(
    "function that validates email addresses"
)
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `SearchIndex` | Fast text search |
| `FuzzyMatcher` | Fuzzy matching |
| `SemanticSearcher` | AI-powered search |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
