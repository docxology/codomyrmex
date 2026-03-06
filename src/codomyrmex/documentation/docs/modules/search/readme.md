# Search Module

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

Full-text search with TF-IDF, fuzzy matching, and query parsing.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **OBSERVE** | Document discovery, full-text search across codebases and knowledge bases | `search_documents`, `search_index_query` |
| **THINK** | Fuzzy search for relevant context and prior decisions | `search_fuzzy` |
| **LEARN** | Index new documents for future retrieval | `search_index_query` |

PAI's OBSERVE phase relies heavily on search for codebase and documentation discovery. `search_documents` provides full-text search; `search_fuzzy` enables approximate matching for context retrieval during THINK. Engineer agents use all three tools.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes

- **`Document`** — A searchable document.
- **`SearchResult`** — A search result.
- **`Tokenizer`** — Abstract tokenizer.
- **`SimpleTokenizer`** — Simple whitespace and punctuation tokenizer.
- **`SearchIndex`** — Abstract search index.
- **`InMemoryIndex`** — In-memory inverted index with TF-IDF scoring.
- **`FuzzyMatcher`** — Fuzzy string matching utilities.
- **`QueryParser`** — Parse search queries with operators.

### Functions

- **`create_index()`** — Create a search index.
- **`quick_search()`** — Quick search over a list of strings.

## Quick Start

```python
from codomyrmex.search import InMemoryIndex, Document, quick_search

# Index documents
index = InMemoryIndex()
index.index(Document(id="1", content="Python programming language"))
index.index(Document(id="2", content="JavaScript web development"))
index.index(Document(id="3", content="Python data science and ML"))

# Search with TF-IDF scoring
results = index.search("python", k=5)
for r in results:
    print(f"{r.score:.2f}: {r.document.content}")
    print(f"  Highlights: {r.highlights}")

# Quick one-liner search
docs = ["apple pie recipe", "orange juice", "apple cider"]
results = quick_search(docs, "apple", k=2)
```

## Directory Structure

- `models.py` — Data models (Document, SearchResult)
- `index.py` — Search index implementations (SearchIndex, InMemoryIndex)
- `tokenizer.py` — Tokenizers (Tokenizer, SimpleTokenizer)
- `parser.py` — Query parsing logic (QueryParser)
- `matching.py` — Fuzzy matching utilities (FuzzyMatcher)
- `__init__.py` — Public API re-exports

## Exports

| Class/Function | Description |
| :--- | :--- |
| `InMemoryIndex` | In-memory inverted index with TF-IDF |
| `Document` | Searchable document with id, content, metadata |
| `SearchResult` | Result with document, score, highlights |
| `SimpleTokenizer` | Whitespace tokenizer with lowercase/min_length |
| `FuzzyMatcher` | Levenshtein distance fuzzy matching |
| `QueryParser` | Parse `+must -exclude "phrase"` queries |
| `create_index(backend)` | Factory for search indexes |
| `quick_search(docs, query)` | One-liner search over strings |

## Query Syntax

```python
from codomyrmex.search import QueryParser

parser = QueryParser()
parsed = parser.parse('+python -java "machine learning"')
# {
#   'terms': [],
#   'must': ['python'],
#   'must_not': ['java'],
#   'phrases': ['machine learning']
# }
```

## Fuzzy Matching

```python
from codomyrmex.search import FuzzyMatcher

# Similarity ratio (0-1)
FuzzyMatcher.similarity_ratio("apple", "aple")  # 0.8

# Find best match
candidates = ["python", "java", "javascript"]
FuzzyMatcher.find_best_match("pythn", candidates)  # "python"
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k search -v
```

## Documentation

- [Module Documentation](../../../docs/modules/search/README.md)
- [Agent Guide](../../../docs/modules/search/AGENTS.md)
- [Specification](../../../docs/modules/search/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
