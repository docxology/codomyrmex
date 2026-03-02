# Discovery Engine Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Module discovery and dependency analysis for the Codomyrmex platform. Agents use the `DiscoveryEngine` to enumerate installed modules, inspect their metadata, and query the dependency graph.

## Key Components

| Component | Type | Role |
|-----------|------|------|
| `DiscoveryEngine` | Class | Scans `src/codomyrmex/` for modules, builds dependency graph |
| `ModuleMetadata` | Dataclass | Name, version, status, dependencies, MCP tools, RASP doc paths |
| `DependencyGraph` | Class | DAG of module dependencies with cycle detection |

## Operating Contracts

- `DiscoveryEngine.discover()` scans the source tree and populates the module registry.
- `get_module(name)` returns `ModuleMetadata`; raises `KeyError` if unknown.
- `list_modules()` returns all discovered modules sorted alphabetically.
- `dependency_tree(module_name)` returns transitive dependency set.
- The engine uses `pkgutil` for package enumeration and inspects `__init__.py` for metadata.

## Integration Points

- Exposes MCP tools: `health_check`, `list_modules`, `dependency_tree`.
- Used by `system_discovery/health` for health checks against discovered modules.
- CLI `codomyrmex modules` command delegates to this engine.

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- Parent: [system_discovery](../README.md)
