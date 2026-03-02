# Text-to-SQL -- PAI Integration

## Phase Mapping

| PAI Phase | Tool | Usage |
|-----------|------|-------|
| OBSERVE | `text_to_sql_validate` | Check SQL safety before execution |
| THINK | `text_to_sql_generate` | Convert user questions to structured queries |
| BUILD | `text_to_sql_generate` | Generate data retrieval queries |
| VERIFY | `text_to_sql_validate` | Validate generated SQL before execution |

## MCP Tools

| Tool Name | Category | Description |
|-----------|----------|-------------|
| `text_to_sql_generate` | text_to_sql | Generate SQL from natural language question |
| `text_to_sql_validate` | text_to_sql | Validate SQL for safety and basic syntax |

## Agent Providers

This module does not provide agent types. It provides query generation tools that agents consume.

## Dependencies

- Foundation: `model_context_protocol` (for `@mcp_tool` decorator)
- External: None (pure Python stdlib)
