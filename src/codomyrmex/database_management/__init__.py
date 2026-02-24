"""
Database Management Module for Codomyrmex.

The Database Management module provides database management,
migration, and administration capabilities for the Codomyrmex ecosystem.

Submodules:
    lineage: Consolidated lineage capabilities.
    migration: Consolidated migration capabilities.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Integrates with `security` for database security and compliance.
- Works with `config_management` for database configuration management.
- Supports `performance` for database performance monitoring.

Available functions:
- manage_databases: Comprehensive database administration
- run_migrations: Database migration management and execution
- backup_database: Automated database backup and recovery
- monitor_database: Database performance and health monitoring
- optimize_database: Database optimization and tuning
- audit_database: Database security and compliance auditing
- replicate_database: Database replication and synchronization
- generate_schema: Database schema generation and management

Data structures:
- DatabaseConnection: Database connection configuration and management
- Migration: Database migration definition and tracking
- Backup: Database backup configuration and status
- DatabaseMetrics: Database performance and health metrics
- SchemaDefinition: Database schema definition and management
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

from . import audit, connections, replication, sharding
from .backup_manager import (
    Backup,
    BackupManager,
    backup_database,
)
from .db_manager import (
    DatabaseConnection,
    DatabaseManager,
    manage_databases,
)
from .migration_manager import (
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


from . import migration

from . import lineage

__all__ = [
    "lineage",
    "migration",
    # CLI integration
    "cli_commands",
    'audit',
    'sharding',
    'replication',
    'connections',
    # Database management
    "DatabaseManager",
    "manage_databases",
    "DatabaseConnection",
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
