# Versioning — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Semantic versioning, deprecation lifecycle management, compatibility tracking, and migration guide generation for MCP tools. Enables tool authors to annotate functions with version metadata and consumers to check compatibility and plan migrations.

## Architecture

Two modules:

- **versioning.py**: Core primitives — `APIVersion` (semantic version value object), `DeprecationInfo` (metadata), `VersionedTool` (per-tool version record), `@versioned` and `@deprecated` decorators, and `CompatibilityMatrix`.
- **version_registry.py**: Aggregate registry — `VersionRegistry` tracks all tools, their versions, deprecation status, version history, and migration steps. Generates markdown summaries.

## Key Classes

### `APIVersion`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse` | `version_str: str` | `APIVersion` | Parse `"v1.2.3"` or `"1.2.3"` into an `APIVersion` instance |
| `is_compatible` | `other: APIVersion` | `bool` | True if same major and `other >= self` |
| `__str__` | — | `str` | Returns `"v1.2.3"` format |

Frozen dataclass with natural ordering on `(major, minor, patch)`.

### `VersionRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `name, version, introduced` | `None` | Register a versioned tool |
| `deprecate` | `name, since, removal, replacement` | `bool` | Mark a tool deprecated; returns `False` if not found |
| `is_deprecated` | `name: str` | `bool` | Check deprecation status |
| `get_tool` | `name: str` | `VersionedTool | None` | Look up a tool |
| `list_versions` | `name: str` | `list[APIVersion]` | All known versions of a tool |
| `list_deprecated` | — | `list[str]` | All deprecated tool names |
| `list_all` | — | `list[VersionedTool]` | All registered tools |
| `add_migration` | `tool_name, from_version, to_version, action, details` | `None` | Record a migration step |
| `migration_guide` | `from_ver, to_ver` | `list[MigrationStep]` | Filter migration steps by version range |
| `to_markdown` | — | `str` | Generate markdown registry summary |

### `CompatibilityMatrix`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_compatible` | `tool, from_ver, to_ver` | `None` | Record an explicit compatibility pair |
| `is_compatible` | `tool, ver_a, ver_b` | `bool` | Check compatibility; same-major defaults to `True` |

### Decorators

#### `@versioned(version, introduced)`

Attaches `_api_version`, `_api_introduced`, and `_api_deprecated=False` to the decorated function.

#### `@deprecated(since, removal, replacement, message)`

Attaches `_deprecation_info` and `_api_deprecated=True`. Emits `DeprecationWarning` via `warnings.warn(stacklevel=2)` on every call, including replacement and removal info in the message.

## Dependencies

- **Internal**: None (standard library only)
- **External**: Standard library only (`functools`, `warnings`, `dataclasses`)

## Constraints

- `APIVersion` is immutable (`frozen=True`); version values cannot be modified after creation.
- `VersionRegistry.register()` overwrites previous registrations for the same tool name but appends to version history.
- `deprecated()` warnings use `stacklevel=2` so the warning points to the caller, not the decorator.
- Zero-mock: real version objects only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `APIVersion.parse()` raises `ValueError`/`IndexError` on malformed version strings (not caught internally).
- `VersionRegistry.deprecate()` returns `False` for unknown tools rather than raising.
- All errors logged before propagation.
