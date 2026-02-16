"""Backward-compatible shim -- delegates to config_management.migration.config_migrator."""

from .migration.config_migrator import (  # noqa: F401
    ConfigMigrator,
    MigrationAction,
    MigrationResult,
    MigrationRule,
    create_database_migration_rules,
    create_logging_migration_rules,
    migrate_config,
)
