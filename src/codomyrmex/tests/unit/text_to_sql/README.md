# Text-to-SQL Tests

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `text_to_sql` module. Covers SQL validation (safe/dangerous queries), SQL generation from natural language (count, aggregation, limit), and schema matching (table/column matching, confidence).

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestSQLValidator` | Safe SELECT/COUNT, dangerous DROP/DELETE/UPDATE/INSERT/TRUNCATE/ALTER/CREATE, missing SELECT/FROM |
| `TestSQLGeneration` | Count/avg/max/min/sum queries, limit, tables_used, semicolon, SQLResult type |
| `TestSchemaMatching` | Users/orders table matching, column-based confidence boosting, empty schema |

## Test Structure

```
tests/unit/text_to_sql/
    __init__.py
    test_text_to_sql.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/text_to_sql/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/text_to_sql/ --cov=src/codomyrmex/text_to_sql -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../text_to_sql/README.md)
- [All Tests](../README.md)
