# Agent Guidelines - Database Management

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Database connections, migrations, and query execution.

## Key Classes

- **DatabaseConnection** — Connection pooling
- **MigrationManager** — Schema migrations
- **QueryBuilder** — Safe query construction
- **TransactionManager** — Transaction handling

## Agent Instructions

1. **Use connection pool** — Don't create per-request
2. **Parameterize queries** — Never string concatenation
3. **Migrate safely** — Test migrations first
4. **Transaction scope** — Explicit transaction boundaries
5. **Close connections** — Use context managers

## Common Patterns

```python
from codomyrmex.database_management import (
    DatabaseConnection, QueryBuilder, MigrationManager
)

# Connection pooling
db = DatabaseConnection(
    host="localhost",
    database="mydb",
    pool_size=10
)

# Safe query execution
with db.connection() as conn:
    result = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        [user_id]
    )

# Query builder
query = QueryBuilder("users")
query.select("id", "name").where("active", True).limit(10)
result = db.execute(query.build())

# Migrations
migrations = MigrationManager(db)
migrations.migrate_up()
```

## Testing Patterns

```python
# Verify connection
db = DatabaseConnection(url="sqlite:///:memory:")
assert db.is_connected()

# Verify query builder
query = QueryBuilder("test")
query.select("*").where("id", 1)
sql, params = query.build()
assert "SELECT" in sql
assert 1 in params
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Database operations, schema management, query execution, connection pooling | TRUSTED |
| **Architect** | Read + Design | Schema design review, query optimization analysis, database architecture | OBSERVED |
| **QATester** | Validation | Query correctness, schema validation, data integrity verification | OBSERVED |

### Engineer Agent
**Use Cases**: Database operations during BUILD/EXECUTE, schema migrations, connection management.

### Architect Agent
**Use Cases**: Reviewing database schemas, analyzing query plans, designing data architecture.

### QATester Agent
**Use Cases**: Validating query correctness during VERIFY, testing schema migrations, data integrity checks.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
