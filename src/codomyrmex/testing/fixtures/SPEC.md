# Fixtures -- Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Test fixture management module providing scoped lifecycle fixtures, data fixtures with query methods, JSON file loading, a fluent builder, and a real HTTP server manager for zero-mock integration testing.

## Architecture

```
fixtures/
  __init__.py             -- FixtureManager, DataFixture, JSONFixtureLoader, FixtureBuilder, data classes
  integration_servers.py  -- TestServerManager (FastAPI/uvicorn background thread)
```

## Key Classes

### FixtureManager

| Method | Signature | Description |
|--------|-----------|-------------|
| `register` | `(name, factory, scope=FUNCTION, cleanup=None, dependencies=None) -> FixtureManager` | Register a fixture definition |
| `get` | `(name: str) -> Any` | Get or create instance; resolves dependencies recursively |
| `cleanup` | `(name: str) -> None` | Invoke cleanup callable and remove instance |
| `cleanup_all` | `() -> None` | Clean up all active fixture instances |
| `use` | `(name: str) -> ContextManager` | Context manager; auto-cleans FUNCTION-scoped fixtures on exit |
| `list_fixtures` | `() -> list[str]` | List all registered fixture names |

### FixtureScope (Enum)

Values: `FUNCTION`, `CLASS`, `MODULE`, `SESSION`

### DataFixture

| Method | Signature | Description |
|--------|-----------|-------------|
| `filter` | `(**kwargs) -> list[dict]` | Filter records by exact field value match |
| `find` | `(**kwargs) -> dict | None` | Return first matching record or None |
| `all` | `() -> list[dict]` | Return all records |

Supports `__getitem__`, `__len__`, `__iter__` for list-like access.

### JSONFixtureLoader

| Method | Signature | Description |
|--------|-----------|-------------|
| `load` | `(name: str) -> DataFixture` | Load `{base_path}/{name}.json`, cache result |
| `clear_cache` | `() -> None` | Clear internal cache |

### FixtureBuilder

| Method | Signature | Description |
|--------|-----------|-------------|
| `with_field` | `(key, value) -> FixtureBuilder` | Add single field (fluent) |
| `with_fields` | `(**kwargs) -> FixtureBuilder` | Add multiple fields (fluent) |
| `build` | `() -> dict[str, Any]` | Build single fixture dict |
| `build_many` | `(count, id_field="id") -> list[dict]` | Build N fixtures with incremental IDs |

### TestServerManager

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_route` | `(path, endpoint, methods=["GET"]) -> None` | Add route to underlying FastAPI app |
| `start` | `() -> None` | Start uvicorn on daemon thread; waits up to 5s for startup |
| `stop` | `() -> None` | Signal server exit and join thread (2s timeout) |

Constructor: `(host="127.0.0.1", port=8000)`. Creates FastAPI app with default `/health` endpoint.

## Dependencies

- Standard library: `json`, `threading`, `pathlib`
- External: `fastapi`, `uvicorn` (for `TestServerManager`)

## Constraints

- `FixtureManager.get()` does not detect circular dependencies; recursive resolution would stack overflow.
- `JSONFixtureLoader` expects files to contain either a JSON array or a single JSON object.
- `TestServerManager.start()` raises `RuntimeError` if server does not start within 5 seconds.
- Thread safety is per-`FixtureManager` instance (one lock per manager).

## Error Handling

- `FixtureManager.get()` raises `KeyError` for unregistered fixture names
- `JSONFixtureLoader.load()` raises `FileNotFoundError` for missing fixture files
- `TestServerManager.start()` raises `RuntimeError` on startup timeout
