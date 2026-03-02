# Language Support -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Grammar lifecycle management for tree-sitter. Handles discovery, loading, and caching of compiled grammar shared libraries across platforms.

## Architecture

Registry pattern via `LanguageManager` class methods. A single class-level `_languages: dict[str, Any]` stores loaded `tree_sitter.Language` objects, shared across all instances.

## Key Classes

### `LanguageManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `load_language` | `library_path: str, lang_name: str` | `bool` | Load `.so`/`.dylib`/`.dll` grammar; returns success |
| `get_language` | `lang_name: str` | `Language or None` | Retrieve a loaded language by name |
| `discover_languages` | `search_path: str` | `None` | Walk directory, auto-load all grammar libraries |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: `tree_sitter` Python bindings

## Constraints

- Compiled libraries are platform-specific (macOS `.dylib`, Linux `.so`, Windows `.dll`).
- Grammar compilation requires a C compiler and access to grammar source repos.
- Zero-mock: real `tree_sitter.Language` objects required.

## Error Handling

- `load_language()` catches all exceptions and returns `False` on failure, logging at ERROR level.
- `discover_languages()` silently skips directories that do not exist.
