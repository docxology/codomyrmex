# Search API Specification

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `search` module provides full-text search with TF-IDF scoring, fuzzy string matching, and structured query parsing. Ships with an in-memory inverted index, a configurable tokenizer, and convenience functions for quick one-off searches.

## Core API

### Document (dataclass)

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | `str` | Unique document identifier |
| `content` | `str` | Searchable text content |
| `metadata` | `dict[str, Any]` | Arbitrary metadata |
| `indexed_at` | `datetime` | Indexing timestamp |

### SearchResult (dataclass)

| Field | Type | Description |
|:------|:-----|:------------|
| `document` | `Document` | The matched document |
| `score` | `float` | TF-IDF relevance score |
| `highlights` | `list[str]` | Context snippets around matches (max 3) |

### Tokenizer

```python
from codomyrmex.search import SimpleTokenizer

tokenizer = SimpleTokenizer(lowercase=True, min_length=2)
tokens = tokenizer.tokenize("Hello World!")  # -> ["hello", "world"]
```

Custom tokenizers extend `Tokenizer(ABC)` and implement `tokenize(text) -> list[str]`.

### SearchIndex (ABC)

All index backends implement this interface:

| Method | Signature | Description |
|:-------|:----------|:------------|
| `index` | `(document: Document) -> None` | Add or update a document |
| `search` | `(query: str, k: int = 10) -> list[SearchResult]` | Search with TF-IDF scoring |
| `delete` | `(doc_id: str) -> bool` | Remove a document |
| `count` | `() -> int` | Total indexed documents |

### InMemoryIndex

TF-IDF inverted index with automatic highlight generation.

```python
from codomyrmex.search import InMemoryIndex, Document

index = InMemoryIndex(tokenizer=SimpleTokenizer(min_length=3))

index.index(Document(id="1", content="Rate limiting protects APIs from abuse"))
index.index(Document(id="2", content="Token buckets control burst traffic"))

results = index.search("rate limiting", k=5)
# results[0].score -> TF-IDF score
# results[0].highlights -> ["...Rate limiting protects APIs..."]

doc = index.get("1")  # -> Document or None
index.delete("1")     # -> True
```

### FuzzyMatcher (static methods)

```python
from codomyrmex.search import FuzzyMatcher

FuzzyMatcher.levenshtein_distance("kitten", "sitting")    # -> 3
FuzzyMatcher.similarity_ratio("python", "pyhton")         # -> 0.833...
FuzzyMatcher.find_best_match("pythn", ["python", "java", "rust"], threshold=0.6)  # -> "python"
```

### QueryParser

Parses search queries with `+` (must include), `-` (must exclude), and `"..."` (exact phrase) operators.

```python
from codomyrmex.search import QueryParser

parser = QueryParser()
parsed = parser.parse('+python -java "machine learning"')
# -> {
#     "terms": [],
#     "must": ["python"],
#     "must_not": ["java"],
#     "phrases": ["machine learning"]
# }
```

### Factory and Convenience Functions

```python
from codomyrmex.search import create_index, quick_search

# Factory
index = create_index(backend="memory", tokenizer=SimpleTokenizer())

# One-liner search over raw strings
results = quick_search(
    documents=["Python is great", "Java is verbose", "Rust is fast"],
    query="fast language",
    k=2,
)
```

`backend` accepts: `"memory"`.

## Error Handling

| Exception | Raised When |
|:----------|:------------|
| `ValueError` | Unknown `backend` passed to `create_index()` |

Empty queries return empty result lists without raising.

## Thread Safety

`InMemoryIndex` uses `threading.Lock` for index mutations. Search operations read from the current index state without locking.

## Integration Points

- `vector_store` -- Combine TF-IDF with vector similarity for hybrid search
- `llm` -- Use LLM output to enrich document metadata before indexing
- `logging_monitoring` -- Index operations and query performance logged

## Navigation

- **Human Documentation**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
