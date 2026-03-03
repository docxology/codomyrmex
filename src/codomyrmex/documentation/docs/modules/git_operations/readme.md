# Git Operations

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Git Operations Module for Codomyrmex.

## Architecture Overview

```
git_operations/
    __init__.py              # Public API exports
    mcp_tools.py             # MCP tool definitions
```

## Key Exports

- **`cli_commands`**
- **`check_git_availability`**
- **`is_git_repository`**
- **`initialize_git_repository`**
- **`clone_repository`**
- **`create_branch`**
- **`delete_branch`**
- **`switch_branch`**
- **`get_current_branch`**
- **`list_branches`**
- **`merge_branch`**
- **`rebase_branch`**
- **`add_files`**
- **`commit_changes`**
- **`amend_commit`**

## MCP Tools Reference

| Tool | Trust Level |
|------|-------------|
| `git_check_availability` | Safe |
| `git_is_repo` | Safe |
| `git_current_branch` | Safe |
| `git_diff` | Safe |
| `git_log` | Safe |
| `git_init` | Safe |
| `git_clone` | Safe |
| `git_commit` | Safe |
| `git_create_branch` | Safe |
| `git_switch_branch` | Safe |
| `git_list_branches` | Safe |
| `git_pull` | Safe |
| `git_push` | Safe |
| `git_delete_branch` | Safe |
| `git_merge` | Safe |
| `git_rebase` | Safe |
| `git_cherry_pick` | Safe |
| `git_revert` | Safe |
| `git_reset` | Safe |
| `git_amend` | Safe |
| `git_stash` | Safe |
| `git_stash_apply` | Safe |
| `git_stash_list` | Safe |
| `git_create_tag` | Safe |
| `git_list_tags` | Safe |
| `git_fetch` | Safe |
| `git_add_remote` | Safe |
| `git_remove_remote` | Safe |
| `git_list_remotes` | Safe |
| `git_commit_details` | Safe |
| `git_get_config` | Safe |
| `git_clean` | Safe |

## Related Modules

See [All Modules](../README.md) for the complete module listing.

## Navigation

- **Source**: [src/codomyrmex/git_operations/](../../../../src/codomyrmex/git_operations/)
- **Parent**: [All Modules](../README.md)
