# Text to SQL -- MCP Tool Specification

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

This document defines the MCP tools exposed by the `text_to_sql` module.
These tools are auto-discovered by the PAI MCP bridge via the `@mcp_tool` decorator
in `mcp_tools.py` and surfaced as part of the ~303 dynamic tools available to Claude.

## Auto-Discovery

| Property | Value |
|----------|-------|
| Discovery method | `@mcp_tool` decorator scan |
| Namespace | `text_to_sql` |
| Trust default | Safe |
| PAI bridge | `src/codomyrmex/agents/pai/mcp/` |

## Tool Reference

### `text_to_sql_generate`

**Description**: Generate a SQL query from a natural language question.
**Trust Level**: Safe
**Category**: generation

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `question` | `str` | Yes | -- | Natural language question about the data |
| `tables` | `dict` | Yes | -- | Schema dict mapping table names to column lists, e.g. `{"users": ["id", "name", "email"]}` |
| `primary_keys` | `dict` | No | `None` | Optional dict mapping table names to primary key columns |

**Returns**: `dict` -- Dictionary with query (str), confidence (float), tables_used (list), valid (bool), error (str or None).

**Example**:
```python
from codomyrmex.text_to_sql.mcp_tools import text_to_sql_generate

result = text_to_sql_generate(
    question="How many users signed up in 2025?",
    tables={"users": ["id", "name", "email", "created_at"]},
    primary_keys={"users": "id"},
)
```

---

### `text_to_sql_validate`

**Description**: Validate a SQL query for safety and basic syntax.
**Trust Level**: Safe
**Category**: analysis

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sql` | `str` | Yes | -- | SQL query string to validate |

**Returns**: `dict` -- Dictionary with valid (bool) and error (str or None).

**Example**:
```python
from codomyrmex.text_to_sql.mcp_tools import text_to_sql_validate

result = text_to_sql_validate(sql="SELECT COUNT(*) FROM users WHERE created_at > '2025-01-01'")
```

## Integration Notes

- **Auto-discovered**: Yes (via `@mcp_tool` in `mcp_tools.py`)
- **Trust Gateway**: All tools are safe -- query generation and validation only, no execution
- **PAI Phases**: BUILD (query generation), VERIFY (query validation)
- **Dependencies**: Internal `engine` module (SQLSchema, TextToSQLEngine, SQLValidator)

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
