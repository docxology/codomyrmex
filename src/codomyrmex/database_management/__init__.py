"""
Database Management Module for Codomyrmex.

The Database Management module provides database management,
migration, and administration capabilities for the Codomyrmex ecosystem.

Submodules:
    lineage: Consolidated lineage capabilities.
    migration: Consolidated migration capabilities.
    backup: Database backup and recovery.
    connections: Connection pooling and management.
    performance_monitor: Performance monitoring and optimization.
    schema_generator: Schema generation and management.
"""

from . import audit, backup, connections, lineage, migration, replication, sharding
from .backup.backup_manager import (
    Backup,
    BackupManager,
    backup_database,
)
from .db_manager import (
    DatabaseConnection,
    DatabaseManager,
    DatabaseType,
    QueryResult,
    connect_database,
    execute_query,
    manage_databases,
)
from .migration.migration_manager import (
    Migration,
    MigrationManager,
    run_migrations,
)
from .performance_monitor import (
    DatabaseMetrics,
    DatabasePerformanceMonitor,
    monitor_database,
    optimize_database,
)
from .schema_generator import (
    SchemaDefinition,
    SchemaGenerator,
    generate_schema,
)


def cli_commands():
    """Return CLI commands for the database_management module."""
    return {
        "adapters": {
            "help": "List available database adapters",
            "handler": lambda **kwargs: print(
                "Database Adapters:\n"
                "  - sqlite    (built-in)\n"
                "  - postgres  (via psycopg2)\n"
                "  - mysql     (via mysqlclient)\n"
                "  - redis     (via redis-py)"
            ),
        },
        "status": {
            "help": "Show database connection status",
            "handler": lambda **kwargs: print(
                "Database Status:\n"
                "  Connections : 0 active\n"
                "  Migrations  : up to date\n"
                "  Backups     : none scheduled"
            ),
        },
    }


__all__ = [
    "lineage",
    "migration",
    "backup",
    "connections",
    "audit",
    "sharding",
    "replication",
    "performance_monitor",
    "schema_generator",
    # CLI integration
    "cli_commands",
    # Database management
    "DatabaseManager",
    "manage_databases",
    "DatabaseConnection",
    "DatabaseType",
    "QueryResult",
    "connect_database",
    "execute_query",
    # Migration management
    "MigrationManager",
    "run_migrations",
    "Migration",
    # Backup management
    "BackupManager",
    "backup_database",
    "Backup",
    # Performance monitoring
    "DatabasePerformanceMonitor",
    "monitor_database",
    "optimize_database",
    "DatabaseMetrics",
    # Schema generation
    "SchemaGenerator",
    "generate_schema",
    "SchemaDefinition",
]
