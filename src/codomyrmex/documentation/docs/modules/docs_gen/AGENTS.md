# docs_gen - Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Documentation generation module exposing 2 MCP tools for extracting API documentation from Python source and building searchable indices. Uses AST-based analysis via `APIDocExtractor` and inverted-index search via `SearchIndex`.

## Key Files

| File | Role |
|------|------|
| `__init__.py` | Package root; exports all components |
| `mcp_tools.py` | 2 MCP tool definitions |
| `api_doc_extractor.py` | `APIDocExtractor`, `ModuleDoc`, `ClassDoc`, `FunctionDoc` |
| `search_index.py` | `SearchIndex`, `IndexEntry`, `SearchResult` |
| `site_generator.py` | `SiteGenerator`, `SiteConfig` |

## MCP Tools Available

| Tool | Parameters | Returns |
|------|-----------|---------|
| `docs_gen_extract_api` | `source_code: str, module_name: str` | Module docstring, functions, classes with counts |
| `docs_gen_build_search_index` | `source_code: str, module_name: str` | Index statistics with entry counts |

## Agent Instructions

1. `docs_gen_extract_api` accepts raw Python source code as a string, not file paths.
2. `docs_gen_build_search_index` combines extraction and indexing in one call.
3. Both tools return `{"status": "success", ...}` on success or `{"status": "error", "message": "..."}` on failure.
4. The `module_name` parameter is optional and used for labeling output.

## Operating Contracts

- Both tools are read-only and produce no side effects.
- `APIDocExtractor` uses Python's `ast` module for parsing; invalid Python source raises errors.
- `SearchIndex` is ephemeral (in-memory); state does not persist across calls.

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Primary Tools |
|-----------|-------------|---------------|
| Engineer | Full | Both tools |
| Architect | Read | `docs_gen_extract_api` |

## Navigation

- [Root](../../../../../../README.md)
