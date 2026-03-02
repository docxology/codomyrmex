# Flag Storage -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides pluggable storage backends for feature flag data. The `FlagStore` ABC defines a four-method contract (get, set, delete, list_all). Two implementations ship: `InMemoryFlagStore` for fast ephemeral storage and `FileFlagStore` for durable JSON-file persistence with atomic writes.

## Architecture

Storage follows a simple Repository pattern. `FlagStore` is the interface; concrete backends own their own threading and I/O strategy. `FileFlagStore` uses write-to-temp-then-`os.replace` for crash safety.

## Key Classes

### `FlagStore` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get` | `key: str` | `Any \| None` | Retrieve a flag value by key; `None` if absent |
| `set` | `key: str, value: Any` | `None` | Store or update a flag value |
| `delete` | `key: str` | `bool` | Remove a flag; returns `True` if key existed |
| `list_all` | none | `dict[str, Any]` | Snapshot of all stored key-value pairs |

### `InMemoryFlagStore`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get` | `key: str` | `Any \| None` | Thread-safe dict lookup |
| `set` | `key: str, value: Any` | `None` | Thread-safe dict insert |
| `delete` | `key: str` | `bool` | Thread-safe dict removal |
| `list_all` | none | `dict[str, Any]` | Returns a shallow copy of the internal dict |
| `__len__` | none | `int` | Number of stored flags |

### `FileFlagStore`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `path: str` | -- | Path to JSON file; auto-created if missing |
| `get` | `key: str` | `Any \| None` | Reads JSON file each call (no caching) |
| `set` | `key: str, value: Any` | `None` | Read-modify-write under threading lock; atomic file replace |
| `delete` | `key: str` | `bool` | Read-modify-write under threading lock; atomic file replace |
| `list_all` | none | `dict[str, Any]` | Full JSON file read |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`json`, `os`, `threading`, `abc`, `logging`)

## Constraints

- `FileFlagStore.get` re-reads the file on every call (no in-memory cache); suitable for low-frequency reads.
- `FileFlagStore._write` serializes with `indent=2, sort_keys=True` for human-readable diffs.
- All values stored via `FileFlagStore` must be JSON-serializable.
- `FileFlagStore._read` returns `{}` on `FileNotFoundError` (valid first-use case) but raises `json.JSONDecodeError` on corrupt content.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `FileFlagStore._read` raises `json.JSONDecodeError` with a logged warning on corrupt JSON (no silent fallback).
- `FileNotFoundError` during read is handled gracefully (returns empty dict).
- All errors logged before propagation.
