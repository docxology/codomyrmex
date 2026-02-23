# Search - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Search module providing full-text search, fuzzy matching, and semantic search capabilities for document retrieval.

## Functional Requirements

- Full-text indexing and search
- Fuzzy string matching
- Query parsing with operators
- Result ranking and scoring
- Highlight matching terms

## Core Classes

| Class | Description |
|-------|-------------|
| `SearchIndex` | Abstract search index |
| `InMemoryIndex` | In-memory full-text index |
| `FuzzyMatcher` | Fuzzy string matching |
| `QueryParser` | Parse search queries |
| `Tokenizer` | Text tokenization |
| `SearchResult` | Search result with score |

## Key Functions

| Function | Description |
|----------|-------------|
| `create_index()` | Create search index |
| `quick_search(query, corpus)` | Simple search |

## Query Operators

- `AND`, `OR`, `NOT` — Boolean operators
- `"phrase"` — Exact phrase match
- `field:value` — Field-specific search

## Design Principles

1. **Fast Indexing**: Efficient incremental updates
2. **Relevance**: TF-IDF and BM25 ranking
3. **Flexibility**: Custom analyzers and tokenizers
4. **Scalability**: Handle large document sets

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k search -v
```
