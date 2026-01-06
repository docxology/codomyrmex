# Codomyrmex Agents — src/codomyrmex/database_management

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Database Management Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Service Layer module providing database management, migration, and administration capabilities for the Codomyrmex platform. This module handles database operations, schema management, migrations, backups, and performance monitoring across multiple database systems.

The database_management module serves as the data persistence and management layer, ensuring reliable and efficient database operations throughout the platform.

## Module Overview

### Key Capabilities
- **Database Administration**: Connection management and database operations
- **Migration Management**: Schema migrations and version control
- **Backup and Recovery**: Automated database backup and restoration
- **Performance Monitoring**: Database performance analysis and optimization
- **Schema Generation**: Automated schema creation from data models
- **Multi-Database Support**: Support for various database systems

### Key Features
- Multi-database system support (PostgreSQL, MySQL, SQLite, etc.)
- Automated migration tracking and rollback
- Comprehensive backup strategies with compression
- Real-time performance monitoring and alerting
- Schema generation from application models
- Database security and access control

## Function Signatures

### Database Management Functions

```python
def manage_databases() -> DatabaseManager
```

Get database manager instance for database administration operations.

**Returns:** `DatabaseManager` - Database management interface

### Migration Management Functions

```python
def run_migrations(
    migration_dir: str,
    database_url: str,
    target_revision: Optional[str] = None,
    dry_run: bool = False,
) -> dict[str, Any]
```

Execute database migrations from migration files.

**Parameters:**
- `migration_dir` (str): Directory containing migration files
- `database_url` (str): Database connection URL
- `target_revision` (Optional[str]): Target migration revision. If None, migrates to latest
- `dry_run` (bool): If True, show what would be migrated without executing

**Returns:** `dict[str, Any]` - Migration execution results and status

### Backup and Recovery Functions

```python
def backup_database(
    database_name: str,
    database_url: Optional[str] = None,
    backup_type: str = "full",
    compression: str = "gzip"
) -> BackupResult
```

Create a database backup with specified options.

**Parameters:**
- `database_name` (str): Name for the backup operation
- `database_url` (Optional[str]): Database connection URL. If None, uses configured default
- `backup_type` (str): Type of backup ("full", "incremental", "differential"). Defaults to "full"
- `compression` (str): Compression method ("gzip", "bz2", "none"). Defaults to "gzip"

**Returns:** `BackupResult` - Backup operation result with file path and metadata

### Performance Monitoring Functions

```python
def monitor_database(database_name: str, workspace_dir: Optional[str] = None) -> dict[str, Any]
```

Monitor database performance and health metrics.

**Parameters:**
- `database_name` (str): Name of the database to monitor
- `workspace_dir` (Optional[str]): Directory for storing monitoring data

**Returns:** `dict[str, Any]` - Database performance metrics and health status

```python
def optimize_database(database_name: str, workspace_dir: Optional[str] = None) -> dict[str, Any]
```

Analyze and optimize database performance.

**Parameters:**
- `database_name` (str): Name of the database to optimize
- `workspace_dir` (Optional[str]): Directory for storing optimization reports

**Returns:** `dict[str, Any]` - Optimization recommendations and applied changes

### Schema Generation Functions

```python
def generate_schema(models: list[Any], output_dir: str) -> dict[str, Any]
```

Generate database schema from data models.

**Parameters:**
- `models` (list[Any]): List of data model classes
- `output_dir` (str): Directory to save generated schema files

**Returns:** `dict[str, Any]` - Schema generation results and file paths

```python
def generate_schema_from_models(models: list[Any], output_dir: str) -> dict[str, Any]
```

Generate database schema and migration files from application models.

**Parameters:**
- `models` (list[Any]): List of application data models
- `output_dir` (str): Output directory for schema and migration files

**Returns:** `dict[str, Any]` - Schema and migration generation results

## Data Structures

### DatabaseConnection
```python
class DatabaseConnection:
    url: str
    driver: str
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_config: Optional[dict[str, Any]]

    def connect(self) -> Any
    def test_connection(self) -> bool
    def get_connection_info(self) -> dict[str, Any]
    def close(self) -> None
```

Database connection configuration and management.

### Migration
```python
class Migration:
    revision: str
    description: str
    upgrade_sql: str
    downgrade_sql: str
    dependencies: list[str]
    created_at: datetime

    def apply(self, connection: DatabaseConnection) -> bool
    def rollback(self, connection: DatabaseConnection) -> bool
    def validate(self) -> list[str]
    def to_dict(self) -> dict[str, Any]
```

Database migration definition and tracking.

### Backup
```python
class Backup:
    name: str
    database_name: str
    backup_type: str
    compression: str
    file_path: str
    size_bytes: int
    checksum: str
    created_at: datetime
    status: str

    def restore(self, target_database: str) -> bool
    def validate(self) -> bool
    def get_info(self) -> dict[str, Any]
    def delete(self) -> bool
```

Database backup configuration and status tracking.

### DatabaseMetrics
```python
class DatabaseMetrics:
    connections_active: int
    connections_idle: int
    query_count: int
    slow_queries: list[dict[str, Any]]
    table_sizes: dict[str, int]
    index_usage: dict[str, float]
    cache_hit_ratio: float
    lock_waits: int

    def to_dict(self) -> dict[str, Any]
    def get_summary(self) -> dict[str, Any]
    def detect_anomalies(self) -> list[str]
```

