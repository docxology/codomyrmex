# cost_management — MCP Tool Specification

## Overview

Budget and cost summaries. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `cost_management`.

## Tool: `get_cost_summary`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `period_str` | string | `MONTHLY` | `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY`, or `ALL` |

**Returns:** `total`, `by_category`, `by_resource`, `period`, or error envelope.

## Tool: `check_budgets`

No parameters. **Returns:** `budgets` (utilization list), `alerts`.

## FastMCP registration

[`register_mcp_tools`](mcp_tools.py) also exposes `mcp_get_cost_summary` and `mcp_check_budgets` wrapping the same functions.

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
