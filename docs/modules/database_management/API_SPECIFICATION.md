# Database Management - API Specification

## Introduction

This API specification documents the programmatic interfaces for the Database Management module of Codomyrmex. The module provides comprehensive database management, migration, and administration capabilities for the Codomyrmex ecosystem, supporting SQLite, PostgreSQL, and MySQL databases with unified interfaces.

## Functions

### Function: `manage_databases(database_url: str | None = None) -> DatabaseManager`

- **Description**: Create and return a `DatabaseManager` instance for database administration. If a `database_url` is provided, automatically connects to the database.
- **Parameters**:
    - `database_url` (str | None, optional): Database connection URL. If provided, connects automatically. Supported formats: `sqlite:///path/to/db.sqlite`, `postgresql://user:pass@host:port/database`, `mysql://user:pass@host:port/database`.
- **Return Value**: `DatabaseManager` instance ready for use.
- **Errors**: Raises `CodomyrmexError` for unsupported database URLs or connection failures.

### Function: `run_migrations(migration_dir: str, database_url: str, direction: str = "up") -> dict[str, Any]`

- **Description**: Run database migrations. Loads migration files from the specified directory and applies or rolls back migrations.
- **Parameters**:
    - `migration_dir` (str): Directory containing migration JSON files.
    - `database_url` (str): Database connection URL.
    - `direction` (str, optional): Migration direction (`"up"` to apply pending, `"down"` to rollback latest). Default: `"up"`.
- **Return Value**:
    ```python
    # For direction="up":
    {
        "direction": "up",
        "migrations_processed": int,
        "successful": int,
        "failed": int,
        "success": bool,
        "results": [
            {
                "migration_id": str,
                "success": bool,
                "execution_time": float,
                "error_message": str | None
            }
        ]
    }

    # For direction="down":
    {
        "direction": "down",
        "migrations_processed": int,
        "success": bool,
        "result": {
            "migration_id": str,
            "success": bool,
            "execution_time": float,
            "error_message": str | None
        }
    }
    ```
- **Errors**: Raises `CodomyrmexError` for invalid migration direction, database connection failures, or migration execution failures.

### Function: `backup_database(database_name: str, database_url: str | None = None, backup_type: str = "full", compression: str = "gzip") -> BackupResult`

- **Description**: Convenience function to create a database backup. Creates a `BackupManager` and performs the backup.
- **Parameters**:
    - `database_name` (str): Name identifying the database being backed up.
    - `database_url` (str | None, optional): Database connection URL.
    - `backup_type` (str, optional): Backup type (`"full"`, `"incremental"`, `"differential"`). Default: `"full"`.
    - `compression` (str, optional): Compression method (`"gzip"`, `"none"`). Default: `"gzip"`.
- **Return Value**: `BackupResult` dataclass with fields: `backup_id`, `success`, `duration`, `file_size_mb`, `error_message`, `warnings`, `checksum`.
- **Errors**: Raises `CodomyrmexError` for missing database URL, unsupported database types, or backup failures.

### Function: `monitor_database(database_name: str, workspace_dir: str | None = None) -> dict[str, Any]`

- **Description**: Monitor database performance by analyzing recorded metrics.
- **Parameters**:
    - `database_name` (str): Name of the database to monitor.
    - `workspace_dir` (str | None, optional): Workspace directory for performance data storage.
- **Return Value**: Database performance analysis dictionary from `DatabasePerformanceMonitor.analyze_database_performance()`.
- **Errors**: Returns empty analysis if no metrics are found.

### Function: `optimize_database(database_name: str, workspace_dir: str | None = None) -> dict[str, Any]`

- **Description**: Generate a comprehensive performance report with optimization recommendations.
- **Parameters**:
    - `database_name` (str): Name of the database to optimize.
    - `workspace_dir` (str | None, optional): Workspace directory for performance data storage.
- **Return Value**: Performance report dictionary from `DatabasePerformanceMonitor.get_performance_report()` including query performance, database performance, alerts, and recommendations.
- **Errors**: Returns report with empty sections if no metrics are found.

