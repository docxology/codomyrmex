# Git Core Commands

> **Codomyrmex v1.1.9** | Sub-module of `git_operations.core` | March 2026

## Overview

The `commands` sub-module contains the low-level Git command wrappers that
power the `git_operations` module. Each file maps to a distinct Git domain
(branching, commits, status, history, remotes, merging, stashing, tags,
submodules, sync, config, and repository introspection). Most functions call
`subprocess.run` with `check=True` and expose results as typed Python values.

Several functions are decorated with `@mcp_tool` and are therefore
auto-discovered by the PAI MCP bridge.

## PAI Integration

| PAI Phase | Usage |
|-----------|-------|
| OBSERVE   | `get_status`, `get_commit_history`, `get_current_branch`, `list_branches` |
| EXECUTE   | `commit_changes`, `push_changes`, `merge_branch`, `create_branch` |
| BUILD     | `stash_changes`, `pop_stash`, `create_tag` |

## Key Exports

| File | Functions | MCP Tools |
|------|-----------|-----------|
| `branching.py` | `create_branch`, `switch_branch`, `delete_branch`, `get_current_branch`, `list_branches` | -- |
| `commit.py` | `commit_changes` | `git_commit` |
| `status.py` | `add_files`, `get_status` | `git_add`, `git_repo_status` |
| `history.py` | `get_commit_history` | `git_log` |
| `config.py` | `get_config` | `get_config` |
| `merge.py` | `merge_branch` | `git_merge` |
| `remote.py` | `fetch_remote` | `git_fetch` |
| `repository.py` | `check_git_availability`, `is_git_repository` | `git_check_availability`, `git_is_repo` |
| `stash.py` | `stash_changes` | `git_stash` |
| `submodules.py` | `init_submodules` | `init_submodules` |
| `sync.py` | `push_changes` | `git_push` |
| `tags.py` | `create_tag` | `git_create_tag` |

## Quick Start

```python
from codomyrmex.git_operations.core.commands.branching import (
    create_branch,
    get_current_branch,
    list_branches,
)

current = get_current_branch()
branches = list_branches()

from codomyrmex.git_operations.core.commands.commit import commit_changes
sha = commit_changes("fix: resolve edge case in parser")

from codomyrmex.git_operations.core.commands.status import get_status
status = get_status()  # {"modified": [...], "untracked": [...], ...}
```

## Architecture

```
git_operations/core/commands/
  __init__.py       # Package marker
  branching.py      # Branch create/switch/delete/list/current
  commit.py         # Commit with optional author override and selective staging
  config.py         # Read/write git config values
  history.py        # Commit log retrieval with structured output
  merge.py          # Branch merging with strategy support
  remote.py         # Fetch from remotes
  repository.py     # Git availability check, repository detection
  stash.py          # Stash push/pop
  status.py         # Working tree status, stage files
  submodules.py     # Submodule init/update
  sync.py           # Push to remote
  tags.py           # Annotated and lightweight tag creation
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/git_operations/ -v
```

## Navigation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../../README.md) | `git_operations` module overview |
