---
name: Recursive Agentic Task Orchestration (Fractals)
description: A powerful orchestration skill for breaking down high-level objectives into hierarchical task graphs and resolving them through isolated multi-agent execution in dedicated worktrees.
category: Orchestration
version: 1.0.0
---

# Fractals orchestrator

## Overview

The `fractals` integration provides a self-similar, LLM-steered recursion flow that maps high-level goals into task trees with `atomic` leaves. Each leaf runs in its own **git worktree** under a dedicated workspace directory so agents stay isolated.

## Capabilities context

Use the `orchestrate_fractal_task` MCP tool when the user gives a large composite goal (for example a full-stack build or a broad refactor) and single-shot agent runs are unlikely to succeed.

Phases:

1. **PLAN**: Tasks are classified as composite or atomic up to `max_depth` (default 3).
2. **EXECUTE**: For each leaf, a worktree is created and the chosen provider runs the task there.

## Workspace layout (actual behavior)

The MCP entrypoint [`mcp_tools.orchestrate_fractal_task`](mcp_tools.py) uses a workspace directory:

- **Path**: `tempfile.gettempdir() / "fractals_workspace"` (for example `/tmp/fractals_workspace` on Unix).
- **Git root**: That directory is initialized as its own repository if needed.
- **Leaf worktrees**: `WorkspaceManager` creates `<workspace_path>/.worktrees/<task_id>/` per leaf (see [`workspace.py`](workspace.py)).

Do not merge these worktrees by hand unless you understand the fractal run; treat them as disposable sandboxes for that orchestration run.

## Providers

- **`provider="claude"`** (default): runs the Anthropic Claude CLI in each worktree (`executor.py`).
- **`provider="codomyrmex"`**: uses the internal codomyrmex agent path in the same worktree.

## Best practices

- Set `max_depth` deliberately; excessive depth adds coordination overhead.
- Expect sequential leaf execution in the current MCP wrapper (concurrency may be added at async boundaries).

## Related

- [`mcp_tools.py`](mcp_tools.py) — `orchestrate_fractal_task`
- [`executor.py`](executor.py), [`planner.py`](planner.py), [`models.py`](models.py)
