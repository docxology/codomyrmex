# Parsers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides source-code parsing across multiple languages. The primary backend is tree-sitter (C-based, high-performance); a regex-based fallback parser exists for Python and JavaScript when tree-sitter grammars are unavailable.

## Architecture

Facade pattern: `parsers/__init__.py` re-exports everything from `tree_sitter/`, which itself is split into four sub-modules -- `parsers` (core parser wrapper), `languages` (grammar loading), `queries` (S-expression query engine), and `transformers` (AST rewriting).

## Key Classes

### `TreeSitterParser` (tree_sitter/parsers/parser.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse` | `source_code: str` | `tree_sitter.Tree` | Parse source into a syntax tree |
| `query` | `tree: Tree, query_str: str` | `list` | Execute S-expression query against tree |

### `LanguageManager` (tree_sitter/languages/languages.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load_language` | `library_path: str, lang_name: str` | `bool` | Load grammar from shared library |
| `get_language` | `lang_name: str` | `Language or None` | Retrieve a loaded language |
| `discover_languages` | `search_path: str` | `None` | Auto-discover `.so/.dylib/.dll` grammars |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: `tree-sitter` Python bindings, compiled grammar libraries

## Constraints

- Grammar compilation requires a C compiler and grammar source repos.
- Compiled `.so`/`.dylib` files are platform-specific.
- Zero-mock: real tree-sitter bindings required; `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised for unsupported languages in the fallback parser.
- `ToolNotFoundError` if tree-sitter bindings are missing at runtime.
- All errors logged before propagation.
