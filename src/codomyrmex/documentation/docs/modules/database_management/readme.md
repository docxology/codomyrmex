# Database Management Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: October 2026

## Overview

The Database Management module is a comprehensive suite for database administration in the Codomyrmex ecosystem. It provides unified interfaces for connection management, schema generation, versioned migrations, backup/recovery, and performance monitoring.

## Key Features

- **Unified DatabaseManager**: Manage multiple heterogeneous database connections through a single interface.
- **SQLite, PostgreSQL, MySQL Support**: Broad support for popular relational databases (SQLite prioritized for embedded use).
- **Safe Query Execution**: Built-in support for parameterized queries and result handling via `QueryResult`.
- **Atomic Transactions**: Context managers for robust transaction handling.
- **Automated Migrations**: Version-controlled schema changes with rollback support.
- **Performance Monitoring**: Track query execution times, active connections, and identify slow queries.
- **Snapshots & Recovery**: Easily backup and restore databases.

## Installation

```bash
uv add codomyrmex
```

## Quick Start

```python
from codomyrmex.database_management import manage_databases

# Connect to an in-memory SQLite database
db = manage_databases("sqlite:///:memory:")

# Create a table
db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, value REAL)")

# Insert data
db.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("Widget", 19.99))

# Query data
result = db.execute("SELECT * FROM items WHERE value > ?", (10.0,))
for row in result.to_dict_list():
    print(f"Item: {row['name']}, Price: {row['value']}")

# Get table info
info = db.get_table_info("items")
print(f"Table columns: {[col['name'] for col in info]}")
```

## Submodules

- **`connections`**: Connection pooling and lifecycle management.
- **`migration`**: Versioned database migrations.
- **`backup`**: Automated backup and recovery.
- **`performance_monitor`**: Real-time health and performance metrics.
- **`schema_generator`**: DDL generation from code definitions.

## Testing

Run tests using pytest:

```bash
pytest src/codomyrmex/tests/unit/database_management/
```

Tests use real SQLite databases (zero-mock) to ensure reliable validation of database operations.

## Navigation

- [API Specification](SPEC.md)
- [Agent Guidelines](AGENTS.md)
- [MCP Tool Specification](MCP_TOOL_SPECIFICATION.md)
