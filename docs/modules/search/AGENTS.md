# Search Module — Agent Coordination

## Purpose

Full-text search, semantic search, and indexing utilities.

## Key Capabilities

- **Document**: A searchable document.
- **SearchResult**: A search result.
- **Tokenizer**: Abstract tokenizer.
- **SimpleTokenizer**: Simple whitespace and punctuation tokenizer.
- **SearchIndex**: Abstract search index.
- `create_index()`: Create a search index.
- `quick_search()`: Quick search over a list of strings.
- `tokenize()`: tokenize

## Agent Usage Patterns

```python
from codomyrmex.search import Document

# Agent initializes search
instance = Document()
```

## Integration Points

- **Source**: [src/codomyrmex/search/](../../../src/codomyrmex/search/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k search -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
