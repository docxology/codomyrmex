# Agents Context — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides repository indexing (symbol extraction and import graph construction) and project scanning (file tree awareness with module detection) to give agents contextual intelligence about the codebase they are operating in.

## Architecture

Two independent subsystems: `RepoIndexer` uses Python's `ast` module for static analysis of source files, while `ProjectScanner` uses `os.walk` for filesystem enumeration. Both produce immutable dataclass results. `ToolSelector` provides a lookup table mapping file types and task types to recommended tool sets.

## Key Classes

### `RepoIndexer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `index_file` | `file_path: str \| Path` | `RepoIndex` | Parse a single Python file, extract `Symbol` and `ImportEdge` entries |
| `index_directory` | `root: str \| Path` | `RepoIndex` | Walk a directory, index all `.py` files, return merged `RepoIndex` |

### `RepoIndex`

| Method / Property | Parameters | Returns | Description |
|-------------------|-----------|---------|-------------|
| `symbol_count` | — | `int` | Total number of extracted symbols |
| `symbols_in_file` | `file_path: str` | `list[Symbol]` | Filter symbols by source file |
| `functions` | — | `list[Symbol]` | All function-type symbols |
| `classes` | — | `list[Symbol]` | All class-type symbols |
| `to_dict` | — | `dict[str, Any]` | Summary dict with counts |

### `ProjectScanner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `extensions: set[str] \| None`, `exclude_dirs: set[str] \| None` | `None` | Configure file extensions and exclusion patterns |
| `scan` | `root: str \| Path` | `ProjectContext` | Walk directory tree and build project context |

### `ToolSelector`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `select` | `file_ext: str`, `task_type: str` | `list[str]` | Return recommended tools for the given file type and task |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (`get_logger`)
- **External**: Standard library only (`ast`, `os`, `pathlib`, `dataclasses`)

## Constraints

- `RepoIndexer` only supports Python files (`.py` extension); other languages are silently skipped.
- `Symbol.docstring` is truncated to 80 characters in `to_dict()` output.
- `ProjectScanner` default extensions: `py`, `md`, `toml`, `yaml`, `yml`.
- `ToolSelector._TOOL_MAP` is a class-level static dict; extending it requires subclassing or direct mutation.
- Zero-mock: all scanning uses real filesystem access; `NotImplementedError` for unimplemented paths.

## Error Handling

- `SyntaxError` and `UnicodeDecodeError` during AST parsing return an empty `RepoIndex` (no propagation).
- `OSError` during `os.path.getsize()` defaults file size to 0.
- Non-existent or non-directory paths passed to `ProjectScanner.scan()` return an empty `ProjectContext`.
- All successful scans are logged via `logging_monitoring` with file and symbol counts.
