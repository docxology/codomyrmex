# gemini — MCP Tool Specification

## Overview

Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `gemini`.

## Tool: `gemini_execute`

Single-turn execution against the Gemini API.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `prompt` | string | Yes | — | Natural-language query |
| `timeout` | integer | No | `120` | API timeout (seconds) |

**Returns:** `status`, `content`, `error`, `metadata`.

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
