# pai_pm — MCP Tool Specification

## Overview

PAI Project Manager server lifecycle and HTTP API. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `pai_pm`.

## Tools

| Tool | Summary |
|:-----|:--------|
| `pai_pm_start` | Start Bun/TS server subprocess |
| `pai_pm_stop` | SIGTERM server |
| `pai_pm_health` | GET `/api/health` |
| `pai_pm_get_state` | Dashboard state (missions, projects, tasks) |
| `pai_pm_get_awareness` | Agent awareness payload |
| `pai_pm_dispatch` | POST dispatch execute |

### `pai_pm_dispatch`

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `action` | string | Yes | — | Action name |
| `backend` | string | No | `""` | e.g. `claude`, `gemini` |
| `model` | string | No | `""` | Model override |
| `context` | object | No | `null` | Extra context |

## Navigation

- **Parent**: [codomyrmex](../README.md)
- **Project root**: [README.md](../../../README.md)
