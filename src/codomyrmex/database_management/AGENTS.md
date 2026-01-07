# Codomyrmex Agents — src/codomyrmex/database_management

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Database operations including database connection management, query execution, schema management, migration handling, backup and restore, and performance monitoring. Provides unified interface for database operations across different database backends.

## Active Components
- `API_SPECIFICATION.md` – Detailed API specification
- `README.md` – Project file
- `SECURITY.md` – Security considerations
- `SPEC.md` – Project file
- `__init__.py` – Module exports and public API
- `backup_manager.py` – Backup and restore management
- `db_manager.py` – Database connection and query management
- `migration_manager.py` – Database migration management
- `performance_monitor.py` – Database performance monitoring
- `schema_generator.py` – Schema generation

## Key Classes and Functions

### DatabaseManager (`db_manager.py`)
- `DatabaseManager(connection_string: str)` – Database connection and query management
- `execute_query(query: str, params: dict = None) -> list` – Execute query
- `execute_transaction(queries: list[dict]) -> bool` – Execute transaction
- `get_connection() -> Connection` – Get database connection
- `close_connection() -> None` – Close database connection

### MigrationManager (`migration_manager.py`)
- `MigrationManager()` – Database migration management
- `run_migration(migration_file: str) -> bool` – Run migration
- `rollback_migration(migration_id: str) -> bool` – Rollback migration
- `get_migration_status() -> MigrationStatus` – Get migration status
- `list_migrations() -> list[Migration]` – List available migrations

### SchemaManager (`schema_generator.py`)
- `SchemaManager()` – Schema generation and management
- `generate_schema(model: type) -> dict` – Generate schema from model
- `create_table(schema: dict) -> bool` – Create table from schema
- `alter_table(table: str, changes: dict) -> bool` – Alter table schema
- `get_schema(table: str) -> dict` – Get table schema

### BackupManager (`backup_manager.py`)
- `BackupManager()` – Backup and restore management
- `create_backup(database: str, output_path: str) -> str` – Create database backup
- `restore_backup(backup_path: str, database: str) -> bool` – Restore from backup
- `list_backups(database: str) -> list[BackupRecord]` – List available backups

### PerformanceMonitor (`performance_monitor.py`)
- `PerformanceMonitor()` – Database performance monitoring
- `monitor_query_performance(query: str) -> PerformanceMetrics` – Monitor query performance
- `analyze_slow_queries(threshold: float = 1.0) -> list[SlowQuery]` – Analyze slow queries
- `get_database_stats() -> DatabaseStats` – Get database statistics

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../README.md) - Main project documentation