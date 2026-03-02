# Core - Agent Coordination

## Purpose

Hub module re-exporting 37 git operation functions from the `commands/` subpackage, covering branching, commits, remotes, stash, sync, tags, submodules, config, and status.

## Key Components

| Component | Category | Functions |
|-----------|----------|-----------|
| `commands/branching` | Branch management | `create_branch`, `delete_branch`, `get_current_branch`, `switch_branch` |
| `commands/commit` | Commit operations | `commit_changes`, `amend_commit`, `revert_commit`, `cherry_pick` |
| `commands/config` | Git config | `get_config`, `set_config` |
| `commands/history` | History queries | `get_commit_history`, `get_commit_history_filtered`, `get_commit_details`, `get_blame` |
| `commands/merge` | Merge/rebase | `merge_branch`, `rebase_branch` |
| `commands/remote` | Remote management | `add_remote`, `remove_remote`, `list_remotes`, `fetch_remote`, `prune_remote` |
| `commands/repository` | Repo operations | `check_git_availability`, `clone_repository`, `initialize_git_repository`, `is_git_repository` |
| `commands/stash` | Stash operations | `stash_changes`, `apply_stash`, `list_stashes` |
| `commands/status` | Working tree | `get_status`, `get_diff`, `get_diff_files`, `add_files`, `reset_changes`, `clean_repository` |
| `commands/submodules` | Submodule ops | `init_submodules`, `update_submodules` |
| `commands/sync` | Push/pull/fetch | `push_changes`, `pull_changes`, `fetch_changes` |
| `commands/tags` | Tag management | `create_tag`, `list_tags` |

## Operating Contracts

- All 37 functions are re-exported via `__all__` for direct import from `git_operations.core`.
- Performance monitoring is optional -- falls back to no-op decorators if unavailable.
- Destructive operations (push, clean, reset, delete_branch) require appropriate trust level when invoked via MCP.

## Integration Points

- **Parent module**: `git_operations/` exposes 34 `@mcp_tool`-decorated tools via `mcp_tools.py`.
- **Dependencies**: `codomyrmex.logging_monitoring`, `codomyrmex.performance`.

## Navigation

- **Parent**: [git_operations/](../README.md)
- **Sibling**: [SPEC.md](SPEC.md)
- **Root**: [/README.md](../../../../README.md)
