# Codomyrmex Agents — src/codomyrmex/agents/context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides project-level awareness for agents by scanning directory trees, extracting Python symbols via AST parsing, building import dependency graphs, and selecting appropriate tools based on file type and task context.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `indexer.py` | `Symbol` | Dataclass representing a code symbol (function or class) with name, kind, file, line, and docstring |
| `indexer.py` | `ImportEdge` | Dataclass representing an import dependency edge between source file and target module |
| `indexer.py` | `RepoIndex` | Aggregated index holding lists of `Symbol` and `ImportEdge` with query helpers (`functions()`, `classes()`, `symbols_in_file()`) |
| `indexer.py` | `RepoIndexer` | Scans Python files using `ast.parse` to extract symbols and imports; supports single-file and directory indexing |
| `project.py` | `FileInfo` | Dataclass describing a source file with path, extension, size, and inferred module name |
| `project.py` | `ProjectContext` | Aggregated project view: all files, top-level modules, and test file paths with filtering helpers |
| `project.py` | `ProjectScanner` | Walks a project directory tree (respecting exclusion patterns) and builds a `ProjectContext` |
| `project.py` | `ToolSelector` | Maps `(file_extension, task_type)` pairs to lists of recommended tool names |

## Operating Contracts

- `RepoIndexer.index_file()` silently returns an empty `RepoIndex` for non-existent files, non-`.py` files, or files with syntax errors -- no exceptions propagated.
- `ProjectScanner` excludes `__pycache__`, `.git`, `.venv`, `node_modules`, and `*.egg-info` directories by default; override via constructor parameters.
- `ToolSelector.select()` falls back to extension-only matching when the exact `(ext, task_type)` key is not in `_TOOL_MAP`.
- `RepoIndexer.index_directory()` logs via `logging_monitoring` after completing a directory scan.
- All dataclasses expose a `to_dict()` method for JSON-safe serialization.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging via `get_logger`)
- **Used by**: Agent orchestration and task routing code that needs to understand project structure before dispatching tools

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Codomyrmex](../../../../README.md)
