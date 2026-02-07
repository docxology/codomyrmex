# Database Management Module — Agent Coordination

## Purpose

Database Management Module for Codomyrmex.

## Key Capabilities

- Database Management operations and management

## Agent Usage Patterns

```python
from codomyrmex.database_management import *

# Agent uses database management capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/database_management/](../../../src/codomyrmex/database_management/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`Backup`** — Database backup information.
- **`BackupResult`** — Result of a backup operation.
- **`BackupManager`** — Database backup and restore management system.
- **`DatabaseType`** — Supported database types.
- **`QueryResult`** — Result of a query execution.
- **`backup_database()`** — Convenience function to backup a database.
- **`connect_database()`** — Convenience function to connect to a database.
- **`execute_query()`** — Convenience function to execute a single query.
- **`manage_databases()`** — Create and return a DatabaseManager instance for database administration.

### Submodules

- `audit` — Audit
- `connections` — Connections
- `replication` — Replication
- `sharding` — Sharding

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k database_management -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
