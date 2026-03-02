# Codomyrmex Agents -- src/codomyrmex/config_management/migration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides configuration migration between versions with support for field renaming, moving, value transformation, addition, removal, splitting, merging, and custom transformations. Handles automatic migration path discovery across a linear version chain.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `config_migrator.py` | `ConfigMigrator` | Main migrator engine managing rules, version ordering, and path finding |
| `config_migrator.py` | `ConfigMigrator.add_migration_rule` | Registers a `MigrationRule` for a specific version transition |
| `config_migrator.py` | `ConfigMigrator.migrate_config` | Migrates config from one version to another by applying chained rules |
| `config_migrator.py` | `ConfigMigrator.get_migration_path` | Finds step-by-step path between two versions |
| `config_migrator.py` | `ConfigMigrator.validate_migration` | Checks compatibility of a config with a target version |
| `config_migrator.py` | `ConfigMigrator.register_migration` | Registers a custom callable as a migration function |
| `config_migrator.py` | `MigrationRule` | Dataclass defining a single migration action with conditions and transforms |
| `config_migrator.py` | `MigrationResult` | Dataclass capturing success, applied rules, warnings, errors, and backup |
| `config_migrator.py` | `MigrationAction` | Enum of 8 action types: RENAME, MOVE, TRANSFORM, ADD, REMOVE, SPLIT, MERGE, CUSTOM |
| `config_migrator.py` | `create_logging_migration_rules` | Predefined rules for logging config upgrades |
| `config_migrator.py` | `create_database_migration_rules` | Predefined rules for database config upgrades |
| `config_migrator.py` | `migrate_config` | Convenience function applying common migration rules |

## Operating Contracts

- Migration paths follow a linear version ordering based on rule registration order.
- Configs are deep-copied before migration; a backup is preserved in `MigrationResult.backup_config`.
- Nested field paths use dot notation (e.g., `connection_pool.connection_timeout`).
- Rules with a `condition` callable are skipped when the condition returns `False`.
- If any rule fails during migration, the result is marked `success=False` and remaining rules are skipped.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring.core.logger_config`
- **Used by**: Config management core, deployment workflows, version upgrade pipelines

## Navigation

- **Parent**: [../AGENTS.md](../AGENTS.md)
- **Root**: [../../../../README.md](../../../../README.md)
