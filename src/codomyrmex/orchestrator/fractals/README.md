# Fractals Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

A recursive agentic task orchestrator integrated directly into `codomyrmex.orchestrator`.
The Fractals engine receives a high-level task descriptions, grows a self-similar task dependency tree using autonomous LLM logic (`classify` and `decompose`), and then executes the atomic leaf tasks discretely inside isolated git `.worktrees`.

## Architecture

```text
               [Task Node]
              /           \
        [Composite]     [Composite]
        /         \          |
   [Atomic]    [Atomic]   [Atomic]
```

- **PLANNER:** Uses GPT (via `codomyrmex.agents.llm_client`) to intelligently split the task graph.
- **WORKSPACE:** Maps leaves directly to discrete `git worktree` instances to avoid cross-agent code collision during concurrent execution.
- **EXECUTOR:** Spawns sub-agents into the worktree scopes and retrieves patches/responses seamlessly.

## Integration

The module is exposed natively within the system as:

1. An **MCP Tool**: `orchestrate_fractal_task(task_description: str, max_depth: int)`
2. A **Skill**: `Recursive Agentic Task Orchestration (Fractals)`

## Zero-Mock Compliant

This module is 100% Zero-Mock tested. Test executions (`test_workspace.py`) interact directly with the local POSIX filesystem and shell environments to ensure real-world capability metrics are accurate.
