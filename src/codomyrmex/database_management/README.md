# Database Management

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `database_management` module provides a comprehensive abstraction layer for interacting with persistent storage systems in Codomyrmex. It handles connection pooling, schema migrations, automated backups, and performance monitoring. By decoupling database operations from business logic, it allows for easy switching of backends (SQLite, PostgreSQL) and consistent data governance.

## Key Features
- **Connection Management**: The `db_manager.py` handles connection lifecycles and pooling.
- **Migration System**: The `migration_manager.py` applies schema changes deterministically.
- **Automated Backups**: The `backup_manager.py` schedules and executes database dumps.
- **Schema Helper**: `schema_generator.py` assists in defining data models code-first.
- **Performance**: `performance_monitor.py` tracks query latency and bottlenecks.

## Quick Start

```python
from codomyrmex.database_management.db_manager import DatabaseManager
from codomyrmex.database_management.migration_manager import MigrationManager

# Initialize connection
db = DatabaseManager(connection_string="sqlite:///data.db")
db.connect()

# Run migrations
migrator = MigrationManager(db)
migrator.apply_pending()

# Execute query
results = db.execute("SELECT * FROM agents WHERE active = 1")
```

## Module Structure

- `db_manager.py`: Core connection and transaction logic.
- `migration_manager.py`: Version control for database schemas.
- `backup_manager.py`: Utilities for data persistence and recovery.
- `schema_generator.py`: Tools for DDL generation.
- `performance_monitor.py`: Ops tooling for database health.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Security Policy**: [SECURITY.md](SECURITY.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
