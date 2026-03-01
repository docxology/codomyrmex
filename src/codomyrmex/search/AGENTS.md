# Agent Guidelines - Search

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Module Overview

Full-text search, fuzzy matching, and semantic search capabilities.

## Key Classes

- **SearchIndex** — Full-text search index
- **InMemoryIndex** — Fast in-memory index
- **FuzzyMatcher** — Fuzzy string matching
- **QueryParser** — Parse search queries
- **Tokenizer** — Text tokenization

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `search_documents` | Perform a quick full-text search across a list of text strings with TF-IDF scoring | Safe |
| `search_index_query` | Create a search index from documents, then query it | Safe |
| `search_fuzzy` | Find the best fuzzy match for a query string among candidates using Levenshtein distance | Safe |

## Agent Instructions

1. **Index at startup** — Build index before queries
2. **Use analyzers** — Tokenization affects results
3. **Fuzzy for typos** — Use fuzzy for user input
4. **Filter before search** — Reduce search space
5. **Cache results** — Common queries, cache results

## Common Patterns

```python
from codomyrmex.search import (
    SearchIndex, InMemoryIndex, FuzzyMatcher, create_index, quick_search
)

# Create and populate index
index = create_index()
index.add_document("doc1", {"title": "Python Guide", "content": "..."})
index.add_document("doc2", {"title": "JavaScript Basics", "content": "..."})

# Search
results = index.search("python programming")
for r in results:
    print(f"{r.score:.2f}: {r.document['title']}")

# Fuzzy matching
matcher = FuzzyMatcher()
matches = matcher.match("pythn", ["python", "java", "rust"])
print(matches)  # [("python", 0.83)]

# Quick search utility
results = quick_search("query", corpus)
```

## Testing Patterns

```python
# Verify indexing and search
index = create_index()
index.add_document("d1", {"title": "test", "content": "hello world"})
results = index.search("hello")
assert len(results) > 0
assert results[0].id == "d1"

# Verify fuzzy matching
matcher = FuzzyMatcher()
matches = matcher.match("helo", ["hello", "goodbye"])
assert matches[0][0] == "hello"
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
