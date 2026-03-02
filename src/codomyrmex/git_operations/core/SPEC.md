# Core - Technical Specification

## Overview

Central hub module for git operations. Re-exports 37 functions from `commands/` subpackage organized into 10 categories. Acts as the single import point for all git functionality.

## Architecture

```
git_operations/core/
├── git.py              # Hub: re-exports all 37 functions from commands/
└── commands/
    ├── branching.py    # create, delete, get_current, switch
    ├── commit.py       # commit, amend, revert, cherry_pick
    ├── config.py       # get_config, set_config
    ├── history.py      # commit_history, filtered, details, blame
    ├── merge.py        # merge_branch, rebase_branch
    ├── remote.py       # add, remove, list, fetch, prune
    ├── repository.py   # check_availability, clone, init, is_repo
    ├── stash.py        # stash, apply, list
    ├── status.py       # status, diff, diff_files, add, reset, clean
    ├── submodules.py   # init, update
    ├── sync.py         # push, pull, fetch
    └── tags.py         # create, list
```

## Exported Functions (37 total)

All functions are listed in `__all__` and importable from `codomyrmex.git_operations.core`.

| Category | Count | Functions |
|----------|-------|-----------|
| Branching | 4 | `create_branch`, `switch_branch`, `delete_branch`, `get_current_branch` |
| Commit | 4 | `commit_changes`, `amend_commit`, `revert_commit`, `cherry_pick` |
| Config | 2 | `get_config`, `set_config` |
| History | 4 | `get_commit_history`, `get_commit_history_filtered`, `get_commit_details`, `get_blame` |
| Merge | 2 | `merge_branch`, `rebase_branch` |
| Remote | 5 | `add_remote`, `remove_remote`, `list_remotes`, `fetch_remote`, `prune_remote` |
| Repository | 4 | `check_git_availability`, `clone_repository`, `initialize_git_repository`, `is_git_repository` |
| Stash | 3 | `stash_changes`, `apply_stash`, `list_stashes` |
| Status | 6 | `get_status`, `get_diff`, `get_diff_files`, `add_files`, `reset_changes`, `clean_repository` |
| Sync | 3 | `push_changes`, `pull_changes`, `fetch_changes` |
| Submodules | 2 | `init_submodules`, `update_submodules` |
| Tags | 2 | `create_tag`, `list_tags` |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring.core.logger_config`, `codomyrmex.performance`
- **External**: Git CLI (subprocess-based operations in commands/)

## Constraints

- Performance monitoring import failure falls back to no-op decorators -- never blocks operation.
- All functions delegate to `commands/` subpackage; `git.py` itself contains no business logic.
