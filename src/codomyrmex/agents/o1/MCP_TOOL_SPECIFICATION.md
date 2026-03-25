# o1 — MCP Tool Specification

## Overview

Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `o1`.

## Tool: `o1_execute`

Single-turn execution against the OpenAI o1-style reasoning API.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `prompt` | string | Yes | — | Natural-language query |
| `timeout` | integer | No | `120` | API timeout (seconds) |

**Returns:** `status`, `content`, `error`, `metadata`.

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
