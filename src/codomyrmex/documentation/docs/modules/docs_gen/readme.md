# docs_gen

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation generation module providing tools for extracting API documentation from Python source code, building searchable in-memory indices, and generating static documentation site configuration. Built around three core components: `APIDocExtractor` for AST-based docstring extraction, `SearchIndex` for inverted-index full-text search, and `SiteGenerator` for site orchestration.

## PAI Integration

| PAI Phase | Capability |
|-----------|-----------|
| LEARN | Extract and index API documentation from source code |
| OBSERVE | Search indexed documentation via `SearchIndex` |
| BUILD | Generate static site configuration via `SiteGenerator` |

## Key Exports

- **`APIDocExtractor`** -- Extract docstrings, signatures, and metadata from Python modules
- **`ModuleDoc`** -- Extracted module-level documentation data
- **`ClassDoc`** -- Extracted class documentation with methods
- **`FunctionDoc`** -- Extracted function documentation with signatures
- **`SearchIndex`** -- In-memory inverted index for full-text documentation search
- **`IndexEntry`** -- Single entry in the search index
- **`SearchResult`** -- Search result with relevance scoring
- **`SiteGenerator`** -- Orchestrates extraction, indexing, and site config generation
- **`SiteConfig`** -- Configuration for generated documentation site

## MCP Tools

| Tool | Description |
|------|-------------|
| `docs_gen_extract_api` | Extract API documentation from Python source code string |
| `docs_gen_build_search_index` | Extract docs and build a searchable in-memory index |

## Quick Start

```python
from codomyrmex.docs_gen import APIDocExtractor, SearchIndex

extractor = APIDocExtractor()
doc = extractor.extract_from_source("def greet(name: str) -> str:\n    '''Say hello.'''\n    return f'Hello {name}'")
print(doc.functions[0].name)  # "greet"

index = SearchIndex()
index.add("greet", title="greet", content="Say hello.", tags=["function"])
results = index.search("hello")
```

## Architecture

```
docs_gen/
  __init__.py            -- Package root; exports all components
  api_doc_extractor.py   -- APIDocExtractor, ModuleDoc, ClassDoc, FunctionDoc
  search_index.py        -- SearchIndex, IndexEntry, SearchResult
  site_generator.py      -- SiteGenerator, SiteConfig
  mcp_tools.py           -- 2 MCP tool definitions
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/docs_gen/ -v
```

## Navigation

- [Root](../../../../../../README.md)
