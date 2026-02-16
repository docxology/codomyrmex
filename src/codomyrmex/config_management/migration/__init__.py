"""Configuration migration for version upgrades and field changes.

Provides automatic migration of configuration files between versions,
with support for field renaming, value transformations, and custom
migration logic.
"""

from .config_migrator import (
    ConfigMigrator,
    MigrationAction,
    MigrationResult,
    MigrationRule,
    create_database_migration_rules,
    create_logging_migration_rules,
    migrate_config,
)

__all__ = [
    "ConfigMigrator",
    "MigrationAction",
    "MigrationResult",
    "MigrationRule",
    "create_database_migration_rules",
    "create_logging_migration_rules",
    "migrate_config",
]
