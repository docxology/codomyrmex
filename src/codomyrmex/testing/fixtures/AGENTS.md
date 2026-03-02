# Fixtures -- Agentic Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides test fixture management including lifecycle-scoped fixtures with dependency resolution, pre-defined data fixtures, JSON fixture loading, and a fluent builder API. Also provides `TestServerManager` for zero-mock integration testing with real FastAPI servers.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `FixtureManager` | `__init__.py` | Core fixture registry with `register()`, `get()`, `cleanup()`, `use()` context manager, and dependency resolution |
| `DataFixture` | `__init__.py` | List-based data container with `filter(**kwargs)` and `find(**kwargs)` query methods |
| `JSONFixtureLoader` | `__init__.py` | File-based fixture loading from JSON with internal cache |
| `FixtureBuilder` | `__init__.py` | Fluent builder: `with_field()`, `with_fields()`, `build()`, `build_many()` with incremental IDs |
| `TestServerManager` | `integration_servers.py` | Starts real FastAPI/uvicorn server on background thread for zero-mock HTTP integration testing |

## Operating Contracts

1. **Fixture Scoping**: `FixtureScope` enum defines 4 scopes: `FUNCTION`, `CLASS`, `MODULE`, `SESSION`. Function-scoped fixtures auto-cleanup when the `use()` context manager exits.
2. **Dependency Resolution**: `FixtureDefinition.dependencies` lists prerequisite fixture names. `FixtureManager.get()` recursively resolves dependencies before creating the requested fixture.
3. **Thread Safety**: `FixtureManager` uses `threading.Lock` for instance storage operations.
4. **Cleanup**: `cleanup(name)` invokes the registered `cleanup` callable on the fixture value. `cleanup_all()` cleans up all active instances.
5. **TestServerManager Lifecycle**: Call `start()` to launch uvicorn on a daemon thread (blocks up to 5s for startup confirmation), `stop()` to signal exit and join the thread (2s timeout).
6. **JSON Fixtures**: `JSONFixtureLoader.load(name)` reads `{base_path}/{name}.json`. Arrays become multi-record fixtures; single objects become single-element fixtures.

## Integration Points

- **FastAPI/uvicorn**: `TestServerManager` requires `fastapi` and `uvicorn` packages
- **testing parent**: Part of the `testing` module alongside `chaos`, `generators`, and `workflow`
- **Zero-Mock Policy**: `TestServerManager` aligns with the project zero-mock policy by providing real HTTP servers

## Navigation

- **Parent**: [testing/](../README.md)
- **Siblings**: [chaos/](../chaos/), [generators/](../generators/), [workflow/](../workflow/)
- **Spec**: [SPEC.md](SPEC.md)
