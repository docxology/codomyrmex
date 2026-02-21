# Search Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Full-text search, semantic search, and indexing utilities.

## Key Features

- **Document** — A searchable document.
- **SearchResult** — A search result.
- **Tokenizer** — Abstract tokenizer.
- **SimpleTokenizer** — Simple whitespace and punctuation tokenizer.
- **SearchIndex** — Abstract search index.
- **InMemoryIndex** — In-memory inverted index with TF-IDF scoring.
- `create_index()` — Create a search index.
- `quick_search()` — Quick search over a list of strings.
- `tokenize()` — tokenize
- `tokenize()` — tokenize

## Quick Start

```python
from codomyrmex.search import Document, SearchResult, Tokenizer

# Initialize
instance = Document()
```


## Installation

```bash
uv pip install codomyrmex
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Document` | A searchable document. |
| `SearchResult` | A search result. |
| `Tokenizer` | Abstract tokenizer. |
| `SimpleTokenizer` | Simple whitespace and punctuation tokenizer. |
| `SearchIndex` | Abstract search index. |
| `InMemoryIndex` | In-memory inverted index with TF-IDF scoring. |
| `FuzzyMatcher` | Fuzzy string matching utilities. |
| `QueryParser` | Parse search queries with operators. |

### Functions

| Function | Description |
|----------|-------------|
| `create_index()` | Create a search index. |
| `quick_search()` | Quick search over a list of strings. |
| `tokenize()` | tokenize |
| `index()` | Index a document. |
| `search()` | Search for documents. |
| `delete()` | Delete a document. |
| `count()` | Get document count. |
| `get()` | Get document by ID. |
| `levenshtein_distance()` | Compute Levenshtein edit distance. |
| `similarity_ratio()` | Get similarity ratio (0-1). |
| `find_best_match()` | Find best matching string. |
| `parse()` | Parse query into structured format. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k search -v
```

## Navigation

- **Source**: [src/codomyrmex/search/](../../../src/codomyrmex/search/)
- **Parent**: [Modules](../README.md)
