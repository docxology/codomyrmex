# Codomyrmex Agents -- src/codomyrmex/coding/parsers/tree_sitter/parsers

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Contains the core tree-sitter parser wrapper and a regex-based fallback AST layer. Provides data types for AST nodes, source positions, and abstract `Parser` base class with concrete `PythonParser` and `JavaScriptParser` implementations.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `parser.py` | `TreeSitterParser` | Wraps `tree_sitter.Parser`; `parse()` and `query()` |
| `__init__.py` | `NodeType`, `Position`, `Range`, `ASTNode` | Core AST data types |
| `__init__.py` | `Parser` (ABC) | Abstract base class for language parsers |
| `__init__.py` | `PythonParser` | Regex-based Python parser (functions, classes, imports) |
| `__init__.py` | `JavaScriptParser` | Regex-based JavaScript parser (functions, classes, imports) |
| `__init__.py` | `get_parser(language)` | Factory function returning the correct `Parser` |
| `__init__.py` | `parse_file(filepath)` | Convenience: detect language and parse a file |

## Operating Contracts

- `TreeSitterParser` requires a pre-loaded `tree_sitter.Language` instance; call `LanguageManager.load_language()` first.
- Regex-based parsers (`PythonParser`, `JavaScriptParser`) are best-effort heuristic parsers -- they do not produce a full AST.
- `get_parser()` raises `ValueError` for unsupported languages.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `tree_sitter` (external), `re`, `ast` (stdlib)
- **Used by**: `coding.pattern_matching`, `coding.review`, `coding.static_analysis`

## Navigation

- **Parent**: [tree_sitter](../README.md)
- **Root**: [Root](../../../../../../README.md)
