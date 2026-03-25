# fractals (orchestrator) — MCP Tool Specification

## Overview

Fractal task decomposition with isolated git worktrees per leaf. Tools are auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `orchestrator`.

## Tool: `orchestrate_fractal_task`

### Purpose

Decompose a high-level task into a tree of composite and atomic nodes, then execute each leaf in its own git worktree using the selected provider.

### Parameters

| Name | Type | Required | Default | Description |
|:-----|:-----|:---------|:--------|:------------|
| `task_description` | string | Yes | — | Natural-language goal to plan and execute |
| `max_depth` | integer | No | `3` | Maximum recursion depth for decomposition |
| `provider` | string | No | `"claude"` | `"claude"` (Anthropic CLI in worktree) or `"codomyrmex"` (internal agent) |

### Behavior

1. Builds and plans a task tree from `task_description` up to `max_depth`.
2. Creates workspace directory `tempfile.gettempdir() / "fractals_workspace"`, initializes a git repo if needed.
3. For each leaf, creates `<workspace_path>/.worktrees/<task_id>/` and runs the provider.
4. Leaf execution is sequential in the current implementation.

### Success response

| Field | Type | Description |
|:------|:-----|:------------|
| `status` | string | `"success"` |
| `task` | string | Original `task_description` |
| `workspace_path` | string | Absolute path to the fractal workspace |
| `final_tree_status` | string | Root tree status value |
| `subtasks_executed` | integer | Number of leaf tasks |
| `results` | array | Per-leaf `{ "task", "status" }` entries (`"success"` or `"error"`) |

### Error response

| Field | Type | Description |
|:------|:-----|:------------|
| `status` | string | `"error"` |
| `message` | string | Failure description |

## Related

- [`SKILL.md`](SKILL.md) — Agent-facing skill narrative
- [`workspace.py`](workspace.py), [`executor.py`](executor.py)

## Navigation

- **Parent module**: [Orchestrator MCP spec](../MCP_TOOL_SPECIFICATION.md)
- **Project root**: [README.md](../../../../README.md)
