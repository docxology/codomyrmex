# Text-to-SQL Engine Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides schema-aware natural language to SQL query generation. Accepts a database schema definition and converts natural language questions into SQL queries with confidence scoring and validation.

## Functional Requirements

1. Schema-aware SQL generation from natural language questions with table/column awareness
2. Confidence scoring for generated queries indicating translation certainty
3. SQL validation for safety (injection prevention) and basic syntax correctness


## Interface

```python
from codomyrmex.text_to_sql import TextToSQLEngine, SQLSchema, SQLResult

schema = SQLSchema(tables={"users": ["id", "name", "email"]}, primary_keys={"users": "id"})
engine = TextToSQLEngine(schema)
result = engine.generate("Show all users named Alice")
print(result.query, result.confidence, result.valid)
```

## Exports

TextToSQLEngine, SQLSchema, SQLResult

## Navigation

- [Source README](../../src/codomyrmex/text_to_sql/README.md) | [AGENTS.md](AGENTS.md)
