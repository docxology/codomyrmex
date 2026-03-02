# Migration — Agent Coordination

## Purpose

Provides database migration and data transformation capabilities for AI agents, supporting step-based schema migrations with rollback, record-level data transformations, and SQL-based migration management across SQLite, PostgreSQL, and MySQL.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `MigrationStep` | Single migration step with `up_fn` / `down_fn` callables and dependency list |
| `models.py` | `Migration` | Migration definition grouping ordered `MigrationStep` instances with `add_step` / `add_simple_step` |
| `models.py` | `MigrationResult` | Result dataclass with `status`, `progress`, `duration_seconds`, and `to_dict` serialization |
| `models.py` | `MigrationStatus` | Enum: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `ROLLED_BACK` |
| `models.py` | `DataTransformer` | Abstract base class for record-level data transformations |
| `models.py` | `FieldRenameTransformer` | Renames dictionary keys according to a mapping |
| `models.py` | `FieldTypeTransformer` | Converts field values to target types with logged warnings on failure |
| `models.py` | `CompositeTransformer` | Chains multiple `DataTransformer` instances in sequence |
| `executor.py` | `MigrationRunner` | Thread-safe migration executor with step-by-step `run` and `rollback` |
| `executor.py` | `DataMigrator` | Pipeline runner applying `DataTransformer` chains to record lists |
| `migration_manager.py` | `DatabaseConnector` | URL-based database connection for SQLite, PostgreSQL, and MySQL with `execute` and `execute_script` |
| `migration_manager.py` | `MigrationManager` | Full lifecycle manager: `create_migration`, `apply_migration`, `rollback_migration`, `apply_pending_migrations`, with tracking table and JSON persistence |
| `migration_manager.py` | `run_migrations` | Convenience function wrapping `MigrationManager.apply_pending_migrations` |

## Operating Contracts

- Agents SHOULD use `MigrationManager` for SQL-based database migrations and `MigrationRunner` for callable-based step migrations; the two systems are independent.
- `MigrationRunner.run` executes steps sequentially; if any step returns `False`, the migration status is set to `FAILED` and execution stops.
- `MigrationRunner.rollback` runs steps in reverse order using each step's `down_fn`.
- `MigrationManager` creates a `_migrations` tracking table in the target database to record applied migrations.
- `MigrationManager` persists migration metadata to JSON files in the `migrations_dir`; agents should not modify these files directly.
- `DataMigrator` applies transformers to each record independently; field conversion failures are logged as warnings but do not halt the pipeline.
- `MigrationManager.apply_migration` supports `dry_run=True` for previewing SQL without executing.
- Dependency checking in `MigrationManager` verifies all listed dependencies are already applied before running a migration.

## Integration Points

- **logging_monitoring**: `MigrationManager` and `FieldTypeTransformer` use the codomyrmex structured logger.
- **exceptions**: `MigrationManager` raises `CodomyrmexError` on failures.
- **database_management/lineage**: Migration steps can be registered as transformations in the lineage graph.

## Navigation

- **Parent**: [database_management/README.md](../README.md)
- **Siblings**: [backup/](../backup/), [lineage/](../lineage/)
- **RASP**: [README.md](README.md) | **AGENTS.md** | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