Database performance and health metrics.

### SchemaDefinition
```python
class SchemaDefinition:
    tables: dict[str, dict[str, Any]]
    indexes: dict[str, dict[str, Any]]
    constraints: dict[str, dict[str, Any]]
    relationships: list[dict[str, Any]]

    def to_sql(self, dialect: str = "postgresql") -> str
    def validate(self) -> list[str]
    def diff(self, other: SchemaDefinition) -> list[str]
    def apply_to_database(self, connection: DatabaseConnection) -> bool
```

Database schema definition and management.

### DatabaseManager
```python
class DatabaseManager:
    def __init__(self, config_path: str = None)

    def connect(self, connection_string: str) -> DatabaseConnection
    def disconnect(self, connection: DatabaseConnection) -> None
    def execute_query(self, query: str, params: dict = None, connection: DatabaseConnection = None) -> list
    def get_database_info(self, connection: DatabaseConnection) -> dict[str, Any]
    def list_databases(self) -> list[str]
    def create_database(self, name: str, config: dict = None) -> bool
    def drop_database(self, name: str) -> bool
```

Main database management and administration class.

### MigrationManager
```python
class MigrationManager:
    def __init__(self, migration_dir: str, database_url: str)

    def get_current_revision(self) -> str
    def get_pending_migrations(self) -> list[Migration]
    def upgrade(self, target_revision: str = None) -> dict[str, Any]
    def downgrade(self, target_revision: str) -> dict[str, Any]
    def create_migration(self, description: str) -> Migration
    def validate_migrations(self) -> list[str]
    def get_migration_history(self) -> list[dict[str, Any]]
```

Database migration management and execution.

### BackupManager
```python
class BackupManager:
    def __init__(self, config_path: str = None)

    def create_backup(self, database_name: str, backup_config: dict = None) -> BackupResult
    def restore_backup(self, backup_path: str, target_database: str) -> bool
    def list_backups(self, database_name: str = None) -> list[Backup]
    def validate_backup(self, backup_path: str) -> dict[str, Any]
    def delete_backup(self, backup_path: str) -> bool
    def schedule_backup(self, database_name: str, schedule: str) -> str
```

Database backup and recovery management.

### PerformanceMonitor
```python
class PerformanceMonitor:
    def __init__(self, database_url: str)

    def collect_metrics(self) -> DatabaseMetrics
    def analyze_performance(self) -> dict[str, Any]
    def get_slow_queries(self, limit: int = 10) -> list[dict[str, Any]]
    def suggest_optimizations(self) -> list[str]
    def monitor_query_performance(self, query: str) -> dict[str, Any]
    def generate_performance_report(self) -> str
```

Database performance monitoring and analysis.

### SchemaGenerator
```python
class SchemaGenerator:
    def __init__(self, dialect: str = "postgresql")

    def generate_from_models(self, models: list[Any]) -> SchemaDefinition
    def generate_migrations(self, current_schema: SchemaDefinition, target_schema: SchemaDefinition) -> list[Migration]
    def validate_schema(self, schema: SchemaDefinition) -> list[str]
    def export_schema(self, schema: SchemaDefinition, format: str = "sql") -> str
    def import_schema(self, schema_file: str) -> SchemaDefinition
```

Database schema generation and management.

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `db_manager.py` – Database connection and administration
- `migration_manager.py` – Database migration management
- `backup_manager.py` – Database backup and recovery operations
- `performance_monitor.py` – Database performance monitoring
- `schema_generator.py` – Database schema generation from models

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `SECURITY.md` – Security considerations for database operations


### Additional Files
- `SPEC.md` – Spec Md
- `__pycache__` –   Pycache  

## Operating Contracts

### Universal Database Protocols

All database operations within the Codomyrmex platform must:

1. **Data Integrity** - Database operations maintain data consistency and integrity
2. **Security First** - Database access is properly authenticated and authorized
3. **Performance Aware** - Database queries and operations are optimized
4. **Backup Ready** - Critical data is regularly backed up with recovery procedures
5. **Migration Safe** - Schema changes are tested and reversible

### Module-Specific Guidelines

#### Database Management
- Support multiple database systems with consistent interface
- Provide connection pooling and efficient resource usage
- Include error handling and logging
- Support database clustering and high availability

#### Migration Management
- Track migration versions and dependencies accurately
- Provide rollback capabilities for all migrations
- Include migration testing and validation
- Support branching and merging migration histories

#### Backup and Recovery
- Implement multiple backup strategies (full, incremental, differential)
- Provide point-in-time recovery capabilities
- Include backup validation and integrity checking
- Support automated backup scheduling

#### Performance Monitoring
- Monitor key performance indicators continuously
- Provide actionable optimization recommendations
- Include query performance analysis and indexing suggestions
- Support real-time alerting for performance issues

#### Schema Generation
- Generate database-agnostic schema definitions
- Support schema versioning and evolution
- Include data migration path generation
- Validate schema compatibility across database systems

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation