# jules — MCP Tool Specification

## Overview

Jules CLI and swarm dispatch. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `jules`.

## Tool: `jules_help`

CLI availability and help text.

**Returns:** `status`, `available`, `help_text`, or `message` on error.

## Tool: `jules_execute`

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `prompt` | string | Yes | — | Task description |
| `repo` | string | Yes | — | GitHub slug or local path |
| `parallel` | integer | No | `1` | Parallel agents |
| `timeout` | integer | No | `120` | Subprocess timeout (s) |

**Returns:** `status`, `content`, `error`, `metadata`.

## Tool: `jules_dispatch_swarm`

Parse `TODO.md` open items and dispatch Jules batches.

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `todo_path` | string | Yes | — | Path to TODO.md |
| `repo` | string | Yes | — | GitHub slug or path |
| `parallel` | integer | No | `100` | `--parallel` per batch |
| `batch_size` | integer | No | `10` | Tasks per invocation |
| `priority_filter` | string | No | `""` | Section keyword filter |
| `dry_run` | boolean | No | `false` | Parse only |

**Returns:** `status`, counts, `tasks` / `responses` per implementation.

## Navigation

- **Parent**: [agents](../README.md)
- **Project root**: [README.md](../../../../README.md)
