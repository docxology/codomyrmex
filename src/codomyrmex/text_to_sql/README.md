# Text-to-SQL Engine

Schema-aware natural language to SQL query generation using pattern matching.

## Overview

The text_to_sql module converts natural language questions into SQL queries by matching question patterns against common SQL structures and resolving table/column references from a provided database schema. Pure Python implementation -- no LLM dependency.

## Quick Start

```python
from codomyrmex.text_to_sql import TextToSQLEngine, SQLSchema

schema = SQLSchema(
    tables={
        "users": ["id", "name", "email", "age"],
        "orders": ["id", "user_id", "total", "created_at"],
    },
    primary_keys={"users": "id", "orders": "id"},
)

engine = TextToSQLEngine(schema)

result = engine.generate("How many users are there?")
print(result.query)       # SELECT COUNT(*) FROM users;
print(result.confidence)  # 0.7
print(result.valid)       # True
```

### Supported Patterns

- **Count**: "how many", "count", "number of"
- **Aggregations**: "average", "maximum", "minimum", "sum", "total"
- **Filtering**: "where column = value"
- **Ordering**: "order by", "sort by"
- **Limits**: "top N", "first N", "limit N"

### SQL Validation

```python
from codomyrmex.text_to_sql.engine import SQLValidator

valid, error = SQLValidator.validate("SELECT * FROM users;")
print(valid)  # True

valid, error = SQLValidator.validate("DROP TABLE users;")
print(valid, error)  # False, "Dangerous SQL keyword 'DROP' not allowed"
```

## Safety

The validator blocks dangerous keywords: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE. Only SELECT queries are generated.

## Dependencies

- Python standard library only (re, dataclasses)
