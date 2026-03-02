# Discovery Engine -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Core module discovery engine that enumerates Codomyrmex modules from the source tree, extracts metadata, and builds a dependency graph for health checking and introspection.

## Architecture

```
DiscoveryEngine
  +-- modules: dict[str, ModuleMetadata]
  +-- discover() -> list[ModuleMetadata]
  +-- get_module(name) -> ModuleMetadata
  +-- list_modules() -> list[ModuleMetadata]
  +-- dependency_tree(name) -> set[str]

DependencyGraph
  +-- add_node(name)
  +-- add_edge(from, to)
  +-- topological_sort() -> list[str]
  +-- has_cycle() -> bool
  +-- transitive_deps(name) -> set[str]
```

## Key Classes

### ModuleMetadata

| Field | Type | Notes |
|-------|------|-------|
| `name` | `str` | Module name (e.g., `"agents"`) |
| `path` | `Path` | Absolute path to module directory |
| `version` | `str` | From `__init__.py` or `"0.0.0"` |
| `status` | `str` | `"active"`, `"deprecated"`, `"experimental"` |
| `dependencies` | `list[str]` | Other codomyrmex modules required |
| `mcp_tools` | `list[str]` | MCP tool names if `mcp_tools.py` exists |
| `has_rasp` | `bool` | Whether all four RASP docs are present |

### DiscoveryEngine Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `discover()` | `list[ModuleMetadata]` | Scan source tree, populate registry |
| `get_module(name)` | `ModuleMetadata` | Lookup by name; `KeyError` if missing |
| `list_modules()` | `list[ModuleMetadata]` | All modules, alphabetically sorted |
| `dependency_tree(name)` | `set[str]` | Transitive dependency set |

### DependencyGraph Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `add_node(name)` | `None` | Register a module node |
| `add_edge(src, dst)` | `None` | Declare dependency edge |
| `topological_sort()` | `list[str]` | Load order respecting dependencies |
| `has_cycle()` | `bool` | Detect circular dependencies |
| `transitive_deps(name)` | `set[str]` | All transitive dependencies |

## Dependencies

- `pkgutil`, `importlib`, `pathlib` (stdlib)
- `codomyrmex.logging_monitoring`

## Constraints

- Discovery is filesystem-based; only directories with `__init__.py` are recognized.
- Dependency extraction relies on convention (declared in module metadata), not import analysis.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
- Parent: [system_discovery](../README.md)
