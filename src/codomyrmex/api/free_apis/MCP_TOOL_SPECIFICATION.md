# free_apis — MCP Tool Specification

## Overview

Public free-API registry and HTTP client. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `api`.

## Tool: `free_api_list_categories`

No parameters. **Returns:** `status`, `category_count`, `categories` (`{name, count}`), `source`.

## Tool: `free_api_search`

| Parameter | Type | Default | Description |
|:----------|:-----|:--------|:------------|
| `query` | string | `""` | Substring on name/description |
| `category` | string | `""` | Exact category filter |
| `auth_type` | string | `""` | e.g. `apiKey`, `OAuth` |
| `https_only` | boolean | `false` | HTTPS-only entries |

**Returns:** `status`, `count`, `entries`.

## Tool: `free_api_call`

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `url` | string | Yes | — | Full URL |
| `method` | string | No | `GET` | HTTP method |
| `params` | string | No | `""` | `k=v,k2=v2` |
| `headers` | string | No | `""` | `K: V; K2: V2` |
| `timeout` | integer | No | `10` | Seconds |

**Returns:** `status`, `status_code`, `body_text`, `headers`.

## Navigation

- **Parent**: [api](../README.md)
- **Project root**: [README.md](../../../../README.md)
