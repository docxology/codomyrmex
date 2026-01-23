# Codomyrmex Agents — src/codomyrmex/database_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The Database Management module provides comprehensive database administration, migration management, backup/recovery, and performance monitoring capabilities for the Codomyrmex ecosystem. It supports multiple database types (SQLite, PostgreSQL, MySQL), handles schema migrations with rollback support, provides automated backup and restore functionality, and includes performance monitoring and optimization tools.

## Active Components

### Database Management

- `db_manager.py` - Database connection and query management
  - Key Classes: `DatabaseManager`, `DatabaseConnection`, `QueryResult`
  - Key Functions: `connect_database()`, `execute_query()`, `manage_databases()`
  - Key Enums: `DatabaseType`

### Migration Management

- `migration_manager.py` - Database migration and schema versioning
  - Key Classes: `MigrationManager`, `Migration`, `MigrationResult`, `DatabaseConnector`
  - Key Functions: `run_migrations()`, `create_migration()`, `apply_migration()`, `rollback_migration()`

### Backup Management

- `backup_manager.py` - Database backup and recovery
  - Key Classes: `BackupManager`, `Backup`, `BackupResult`
  - Key Functions: `backup_database()`, `create_backup()`, `list_backups()`, `delete_backup()`

### Performance Monitoring

- `performance_monitor.py` - Database performance and health monitoring
  - Key Classes: `DatabaseMonitor`, `DatabaseMetrics`
  - Key Functions: `monitor_database()`, `optimize_database()`

### Schema Generation

- `schema_generator.py` - Database schema generation and management
  - Key Classes: `SchemaGenerator`, `SchemaDefinition`
  - Key Functions: `generate_schema()`

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `DatabaseManager` | db_manager | Multi-connection database management |
| `DatabaseConnection` | db_manager | Database connection configuration and operations |
| `QueryResult` | db_manager | Query execution result with rows and columns |
| `MigrationManager` | migration_manager | Migration tracking and execution system |
| `Migration` | migration_manager | Migration definition with SQL and rollback |
| `DatabaseConnector` | migration_manager | Database connection handling for migrations |
| `BackupManager` | backup_manager | Backup creation and management system |
| `Backup` | backup_manager | Backup metadata and file information |
| `run_migrations()` | migration_manager | Run database migrations (up or down) |
| `backup_database()` | backup_manager | Create database backup with compression |
| `manage_databases()` | db_manager | Create DatabaseManager for administration |
| `execute()` | db_manager | Execute SQL query with parameters |
| `transaction()` | db_manager | Context manager for database transactions |

## Operating Contracts

1. **Logging**: All database operations use `logging_monitoring` for structured logging
2. **Connection Management**: Supports multiple named database connections
3. **Migration Tracking**: Migrations tracked in `_migrations` table with checksums
4. **Migration Dependencies**: Migrations can declare dependencies on other migrations
5. **Backup Compression**: Backups support gzip compression
6. **Backup Checksums**: SHA256 checksums calculated for backup verification
7. **Database Support**: Native support for SQLite, PostgreSQL (pg_dump), MySQL (mysqldump)
8. **Transaction Safety**: Migration and backup operations use proper transaction handling
9. **Error Recovery**: Failed migrations automatically rollback

## Integration Points

- **logging_monitoring** - All database operations log via centralized logger
- **security** - Database security and compliance auditing
- **config_management** - Database configuration management
- **performance** - Database performance monitoring

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| config_management | [../config_management/AGENTS.md](../config_management/AGENTS.md) | Configuration management |
| security | [../security/AGENTS.md](../security/AGENTS.md) | Security and compliance |
| performance | [../performance/AGENTS.md](../performance/AGENTS.md) | Performance monitoring |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| (none) | This module has no subdirectories |

### Related Documentation

- [README.md](README.md) - User documentation
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
- [SECURITY.md](SECURITY.md) - Security considerations
