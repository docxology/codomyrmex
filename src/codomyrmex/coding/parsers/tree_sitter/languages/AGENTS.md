# Codomyrmex Agents -- src/codomyrmex/coding/parsers/tree_sitter/languages

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Manages loading and caching of tree-sitter grammar shared libraries (`.so`, `.dylib`, `.dll`). Provides `LanguageManager`, a class-level registry that maps language names to loaded `tree_sitter.Language` instances.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `languages.py` | `LanguageManager` | Class-method based registry for loaded grammars |
| `__init__.py` | _(empty exports)_ | Namespace package marker |

## Operating Contracts

- `load_language()` must be called before `get_language()` for any grammar.
- `discover_languages()` walks a directory for `.so`/`.dylib`/`.dll` files and infers language names from filenames (`tree-sitter-python.so` -> `python`).
- Languages are cached in a class-level `_languages` dict -- loading the same language twice is a no-op (returns cached).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `tree_sitter` (external), `os` (stdlib)
- **Used by**: `parsers.tree_sitter.parsers.TreeSitterParser`

## Navigation

- **Parent**: [tree_sitter](../README.md)
- **Root**: [Root](../../../../../../README.md)
