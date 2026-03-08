# Agent Guidelines - Database Management

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: October 2026

## Module Overview

Database connections, migrations, backups, performance monitoring, and query execution.

## Key Classes

- **DatabaseManager** — Core orchestrator for multiple database connections.
- **DatabaseConnection** — Individual connection handler and low-level executor.
- **MigrationManager** — Schema migrations and version tracking.
- **SchemaGenerator** — Programmatic schema definition and DDL generation.
- **BackupManager** — Database snapshots and recovery.
- **DatabasePerformanceMonitor** — Real-time metrics and query analysis.

## Agent Instructions

1. **Use DatabaseManager** — Prefer `DatabaseManager` for managing one or more connections.
2. **Parameterize queries** — Never use string concatenation for SQL queries to prevent SQL injection.
3. **Transaction scope** — Use `with manager.transaction():` for atomic operations.
4. **SQLite first** — For local development and examples, use SQLite with `sqlite:///path/to/db.sqlite`.
5. **Handle Results** — Always check `QueryResult.success` and use `.to_dict_list()` for easy data access.

## Common Patterns

```python
from codomyrmex.database_management import (
    manage_databases, DatabaseType, DatabaseConnection
)

# Initialize manager
manager = manage_databases()

# Add a connection
conn = DatabaseConnection(name="main", db_type=DatabaseType.SQLITE, database="app.db")
manager.add_connection(conn)

# Safe query execution
result = manager.execute("SELECT * FROM users WHERE id = ?", (1,))
if result.success:
    users = result.to_dict_list()

# Using transactions
with manager.transaction():
    manager.execute("INSERT INTO logs (msg) VALUES (?)", ("Action performed",))
```

## Testing Patterns

```python
# Zero-mock testing with SQLite in-memory
manager = manage_databases("sqlite:///:memory:")
manager.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, val TEXT)")
manager.execute("INSERT INTO test (val) VALUES (?)", ("data",))
result = manager.execute("SELECT * FROM test")
assert result.row_count == 1
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Database operations, schema management, query execution, connection pooling | TRUSTED |
| **Architect** | Read + Design | Schema design review, query optimization analysis, database architecture | OBSERVED |
| **QATester** | Validation | Query correctness, schema validation, data integrity verification | OBSERVED |


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/database_management.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/database_management.cursorrules)
