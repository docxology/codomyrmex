"""
Database Management Module for Codomyrmex.

The Database Management module provides comprehensive database management,
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

from .db_manager import (
    DatabaseManager,
    manage_databases,
    DatabaseConnection,
)

from .migration_manager import (
    MigrationManager,
    run_migrations,
    Migration,
)

from .backup_manager import (
    BackupManager,
    backup_database,
    Backup,
)

from .performance_monitor import (
    DatabaseMonitor,
    monitor_database,
    optimize_database,
    DatabaseMetrics,
)

from .schema_generator import (
    SchemaGenerator,
    generate_schema,
    SchemaDefinition,
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
