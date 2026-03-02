# Configuration Migration -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides automatic migration of configuration dictionaries between versions using a rule-based engine. Supports 8 migration action types with conditional execution, deep-copy safety, backup preservation, and linear version path discovery.

## Architecture

Rule-based migration engine. `ConfigMigrator` maintains a registry of `MigrationRule` objects keyed by `(from_version, to_version)` pairs. Migration executes by finding the shortest path through the version chain and applying rules sequentially. All configs are deep-copied before mutation.

## Key Classes

### `ConfigMigrator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | | `None` | Initializes empty rule registry and version ordering |
| `add_migration_rule` | `rule: MigrationRule` | `None` | Registers a rule for a specific version transition |
| `migrate_config` | `config: dict, from_version: str, to_version: str` | `MigrationResult` | Migrates config across version chain |
| `get_migration_path` | `from_version, to_version` | `list[tuple[str, str]]` | Finds step-by-step path through version chain |
| `validate_migration` | `config: dict, target_version: str` | `bool` | Checks if config is compatible with target version |
| `register_migration` | `from_version, to_version, migrator: Callable` | `None` | Registers a custom migration callable |

### `MigrationAction` (Enum)

8 actions: `RENAME_FIELD`, `MOVE_FIELD`, `TRANSFORM_VALUE`, `ADD_FIELD`, `REMOVE_FIELD`, `SPLIT_FIELD`, `MERGE_FIELDS`, `CUSTOM_TRANSFORM`

### `MigrationRule` (Dataclass)

Fields: `action`, `description`, `from_version`, `to_version`, `old_path`, `new_path`, `old_paths`, `new_value`, `transform_func`, `condition`

### `MigrationResult` (Dataclass)

Fields: `success`, `original_version`, `target_version`, `migrated_config`, `applied_rules`, `warnings`, `errors`, `backup_config`

### Predefined Rule Factories

| Function | Description |
|----------|-------------|
| `create_logging_migration_rules` | Rules for renaming `log_level` to `level`, uppercasing, adding format field |
| `create_database_migration_rules` | Rules for renaming `db_host`, moving connection settings, adding SSL mode |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`
- **External**: `copy` (stdlib), `collections.abc` (stdlib)

## Constraints

- Version path finding assumes linear version progression based on registration order.
- Nested field access uses dot notation (e.g., `connection_pool.connection_timeout`).
- Rules with a `condition` callable are skipped when the condition returns `False`.
- `SPLIT_FIELD` and `MERGE_FIELDS` actions are partially implemented (emit warnings).
- Zero-mock: real config transformation only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Individual rule failures are captured in `MigrationResult.errors` and halt further rule application.
- All errors are logged before propagation.
