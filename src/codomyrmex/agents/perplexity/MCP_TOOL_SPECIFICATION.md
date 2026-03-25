# perplexity — MCP Tool Specification

## Overview

Perplexity API chat. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `perplexity`.

## Tool: `perplexity_execute`

Single-turn query.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `prompt` | string | Yes | — | Natural-language query |
| `timeout` | integer | No | `120` | API timeout (s) |

**Returns:** `status`, `content`, `error`, `metadata`.

## Tool: `perplexity_ask`

Multi-turn messages.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `messages` | array[object] | Yes | — | Each with `role`, `content` |
| `timeout` | integer | No | `120` | API timeout (s) |

**Returns:** `status`, `content`, `error`, `metadata`.

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
