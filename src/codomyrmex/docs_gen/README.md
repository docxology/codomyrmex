# docs_gen -- Documentation Generation

**Version**: v1.0.2 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `docs_gen` module is the codomyrmex documentation pipeline. It extracts structured API documentation from Python source code using AST parsing, builds searchable in-memory inverted indices over the extracted documentation, and generates static documentation site configuration compatible with MkDocs and mkdocs-material.

Three components work together: `APIDocExtractor` parses Python source into structured `ModuleDoc`, `ClassDoc`, and `FunctionDoc` dataclasses. `SearchIndex` builds a tokenized inverted index with relevance scoring over the extracted documentation. `SiteGenerator` orchestrates extraction and indexing, then outputs a `SiteConfig` containing navigation trees and page definitions ready for rendering.

This module does not expose MCP tools. It is used as a Python library within build scripts, CI/CD pipelines, and other codomyrmex modules that need programmatic access to documentation extraction and indexing.

## Key Capabilities

- **AST-based documentation extraction** -- Parses Python source via `ast` to extract module docstrings, class hierarchies (including base classes), function signatures (including parameter lists), decorator names, and async/sync status.
- **Structured documentation models** -- `ModuleDoc`, `ClassDoc`, and `FunctionDoc` dataclasses provide typed, structured representations of extracted documentation with full attribute access.
- **`__all__` export detection** -- Automatically extracts module-level `__all__` lists to identify public API surface.
- **Markdown rendering** -- `APIDocExtractor.to_markdown()` converts extracted `ModuleDoc` objects into formatted Markdown suitable for documentation sites.
- **In-memory inverted index** -- `SearchIndex` tokenizes document content and titles into a word-level inverted index for fast full-text search with no external dependencies.
- **Relevance scoring** -- Search results are ranked by token hit count with a 2x bonus for title matches, producing meaningful ordering without heavyweight search infrastructure.
- **Snippet extraction** -- Search results include context-aware snippets centered around the first matching token in the document content.
- **Tag-based indexing** -- Documents can be indexed with custom tags for categorical search alongside full-text.
- **MkDocs site generation** -- `SiteGenerator` produces complete `mkdocs.yml` configuration including navigation trees, theme settings (material with slate scheme), and plugin declarations.
- **Custom page support** -- `SiteGenerator.add_page()` allows injecting arbitrary Markdown pages alongside auto-generated API reference pages.

## Quick Start

```python
from codomyrmex.docs_gen import APIDocExtractor, ModuleDoc

# Extract documentation from Python source code
extractor = APIDocExtractor()
source = open("path/to/module.py").read()
doc: ModuleDoc = extractor.extract_from_source(source, "my_module")

# Access structured documentation
for cls in doc.classes:
    print(f"Class: {cls.name}, bases: {cls.bases}")
    for method in cls.methods:
        print(f"  Method: {method.name}{method.signature}")

for func in doc.functions:
    print(f"Function: {func.name}{func.signature}, async={func.is_async}")

# Render as Markdown
markdown = extractor.to_markdown(doc)
```

```python
from codomyrmex.docs_gen import SearchIndex, SearchResult

# Build a searchable index
index = SearchIndex()
index.add(doc_id="my_module", title="My Module", content=markdown, path="api/my_module.md")
results: list[SearchResult] = index.search("function_name", limit=5)
for r in results:
    print(f"{r.title} (score={r.score}): {r.snippet}")
```

```python
from codomyrmex.docs_gen import SiteGenerator

# Generate a full documentation site config
gen = SiteGenerator(title="My Project Docs")
gen.add_module_source(source, "my_module")
gen.add_page("guides/quickstart.md", "# Quick Start\n...", title="Quick Start")

mkdocs_yaml = gen.to_mkdocs_yaml()  # Ready to write to mkdocs.yml
pages = gen.generate_pages()         # dict[str, str] of path -> markdown content
```

## Module Structure

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports: all 9 public symbols |
| `api_doc_extractor.py` | AST-based Python source parser; `APIDocExtractor`, `ModuleDoc`, `ClassDoc`, `FunctionDoc` |
| `search_index.py` | In-memory inverted index; `SearchIndex`, `IndexEntry`, `SearchResult` |
| `site_generator.py` | Site orchestration and MkDocs config; `SiteGenerator`, `SiteConfig` |
| `PAI.md` | PAI integration documentation and phase mapping |
| `API_SPECIFICATION.md` | Programmatic interface specification |
| `MCP_TOOL_SPECIFICATION.md` | MCP tool specification (no MCP tools exposed) |

## Configuration

`SiteGenerator` accepts a `title` parameter at construction (default: `"Codomyrmex Documentation"`).

`SiteConfig` exposes the following configuration fields:
- `title` -- Site title (default: `"Codomyrmex Documentation"`)
- `theme` -- Theme name (default: `"material"`)
- `plugins` -- Enabled plugins (default: `["search", "mkdocstrings"]`)
- `base_url` -- Base URL (default: `"/"`)
- `nav` -- Auto-generated navigation structure

`SearchIndex.search()` accepts a `limit` parameter (default: `10`) to control maximum result count.

## Dependencies

- **Python standard library only**: `ast`, `re`, `collections.defaultdict`, `dataclasses`
- No external runtime dependencies
- No MCP tool dependencies

## Related Modules

- [documentation/](../documentation/) -- Higher-level documentation maintenance, quality audits, and education
- [coding/](../coding/) -- Code analysis and generation (complementary tooling)
- [search/](../search/) -- General-purpose search (docs_gen search is specialized for API docs)
- [PAI.md](PAI.md) -- PAI integration details
- [Root PAI bridge](../../../PAI.md) -- Authoritative PAI system bridge document
