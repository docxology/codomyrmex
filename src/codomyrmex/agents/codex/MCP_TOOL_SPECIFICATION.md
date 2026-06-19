# codex — MCP Tool Specification

## Overview

Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `codex`.

## Tool: `codex_execute`

Single-turn execution against the Codex API via `CodexClient`.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `prompt` | string | Yes | — | Natural-language query |
| `timeout` | integer | No | `120` | API timeout (seconds) |

**Returns:** `status`, `content`, `error`, `metadata`.

## Tool: `codex_access_status`

Read-only Codex access probe for MCP, skills, trust, Hermes, Codex client, and
dispatch readiness.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| none | - | - | - | No input parameters |

**Returns:** `status`, `repo_root`, `surfaces`, `surface_statuses`, `dispatch`,
and `entrypoints`.

## Tool: `codex_dispatch_catalog`

Read-only catalog of multiagent dispatch surfaces and safety classifications.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| none | - | - | - | No input parameters |

**Returns:** `dispatchers` and `summary`. Dispatch entries are classified as
`read_only`, `dry_run`, or `side_effectful`.

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
