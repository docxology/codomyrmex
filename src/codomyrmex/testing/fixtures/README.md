# fixtures

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Test fixture management with scoped lifecycle, dependency resolution, and multiple data sources. Provides `FixtureManager` for registering, resolving, and cleaning up test resources, plus `DataFixture` for pre-defined data, `JSONFixtureLoader` for file-based fixtures, and `FixtureBuilder` for fluent data construction.

## Key Exports

- **`FixtureManager`** — Core fixture lifecycle manager with `register()`, `get()`, `cleanup()`, `cleanup_all()`, and context manager `use()`. Thread-safe with dependency resolution.
- **`DataFixture`** — Pre-defined data fixture wrapping a list of dicts with `filter(**kwargs)`, `find(**kwargs)`, and `all()` query methods
- **`JSONFixtureLoader`** — Loads fixtures from JSON files with caching. `load("name")` returns a `DataFixture` from `{base_path}/{name}.json`
- **`FixtureBuilder`** — Fluent builder: `FixtureBuilder("user").with_field("name", "Alice").build()`. Supports `build_many(count)` for batch creation
- **`FixtureScope`** — Enum: `FUNCTION`, `CLASS`, `MODULE`, `SESSION`
- **`FixtureDefinition`** — Dataclass: name, factory, scope, cleanup callback, dependencies
- **`FixtureInstance`** — Dataclass: name, value, scope, created_at timestamp

## Navigation

- **Parent Module**: [testing](../README.md)
- **Parent Directory**: [codomyrmex](../../README.md)
