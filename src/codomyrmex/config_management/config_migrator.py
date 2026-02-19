# DEPRECATED(v0.2.0): Shim module. Import from config_management.migration.config_migrator instead. Will be removed in v0.3.0.
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
