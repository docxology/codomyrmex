# relations/crm — MCP Tool Specification

## Overview

In-process CRM contacts and interactions. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `relations_crm`.

## Tool: `crm_add_contact`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `name` | string | Yes | Display name |
| `email` | string | Yes | Email |
| `tags` | array | No | Categorical tags |
| `metadata` | object | No | Arbitrary KV |

## Tool: `crm_search_contacts`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `query` | string | Yes | Name/email/tag substring |

## Tool: `crm_add_interaction`

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `contact_id` | string | Yes | Contact id |
| `type` | string | Yes | e.g. `email`, `call` |
| `notes` | string | Yes | Free text |

## Navigation

- **Parent**: [relations](../README.md)
- **Project root**: [README.md](../../../../README.md)
