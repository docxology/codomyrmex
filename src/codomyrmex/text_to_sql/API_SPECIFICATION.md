# Text to SQL - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `text_to_sql` module provides a schema-aware engine for translating natural language questions into SQL queries. Uses database schema metadata to generate syntactically correct and semantically meaningful SQL.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `TextToSQLEngine` | Main engine translating natural language to SQL via schema context |
| `SQLSchema` | Database schema representation (tables, columns, types, relationships) |
| `SQLResult` | Result container with generated SQL, explanation, and confidence score |

## 3. Usage Example

```python
from codomyrmex.text_to_sql import TextToSQLEngine, SQLSchema

schema = SQLSchema.from_tables({
    "users": {"id": "INT", "name": "TEXT", "email": "TEXT"},
    "orders": {"id": "INT", "user_id": "INT", "total": "DECIMAL"},
})

engine = TextToSQLEngine(schema)
result = engine.translate("How many orders does each user have?")
print(result.sql)
# SELECT u.name, COUNT(o.id) FROM users u JOIN orders o ON u.id = o.user_id GROUP BY u.name
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
