# Codomyrmex Agents — src/codomyrmex/model_context_protocol/versioning

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides semantic versioning, deprecation management, and compatibility tracking for MCP tools. Includes version and deprecation decorators for annotating functions, a version registry for tracking tool lifecycle, migration guide generation, and a compatibility matrix for cross-version checks.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `versioning.py` | `APIVersion` | Frozen, ordered dataclass for semantic versions (major.minor.patch) with `parse()` factory and `is_compatible()` check |
| `versioning.py` | `DeprecationInfo` | Dataclass: since, removal, replacement, message |
| `versioning.py` | `VersionedTool` | Dataclass combining tool name, version, deprecation flag, and introduction version |
| `versioning.py` | `versioned()` | Decorator that attaches `_api_version` and `_api_introduced` metadata to functions |
| `versioning.py` | `deprecated()` | Decorator that marks functions as deprecated; emits `DeprecationWarning` on call with replacement/removal info |
| `versioning.py` | `CompatibilityMatrix` | Tracks explicit version compatibility pairs; same-major versions are compatible by default |
| `version_registry.py` | `VersionRegistry` | Registry of all versioned tools; supports register, deprecate, list, and migration guide generation |
| `version_registry.py` | `MigrationStep` | Dataclass representing a single migration action (tool, from/to version, action, details) |

## Operating Contracts

- `APIVersion` is frozen and ordered; comparison uses `(major, minor, patch)` tuple ordering.
- `is_compatible()` returns `True` when both versions share the same major and `other >= self`.
- `deprecated()` decorator emits `DeprecationWarning` (via `warnings.warn`) at call time with `stacklevel=2`.
- `VersionRegistry.deprecate()` returns `False` if the tool is not registered (no error raised).
- `CompatibilityMatrix.is_compatible()` defaults to `True` for same-major versions; explicit entries extend compatibility across major versions.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`functools`, `warnings`, `dataclasses`)
- **Used by**: Any MCP tool author using `@versioned` or `@deprecated` decorators, PAI MCP bridge for surfacing deprecation info

## Navigation

- **Parent**: [model_context_protocol](../README.md)
- **Root**: [Root](../../../../README.md)
