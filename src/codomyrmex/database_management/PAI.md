# Personal AI Infrastructure — Database Management Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Database Management module provides PAI integration for database operations.

## PAI Capabilities

### Database Connection

Connect to databases:

```python
from codomyrmex.database_management import DatabaseConnection

db = DatabaseConnection(
    host="localhost", database="mydb", pool_size=10
)

with db.connection() as conn:
    result = conn.execute("SELECT * FROM users")
```

### Migrations

Run database migrations:

```python
from codomyrmex.database_management import Migrator

migrator = Migrator(db)
migrator.migrate_to("v2.0.0")
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `DatabaseConnection` | Connect to DB |
| `Migrator` | Run migrations |
| `QueryBuilder` | Build queries |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
