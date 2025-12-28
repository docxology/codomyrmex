"""
Database Management Module for Codomyrmex.

The Database Management module provides database management,
migration, and administration capabilities for the Codomyrmex ecosystem.

Integration:
- Uses `logging_monitoring` for all logging (ensure `setup_logging()` is called in your main app).
- Integrates with `security_audit` for database security and compliance.
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
    DatabaseMonitor,
    monitor_database,
    optimize_database,
)
from .schema_generator import (
    SchemaDefinition,
    SchemaGenerator,
    generate_schema,
)

__all__ = [
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
    "DatabaseMonitor",
    "monitor_database",
    "optimize_database",
    "DatabaseMetrics",
    # Schema generation
    "SchemaGenerator",
    "generate_schema",
    "SchemaDefinition",
]
