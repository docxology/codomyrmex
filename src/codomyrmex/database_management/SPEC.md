# database_management - Functional Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: October 2026

## Purpose

Provides a unified, safe, and observable interface for database operations, including persistence, schema evolution, and performance tracking.

## Interface Contracts

### `DatabaseManager`
- `connect(url: str)`: Connects to a database.
- `execute(query: str, params: tuple)`: Executes a query and returns a `QueryResult`.
- `transaction()`: Returns a context manager for atomic operations.
- `get_tables()`: Lists tables in the current database.
- `get_table_info(table_name: str)`: Returns metadata for a specific table.

### `QueryResult`
- `success: bool`: True if the query executed without errors.
- `rows: list[tuple]`: Raw row data.
- `columns: list[str]`: Column names.
- `row_count: int`: Number of affected rows or returned rows.
- `to_dict_list()`: Converts rows to a list of dictionaries.
- `valid: bool`: Alias for `success` for Unified Streamline compatibility.

### `MigrationManager`
- `apply_pending_migrations()`: Runs all unapplied migrations.
- `create_migration(name, sql, rollback_sql)`: Generates a new migration file.

### `DatabasePerformanceMonitor`
- `record_query_metrics(query_hash, metrics)`: Logs performance data.
- `get_performance_report(database_name)`: Generates a summary of database health.

## Design Principles

1. **Safety**: All queries must be parameterized.
2. **Observability**: Performance metrics and health checks are integrated.
3. **Consistency**: `QueryResult` provides a standard way to handle data across different database types.
4. **Reliability**: Transactions and migrations ensure data integrity during changes.

## Testing Strategy

- **Zero-Mock Policy**: All unit tests for this module must interact with a real SQLite database (often in-memory) to verify actual SQL execution and database behavior.
- **Integration Tests**: Verify cross-database compatibility where drivers are available.
