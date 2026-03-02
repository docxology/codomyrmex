# Language Support -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Manages tree-sitter language grammar libraries, providing loading from shared libraries (.so/.dylib/.dll), caching of loaded instances, and automatic discovery of language grammars in a directory tree.

## Architecture

Single class `LanguageManager` with class-level state (shared across all instances). Uses `importlib.import_module("tree_sitter")` to import the external tree-sitter package without shadowing the local `codomyrmex.tree_sitter` namespace.

## Key Classes

### `LanguageManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load_language` | `library_path: str, lang_name: str` | `bool` | Load a tree-sitter language from a compiled shared library; returns True on success |
| `get_language` | `lang_name: str` | `Language or None` | Retrieve a previously loaded language instance by name |
| `discover_languages` | `search_path: str` | `None` | Walk a directory tree and auto-load all `.so`, `.dylib`, and `.dll` files, inferring language names from filenames (strips `tree-sitter-` prefix) |

### Internal State

| Attribute | Type | Description |
|-----------|------|-------------|
| `_languages` | `dict[str, Language]` | Class-level cache of loaded language instances keyed by name |

## Dependencies

- **Internal**: none (standalone within `tree_sitter/`)
- **External**: `tree_sitter` (pip package; imported via `importlib` to avoid namespace collision)

## Constraints

- Requires pre-compiled tree-sitter grammar shared libraries; does not compile grammars from source.
- Language name inference from filenames assumes the pattern `tree-sitter-{lang}.{ext}`.
- Class-level `_languages` dict means loaded languages are global singletons.
- Load failures are logged at ERROR level and return `False`; no exception is raised.
- Zero-mock: real shared library loading only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `load_language` catches all exceptions during `tree_sitter.Language()` construction, logs the error, and returns `False`.
- `discover_languages` silently skips non-existent search paths.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
- Parent: [tree_sitter](../README.md)
