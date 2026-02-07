# Search — Functional Specification

**Module**: `codomyrmex.search`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Full-text search, semantic search, and indexing utilities.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `Document` | Class | A searchable document. |
| `SearchResult` | Class | A search result. |
| `Tokenizer` | Class | Abstract tokenizer. |
| `SimpleTokenizer` | Class | Simple whitespace and punctuation tokenizer. |
| `SearchIndex` | Class | Abstract search index. |
| `InMemoryIndex` | Class | In-memory inverted index with TF-IDF scoring. |
| `FuzzyMatcher` | Class | Fuzzy string matching utilities. |
| `QueryParser` | Class | Parse search queries with operators. |
| `create_index()` | Function | Create a search index. |
| `quick_search()` | Function | Quick search over a list of strings. |
| `tokenize()` | Function | tokenize |
| `tokenize()` | Function | tokenize |
| `index()` | Function | Index a document. |

### Source Files

- `semantic.py`

## 3. Dependencies

See `src/codomyrmex/search/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.search import Document, SearchResult, Tokenizer, SimpleTokenizer, SearchIndex
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k search -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/search/)
