# Text-to-SQL -- Agent Integration Guide

## Module Purpose

Converts natural language questions into SQL queries using schema-aware pattern matching. Enables AI agents to query databases without writing raw SQL.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `text_to_sql_generate` | Generate SQL from natural language question | `question: str`, `tables: dict`, `primary_keys: dict` | `{query, confidence, tables_used, valid, error}` |
| `text_to_sql_validate` | Validate SQL for safety and syntax | `sql: str` | `{valid, error}` |

## Agent Use Cases

### Natural Language Querying
An agent can convert user questions into SQL without requiring the user to know SQL syntax.

### SQL Safety Checking
Use `text_to_sql_validate` to verify that generated or user-provided SQL is safe (no DROP, DELETE, etc.).

### Schema-Aware Generation
Providing the schema ensures generated SQL references real tables and columns.

## Example Agent Workflow

```
1. Agent receives: "Show me the top 5 orders by total"
2. Agent calls: text_to_sql_generate("top 5 orders by total", {"orders": ["id", "total", "user_id"]})
3. Response: {"query": "SELECT total FROM orders ORDER BY total LIMIT 5;", "valid": true}
4. Agent executes query or presents it for review
```
