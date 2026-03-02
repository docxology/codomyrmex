# Codomyrmex Agents — src/codomyrmex/feature_flags/storage

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Persistence backends for feature flag data. Defines an abstract `FlagStore` interface and two concrete implementations: `InMemoryFlagStore` (thread-safe dict-backed store for testing and ephemeral use) and `FileFlagStore` (JSON-file-backed store with atomic writes via temp-file-then-rename).

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `FlagStore` | ABC defining `get`, `set`, `delete`, `list_all` interface for all storage backends |
| `__init__.py` | `InMemoryFlagStore` | Thread-safe in-memory store using `threading.Lock`; suitable for tests and caching layers |
| `__init__.py` | `FileFlagStore` | JSON file-backed store with atomic writes (`os.replace` from temp file); thread-safe for writes |

## Operating Contracts

- All `FlagStore` implementations must be safe for concurrent reads; write safety varies by backend.
- `FileFlagStore` performs atomic writes: data is written to `{path}.tmp` then renamed via `os.replace`.
- `FileFlagStore` auto-creates the JSON file on initialization if it does not exist.
- `InMemoryFlagStore` guards all reads and writes with a `threading.Lock`.
- Values stored must be JSON-serializable for `FileFlagStore`.
- `FileFlagStore._read` raises `json.JSONDecodeError` on corrupt files (does not silently fall back).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `json`, `os`, `threading` (standard library only)
- **Used by**: `feature_flags.core.FeatureManager` (as a persistence layer), any module needing durable flag state

## Navigation

- **Parent**: [feature_flags](../README.md)
- **Root**: [Root](../../../../README.md)
