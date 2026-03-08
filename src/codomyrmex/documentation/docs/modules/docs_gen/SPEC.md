# docs_gen -- Technical Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation generation module with three components: AST-based API extraction, in-memory full-text search indexing, and static site generation orchestration.

## Design Principles

- **AST-based**: Documentation extraction uses Python's `ast` module, not regex.
- **Composable pipeline**: Extraction, indexing, and site generation are independent stages.
- **Ephemeral index**: `SearchIndex` is in-memory; no disk persistence.

## Architecture

```
docs_gen/
  __init__.py            -- Package root (exports 9 symbols)
  api_doc_extractor.py   -- APIDocExtractor, ModuleDoc, ClassDoc, FunctionDoc
  search_index.py        -- SearchIndex, IndexEntry, SearchResult
  site_generator.py      -- SiteGenerator, SiteConfig
  mcp_tools.py           -- 2 MCP tools (docs_gen_extract_api, docs_gen_build_search_index)
```

## Functional Requirements

### APIDocExtractor
- `extract_from_source(source: str, module_name: str) -> ModuleDoc` -- Parse Python source and return structured documentation.
- Extracts: module docstring, function names/signatures/docstrings, class names/docstrings/methods.

### SearchIndex
- `add(id: str, title: str, content: str, tags: list[str])` -- Add entry to inverted index.
- `search(query: str) -> list[SearchResult]` -- Full-text search with relevance scoring.

### SiteGenerator
- Orchestrates `APIDocExtractor` + `SearchIndex` to produce site configuration.
- `SiteConfig` holds output paths and rendering options.

## Interface Contracts

MCP tool return formats:
- `docs_gen_extract_api`: `{"status": "success", "module_name": str, "docstring": str, "functions": list, "classes": list, "function_count": int, "class_count": int}`
- `docs_gen_build_search_index`: `{"status": "success", "module_name": str, "indexed_entries": int, "function_count": int, "class_count": int}`

Data classes:
- `FunctionDoc(name: str, signature: str, docstring: str)`
- `ClassDoc(name: str, docstring: str, methods: list[FunctionDoc])`
- `ModuleDoc(name: str, docstring: str, functions: list[FunctionDoc], classes: list[ClassDoc])`

## Dependencies

- **Internal**: `model_context_protocol.decorators` for `@mcp_tool`
- **Standard library**: `ast`, `inspect` (no external dependencies)

## Constraints

- `SearchIndex` is not persistent; each MCP tool call creates a fresh index.
- `APIDocExtractor` requires valid Python source; syntax errors raise exceptions.

## Navigation

- [Root](../../../../../../README.md)
