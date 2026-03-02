# documents/search — Technical Specification

## Overview

Implements document search via an in-memory inverted index with term-frequency scoring, plus a fluent query builder for constructing structured queries.

## Architecture

Three modules with distinct responsibilities: `indexer.py` (storage and retrieval), `query_builder.py` (query construction), `searcher.py` (scoring and ranking).

## Key Classes and Functions

### InMemoryIndex (indexer.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `add` | `(doc_id: str, content: str, document: Document \| None = None)` | None |
| `remove` | `(doc_id: str)` | `bool` |
| `search` | `(query: str)` | `list[str]` (doc IDs, AND semantics) |
| `get_document` | `(doc_id: str)` | `Document \| None` |
| `save` | `(path: str)` | None (JSON persistence) |
| `load` | `(path: str)` | None (JSON restore) |
| `document_count` | property | `int` |

Internal structure: `_index: dict[str, set[str]]` (term to doc_id sets), `_documents: dict[str, Document]`.

### QueryBuilder (query_builder.py)

| Method | Signature | Returns |
|--------|-----------|---------|
| `add_term` | `(term: str)` | `QueryBuilder` (fluent) |
| `add_filter` | `(field: str, value: str)` | `QueryBuilder` (fluent) |
| `set_sort` | `(field: str)` | `QueryBuilder` (fluent) |
| `build` | `()` | `str` (space-joined terms) |
| `to_dict` | `()` | `dict` (serialized state) |

State: `terms: list[str]`, `filters: dict`, `sort_by: str | None`.

### Searcher Functions (searcher.py)

| Function | Signature | Returns |
|----------|-----------|---------|
| `search_documents` | `(documents: list[Document], query: str)` | `list[Document]` |
| `search_index` | `(index: InMemoryIndex, query: str)` | `list[tuple[str, float]]` |

`search_index` uses `collections.Counter` for term-frequency scoring. Results are sorted descending by score.

## Dependencies

- `collections.Counter` for TF scoring
- `json` for index persistence
- `documents.models.Document` for document references

## Constraints

- AND-only query semantics (all terms must match).
- In-memory storage; index size bounded by available RAM.
- No stemming or stop-word filtering; tokenization is lowercase whitespace split.