### Function: `generate_schema(models: list[Any], output_dir: str) -> dict[str, Any]`

- **Description**: Generate database schema from model definitions (dictionary-based or SQLAlchemy models).
- **Parameters**:
    - `models` (list[Any]): List of model definitions. Supports dictionaries with `"name"`, `"columns"`, `"indexes"` keys, or SQLAlchemy model classes with `__table__` and `__tablename__` attributes.
    - `output_dir` (str): Output directory for generated schema files.
- **Return Value**:
    ```python
    {
        "tables_generated": int,
        "schema_file": str,  # Path to generated SQL file
        "message": str
    }
    ```
- **Errors**: Raises `CodomyrmexError` for unsupported model formats or schema generation failures.

## Data Structures

### DatabaseConnection (dataclass)
Database connection information:
```python
@dataclass
class DatabaseConnection:
    name: str
    db_type: DatabaseType        # SQLITE, POSTGRESQL, MYSQL, MONGODB, REDIS, CUSTOM
    database: str
    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    connection_pool_size: int = 10
    connection_timeout: int = 30
    max_retries: int = 3
    connection_string: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
```

Key methods: `get_connection_string()`, `connect()`, `disconnect()`, `execute_query(query, params)`, `get_database_info()`, `health_check()`.

### Migration (dataclass)
Database migration definition:
```python
@dataclass
class Migration:
    id: str
    name: str
    description: str
    sql: str
    rollback_sql: str | None = None
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: datetime | None = None
    status: str = "pending"       # "pending", "applied", "failed", "rolled_back"
    checksum: str = ""            # Auto-calculated SHA256 of sql
```

### MigrationResult (dataclass)
Result of a migration execution:
```python
@dataclass
class MigrationResult:
    migration_id: str
    success: bool
    execution_time: float
    error_message: str | None = None
    rows_affected: int = 0
    statements_executed: int = 0
```

### Backup (dataclass)
Database backup information:
```python
@dataclass
class Backup:
    backup_id: str
    database_name: str
    database_type: str
    backup_type: str
    file_path: str
    size_mb: float
    created_at: datetime
    compression: str = "none"
    encryption: bool = False
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

### BackupResult (dataclass)
Result of a backup operation:
```python
@dataclass
class BackupResult:
    backup_id: str
    success: bool
    duration: float
    file_size_mb: float
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)
    checksum: str | None = None
```

### DatabaseMetrics (dataclass)
Database performance metrics:
```python
@dataclass
class DatabaseMetrics:
    database_name: str
    timestamp: datetime
    connections_active: int
    connections_idle: int
    queries_per_second: float
    average_query_time_ms: float
    cache_hit_ratio: float
    disk_io_mb: float
```

### SchemaDefinition (dataclass)
Complete database schema definition:
```python
@dataclass
class SchemaDefinition:
    name: str
    version: str
    tables: list[SchemaTable] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
```

Key methods: `to_sql(dialect)`, `to_dict()`.

## Manager Classes

### DatabaseManager
Database connection and query management:
```python
class DatabaseManager:
    def __init__(self, database_url: str | None = None): ...
    def add_connection(self, connection: DatabaseConnection): ...
    def remove_connection(self, name: str): ...
    def get_connection(self, name: str) -> DatabaseConnection | None: ...
    def list_connections(self) -> list[str]: ...
    def connect_all(self): ...
    def disconnect_all(self): ...
    def execute_query(self, name: str, query: str, params: tuple | None = None) -> list[dict[str, Any]]: ...
    def health_check_all(self) -> dict[str, dict[str, Any]]: ...
    def get_database_stats(self) -> dict[str, Any]: ...
    def connect(self, database_url: str | None = None) -> DatabaseConnection: ...
    def disconnect(self, connection_id: str | None = None): ...
    def execute(self, query: str, params: tuple | None = None) -> QueryResult: ...
    def execute_many(self, query: str, params_list: list[tuple]) -> QueryResult: ...
    def transaction(self) -> Generator[None, None, None]: ...  # context manager
    def get_tables(self) -> list[str]: ...
    def get_table_info(self, table_name: str) -> list[dict[str, Any]]: ...
