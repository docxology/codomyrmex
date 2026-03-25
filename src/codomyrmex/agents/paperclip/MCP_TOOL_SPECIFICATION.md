# paperclip — MCP Tool Specification

## Overview

Paperclip CLI and REST API. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `paperclip`.

## Tools

### `paperclip_execute`

Heartbeat-style run via CLI client.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `prompt` | string | Yes | — | Directive context |
| `agent_id` | string | No | `null` | Agent ID |
| `timeout` | integer | No | `120` | CLI timeout (s) |

**Returns:** `status`, `content`, `error`, `metadata`.

### `paperclip_list_companies`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `base_url` | string | `http://localhost:3100` | API base |
| `api_key` | string | `null` | Bearer token |

### `paperclip_create_issue`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `company_id` | string | Yes | Company ID |
| `title` | string | Yes | Issue title |
| `description` | string | No | Body |
| `base_url` | string | No | Default localhost |
| `api_key` | string | No | Bearer token |

### `paperclip_trigger_heartbeat`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `agent_id` | string | Yes | Agent ID |
| `base_url` | string | No | API base |
| `api_key` | string | No | Bearer token |

### `paperclip_doctor`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `repair` | boolean | `false` | Auto-repair |

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
