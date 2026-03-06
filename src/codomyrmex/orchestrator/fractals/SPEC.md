# FRACTALS SUBMODULE SPECIFICATION

## Context & Motivation

Large tasks often paralyze standard single-agent loops. Codomyrmex required an engine identical to `TinyAGI/fractals` to natively fragment complex issues into smaller atomic components. This specific design creates autonomous self-similar trees bounded explicitly by git structural isolation.

## Data Structures

- **TaskNode**: Pydantic immutability capturing `id`, `description`, `depth`, `lineage`, `status`, and `children`.
- **WorkspaceManager**: Class wrapping POSIX compliance mapping logic to git repository architectures. Relies heavily on `git worktree add` for branching strategies.

## Execution Flow

1. Root `build_tree` instantiated over objective standard payload.
2. `plan()` resolves recursively up to `-max_depth`.
3. `workspace.init_workspace()` provisions base operational space.
4. `executor` sweeps over `planned_tree.get_leaves()` triggering `WorkspaceManager.create_worktree()`.
5. AI completion triggers `TaskStatus.DONE` and propagates statuses.
6. MCP interface returns normalized JSON of successes and failures.

## Security

Agent executions are run tightly within local scopes. The fallback provider maps to internal codomyrmex instances utilizing system API keys securely sourced from `.env` context configurations.