```

### MigrationManager
Database migration management system:
```python
class MigrationManager:
    def __init__(self, workspace_dir: str | None = None, database_url: str | None = None): ...
    def set_database_url(self, database_url: str): ...
    def load_migrations_from_directory(self): ...
    def create_migration(self, name: str, description: str, sql: str, rollback_sql: str | None = None, dependencies: list[str] | None = None) -> Migration: ...
    def apply_migration(self, migration_id: str, dry_run: bool = False) -> MigrationResult: ...
    def rollback_migration(self, migration_id: str) -> MigrationResult: ...
    def get_migration_status(self, migration_id: str) -> dict[str, Any] | None: ...
    def list_migrations(self) -> list[dict[str, Any]]: ...
    def get_pending_migrations(self) -> list[Migration]: ...
    def apply_pending_migrations(self) -> list[MigrationResult]: ...
    def close(self): ...
```

### BackupManager
Database backup and restore management:
```python
class BackupManager:
    def __init__(self, workspace_dir: str | None = None, database_url: str | None = None): ...
    def create_backup(self, database_name: str, database_url: str | None = None, backup_type: str = "full", compression: str = "gzip", include_schema: bool = True, include_data: bool = True) -> BackupResult: ...
    def list_backups(self, database_name: str | None = None) -> list[dict[str, Any]]: ...
    def delete_backup(self, backup_id: str) -> bool: ...
```

### SchemaGenerator
Database schema generation and management:
```python
class SchemaGenerator:
    def __init__(self, workspace_dir: str | None = None, dialect: str = "sqlite"): ...
    def create_table(self, table: SchemaTable) -> str: ...
    def create_table_from_dict(self, table_def: dict[str, Any]) -> str: ...
    def generate_migration(self, name: str, description: str, changes: dict[str, Any]) -> SchemaMigration: ...
    def compare_schemas(self, current_schema: dict, target_schema: dict) -> dict[str, Any]: ...
    def get_schema_drift_report(self, current_schema: dict, target_schema: dict) -> dict[str, Any]: ...
    def generate_schema_sql(self, schema_name: str, version: str = "1.0.0") -> str: ...
    def export_schema(self, output_path: str, format: str = "sql") -> str: ...
    def list_migrations(self) -> list[dict[str, Any]]: ...
```

## Error Handling

All functions use `CodomyrmexError` (from `codomyrmex.exceptions`) as the base error class. Standard Python exceptions (`ValueError`, `OSError`) are also raised where appropriate.

## Integration Patterns

### With Project Orchestration
```python
from codomyrmex.database_management import run_migrations

# Run database migrations
result = run_migrations(
    migration_dir="migrations/",
    database_url="sqlite:///app.db",
    direction="up"
)
```

### With Performance Monitoring
```python
from codomyrmex.database_management import monitor_database, optimize_database

# Monitor database performance
metrics = monitor_database("my_database", workspace_dir="./perf_data")

# Generate optimization report
report = optimize_database("my_database", workspace_dir="./perf_data")
```

### Database Management
```python
from codomyrmex.database_management import manage_databases

# Create a database manager with auto-connect
manager = manage_databases("sqlite:///app.db")

# Execute queries
result = manager.execute("SELECT * FROM users WHERE active = ?", (True,))
print(f"Found {result.row_count} active users")

# Clean up
manager.disconnect()
```

## Security Considerations

- **Connection Security**: PostgreSQL and MySQL connections support SSL/TLS
- **Authentication**: Credentials are parsed from connection URLs
- **Safe SQL Execution**: Parameterized queries prevent SQL injection
- **Backup Security**: Backups support compression and checksum verification
- **Migration Safety**: Migration rollback capabilities and dependency validation

## Performance Characteristics

- **Connection Pooling**: Configurable pool size per connection
- **Query Execution**: Parameterized queries with timing metrics
- **Backup Efficiency**: Supports gzip compression for backups
- **Migration Performance**: Batch migration execution with progress tracking
- **Monitoring Overhead**: In-memory metrics with configurable retention limits


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
