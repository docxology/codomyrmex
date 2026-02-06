# Database Management Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Database connections, migrations, pooling, and query execution.

## Key Features

- **Connection Pool** — Efficient connection management
- **Migrations** — Schema migration support
- **Query Builder** — Safe query construction
- **Transactions** — Transaction management

## Quick Start

```python
from codomyrmex.database_management import DatabaseConnection

db = DatabaseConnection(
    host="localhost", database="mydb", pool_size=10
)

with db.connection() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = ?", [1])
```

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This file |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/database_management/](../../../src/codomyrmex/database_management/)
- **Parent**: [Modules](../README.md)
