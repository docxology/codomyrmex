# Migration — Functional Specification

## Overview

The migration submodule provides two independent migration systems: a callable-based step runner (`MigrationRunner`) for programmatic migrations with rollback, and a SQL-based lifecycle manager (`MigrationManager`) for database schema migrations with tracking, dependency resolution, and dry-run support. A `DataMigrator` pipeline handles record-level data transformations.

## Architecture

```
migration/
  models.py            -- MigrationStep, Migration, MigrationResult, MigrationStatus,
                          MigrationDirection, DataTransformer (ABC), FieldRenameTransformer,
                          FieldTypeTransformer, CompositeTransformer
  executor.py          -- MigrationRunner, DataMigrator
  migration_manager.py -- DatabaseConnector, MigrationManager, run_migrations
  __init__.py          -- Re-exports
```

Two parallel class hierarchies:

- **Step-based** (models.py + executor.py): `Migration` holds ordered `MigrationStep` instances with `up_fn`/`down_fn` callables. `MigrationRunner` executes them sequentially.
- **SQL-based** (migration_manager.py): `MigrationManager` uses `DatabaseConnector` for SQL execution, tracks applied migrations in a `_migrations` database table and JSON files, and supports dependency checking.

## Key Classes

### MigrationRunner

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `()` | Initialises empty completed list with `threading.Lock` |
| `run` | `(migration, direction=UP) -> MigrationResult` | Executes steps sequentially; stops on first `False` return; thread-safe completed tracking |
| `rollback` | `(migration) -> MigrationResult` | Delegates to `run` with `direction=DOWN` |
| `get_completed` | `() -> list[str]` | Returns list of completed migration IDs |
| `is_completed` | `(migration_id: str) -> bool` | Checks if a migration has been completed |

### DataMigrator

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `()` | Initialises empty transformer list |
| `add_transformer` | `(transformer: DataTransformer) -> DataMigrator` | Appends transformer; returns self for chaining |
| `migrate` | `(data: list[dict]) -> list[dict]` | Applies `CompositeTransformer` to each record |
| `migrate_single` | `(record: dict) -> dict` | Applies `CompositeTransformer` to one record |

### MigrationManager

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `(database_url, migrations_dir)` | Creates `DatabaseConnector`, initialises `_migrations` tracking table in database |
| `create_migration` | `(name, description, up_sql, down_sql, dependencies) -> dict` | Writes migration JSON file with UUID, timestamp, SQL, and dependency list |
| `apply_migration` | `(migration_id, dry_run=False) -> dict` | Checks dependencies, executes `up_sql` (or previews if `dry_run`), records in tracking table |
| `rollback_migration` | `(migration_id) -> dict` | Executes `down_sql`, removes from tracking table |
| `load_migrations_from_directory` | `() -> list[dict]` | Reads all JSON files from `migrations_dir` |
| `apply_pending_migrations` | `(dry_run=False) -> list[dict]` | Applies all unapplied migrations in order |
| `get_applied_migrations` | `() -> list[dict]` | Queries `_migrations` table for applied migration records |

### DatabaseConnector

| Method | Signature | Behaviour |
|--------|-----------|-----------|
| `__init__` | `(database_url: str)` | Parses URL scheme (`sqlite`, `postgresql`, `mysql`); establishes connection |
| `execute` | `(sql, params) -> list` | Executes single SQL statement; returns fetched rows |
| `execute_script` | `(sql_script: str) -> None` | Splits script on `;` and executes each statement |
| `close` | `() -> None` | Closes underlying database connection |

## Data Models

### MigrationStep

Fields: `id` (str), `name` (str), `description` (str), `up_fn` (Callable | None), `down_fn` (Callable | None), `dependencies` (list[str]).

### MigrationResult

Fields: `migration_id` (str), `status` (MigrationStatus), `started_at` (datetime), `completed_at` (datetime | None), `steps_completed` (int), `steps_total` (int), `error` (str | None). Properties: `progress` (float 0.0-1.0), `duration_seconds` (float).

### MigrationStatus (Enum)

`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `ROLLED_BACK`

### MigrationDirection (Enum)

`UP`, `DOWN`

### Transformer Classes

| Class | Constructor | `transform` Behaviour |
|-------|------------|----------------------|
| `FieldRenameTransformer` | `(mapping: dict[str, str])` | Renames dict keys per mapping; unmapped keys pass through |
| `FieldTypeTransformer` | `(conversions: dict[str, type])` | Casts field values to target types; logs warning on failure |
| `CompositeTransformer` | `(transformers: list[DataTransformer])` | Applies transformers in sequence |

## Dependencies

- **Standard library**: `threading`, `datetime`, `json`, `uuid`, `pathlib`, `sqlite3`
- **Internal**: `codomyrmex.exceptions.CodomyrmexError`, `codomyrmex.logging_monitoring`
- **Optional external**: `psycopg2` (PostgreSQL), `pymysql` (MySQL) -- imported at call time, not at module import

## Constraints

- `MigrationRunner` and `MigrationManager` are independent systems; they do not share state or tracking.
- `DatabaseConnector.execute_script` splits on `;` which may break on SQL containing semicolons in string literals.
- `MigrationManager` dependency checking is linear (checks each dependency is in applied set); circular dependencies are not detected.
- `DataMigrator` creates a new `CompositeTransformer` instance per `migrate` / `migrate_single` call.

## Error Handling

- `MigrationRunner` catches all exceptions during step execution and sets `MigrationResult.status = FAILED` with the error message.
- `FieldTypeTransformer` logs `ValueError` / `TypeError` as warnings and leaves the field unchanged.
- `MigrationManager` raises `CodomyrmexError` for missing dependencies, already-applied migrations, and database failures.
- `DatabaseConnector` raises `ValueError` for unsupported database URL schemes.
