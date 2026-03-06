---
name: Recursive Agentic Task Orchestration (Fractals)
description: A powerful orchestration skill for breaking down high-level objectives into hierarchical task graphs and resolving them through isolated multi-agent execution in dedicated worktrees.
category: Orchestration
version: 1.0.0
---

# 🌀 Fractals Orchestrator

## Overview

The `fractals` integration provides a robust, self-similar, LLM-steered recursion engine that maps high-level abstract goals into concrete tree graphs of executable `atomic` leaves. The engine spins up individual git `worktrees` per leaf node, executing agents inside completely isolated scopes—thereby resolving complex goals without context pollution.

## Capabilities Context

Use this skill via the `orchestrate_fractal_task` MCP Tool when you are presented with a massive, composite goal from the User (e.g. "Build a full stack web application", "Refactor the entire billing module") and standard single-shot agent patterns will fail.

The logic operates in two phases:

1. **PLAN**: The LLM autonomously classifies tasks as `composite` or `atomic` safely scaling up to a `max_depth`. Composites are strictly decoupled.
2. **EXECUTE**: Isolated `.worktrees` are appended. Granular agents solve their leaf task.

## Best Practices

- **Isolation Boundaries**: Do not attempt to merge the git worktrees manually. The system operates inside `~/.gemini/tmp` equivalent local scopes to sandbox execution.
- **Provider Switching**: Default execution passes through Anthropics CLI, but internal `codomyrmex` agents serve as fallback providers dynamically.
- **Decomposition Overload**: Set `max_depth` intentionally (default: 3). Over-decomposition creates administrative burden; let the classifier properly halt recursion at `atomic` boundaries.

## Related

- `codomyrmex.logistics.orchestration`
- `codomyrmex.agents.qwen`
