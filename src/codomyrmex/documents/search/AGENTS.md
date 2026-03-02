# documents/search — Agent Coordination

## Purpose

Provides full-text search over document collections using an in-memory inverted index with TF-based scoring. Agents use this subpackage to index, query, and rank documents.

## Key Components

| Component | Role |
|-----------|------|
| `InMemoryIndex` | Inverted index mapping terms to document ID sets; supports add, remove, search (AND intersection), JSON persistence |
| `QueryBuilder` | Fluent API for constructing search queries with terms, filters, and sort fields |
| `search_documents()` | Searches a list of `Document` objects by matching content against query terms |
| `search_index()` | Searches an `InMemoryIndex` and returns scored results using term-frequency ranking |
| `build_query()` | Convenience function wrapping `QueryBuilder` for one-shot query construction |
| `index_document()` | Convenience function to add a document to an index |
| `create_index()` | Convenience function to create a new `InMemoryIndex` |

## Operating Contracts

- `InMemoryIndex.add(doc_id, content, document)` tokenizes content (lowercase split), builds inverted index entries, and stores the document reference.
- `InMemoryIndex.search(query)` tokenizes the query and returns document IDs where ALL terms appear (AND semantics).
- `InMemoryIndex.save(path)` / `load(path)` persist/restore the index and document store as JSON.
- `search_index(index, query)` returns `list[tuple[str, float]]` where float is a TF score computed via `collections.Counter`.
- `QueryBuilder` supports method chaining: `builder.add_term("x").add_filter("type", "md").build()` returns a space-joined query string.

## Integration Points

- **Models**: Indexes and returns `Document` objects from `documents.models`.
- **Core**: Documents produced by `DocumentReader` or `DocumentParser` feed into the index.
- **Logging**: Uses `codomyrmex.logging_monitoring.get_logger`.

## Navigation

- **Parent**: [documents README](../README.md)
- **Siblings**: [core](../core/AGENTS.md) | [models](../models/AGENTS.md)
- **Spec**: [SPEC.md](SPEC.md)
