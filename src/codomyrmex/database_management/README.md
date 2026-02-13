# database_management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Database administration module providing connection management, schema generation, migration execution, backup/recovery, and performance monitoring. The `DatabaseManager` handles core database operations through `DatabaseConnection` configurations. Supports automated schema generation via `SchemaGenerator`, versioned migrations through `MigrationManager`, backup scheduling with `BackupManager`, and real-time performance monitoring via `DatabaseMonitor`. Includes submodules for connection pooling, replication, sharding, and auditing.


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Submodules

- **`connections`** -- Connection pooling and connection lifecycle management
- **`replication`** -- Database replication and synchronization
- **`sharding`** -- Database sharding strategies and shard management
- **`audit`** -- Database security and compliance auditing

### Database Management

- **`DatabaseManager`** -- Core class for database administration operations
- **`manage_databases()`** -- Comprehensive database administration entry point
- **`DatabaseConnection`** -- Connection configuration with host, port, credentials, and options

### Migration Management

- **`MigrationManager`** -- Manages versioned database migrations with up/down support
- **`run_migrations()`** -- Execute pending migrations in order
- **`Migration`** -- Individual migration definition with version and SQL statements

### Backup Management

- **`BackupManager`** -- Automated database backup and recovery orchestration
- **`backup_database()`** -- Create a database backup with configurable strategy
- **`Backup`** -- Backup configuration and status tracking

### Performance Monitoring

- **`DatabaseMonitor`** -- Real-time database health and performance monitoring
- **`monitor_database()`** -- Start monitoring database metrics
- **`optimize_database()`** -- Apply performance tuning recommendations
- **`DatabaseMetrics`** -- Performance metrics container (query latency, connections, throughput)

### Schema Generation

- **`SchemaGenerator`** -- Generates database schemas from definitions
- **`generate_schema()`** -- Generate DDL from a schema definition
- **`SchemaDefinition`** -- Schema definition with tables, columns, and constraints

## Directory Contents

- `__init__.py` - Module entry point aggregating all submodule exports
- `db_manager.py` - `DatabaseManager` and `DatabaseConnection` core operations
- `migration_manager.py` - `MigrationManager` and `Migration` for versioned migrations
- `backup_manager.py` - `BackupManager` and `Backup` for backup/recovery
- `performance_monitor.py` - `DatabaseMonitor` and `DatabaseMetrics` for monitoring
- `schema_generator.py` - `SchemaGenerator` and `SchemaDefinition` for DDL generation
- `connections/` - Connection pooling and lifecycle management
- `replication/` - Database replication configuration and sync
- `sharding/` - Sharding strategy definitions and shard routing
- `audit/` - Database security auditing and compliance

## Quick Start

```python
from codomyrmex.database_management import DatabaseManager, DatabaseConnection, MigrationManager

# Create a connection and execute queries
conn = DatabaseConnection(name="app_db", db_type="sqlite", database="app.db")
conn.connect()
results = conn.execute_query("SELECT * FROM users WHERE active = ?", (True,))

# Manage multiple connections
manager = DatabaseManager()
manager.add_connection(conn)
manager.execute_query("app_db", "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, message TEXT)")
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k database_management -v
```

## Navigation

- **Full Documentation**: [docs/modules/database_management/](../../../docs/modules/database_management/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
