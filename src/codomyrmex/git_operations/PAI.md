# Personal AI Infrastructure — Git Operations Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Git Operations module is a comprehensive **programmatic Git interface** for the codomyrmex ecosystem. It provides 30+ core git functions, GitHub API operations, repository management classes, and optional visualization integration. This is a **Core Layer** module that PAI agents use extensively during BUILD, EXECUTE, and VERIFY phases.

## PAI Capabilities

### Core Git Operations (25+ Functions)

```python
from codomyrmex.git_operations import (
    # Repository checks
    check_git_availability, is_git_repository, initialize_git_repository,
    clone_repository,
    # Branch operations
    create_branch, switch_branch, get_current_branch,
    merge_branch, rebase_branch,
    # File & commit operations
    add_files, commit_changes, amend_commit,
    get_status, get_diff, reset_changes,
    # Remote operations
    push_changes, pull_changes, fetch_changes,
    add_remote, remove_remote, list_remotes,
    # History
    get_commit_history,
    # Config
    get_config, set_config,
    # Advanced
    cherry_pick,
    # Tags
    create_tag, list_tags,
    # Stash
    stash_changes, apply_stash, list_stashes,
)

# Example: Get repository status
status = get_status("/path/to/repo")
branch = get_current_branch("/path/to/repo")
diff = get_diff("/path/to/repo")
```

### GitHub API Operations

```python
from codomyrmex.git_operations import (
    create_github_repository, delete_github_repository,
    create_pull_request, get_pull_requests, get_pull_request,
    get_repository_info, GitHubAPIError,
)

# Create a PR
pr = create_pull_request(
    owner="org", repo="project",
    title="Add feature", body="Description",
    head="feature-branch", base="main",
)
```

### Repository Management

```python
from codomyrmex.git_operations import (
    Repository, RepositoryManager, RepositoryType,
    RepositoryMetadataManager, RepositoryMetadata, CloneStatus,
)

manager = RepositoryManager()
repo = manager.get_repository("/path/to/repo")
metadata = RepositoryMetadataManager(repo)
```

### Visualization (Optional)

When visualization dependencies are available:

```python
from codomyrmex.git_operations import (
    create_git_analysis_report,
    visualize_git_branches,
    visualize_commit_activity,
    create_git_workflow_diagram,
    analyze_repository_structure,
    get_repository_metadata,
)
```

### CLI Commands

```bash
codomyrmex git_operations status  # Show git status for current directory
codomyrmex git_operations info    # Show repository info (branch, remotes, path)
```

## Key Exports

| Category | Exports | Count |
|----------|---------|-------|
| **Core Git** | `check_git_availability`, `is_git_repository`, `clone_repository`, `create_branch`, `switch_branch`, `get_current_branch`, `merge_branch`, `rebase_branch`, `add_files`, `commit_changes`, `amend_commit`, `get_status`, `get_diff`, `reset_changes`, `push_changes`, `pull_changes`, `fetch_changes`, `add_remote`, `remove_remote`, `list_remotes`, `get_commit_history`, `get_config`, `set_config`, `cherry_pick`, `create_tag`, `list_tags`, `stash_changes`, `apply_stash`, `list_stashes` | 29 |
| **Repository** | `Repository`, `RepositoryManager`, `RepositoryType`, `RepositoryMetadataManager`, `RepositoryMetadata`, `CloneStatus` | 6 |
| **GitHub API** | `create_github_repository`, `delete_github_repository`, `create_pull_request`, `get_pull_requests`, `get_pull_request`, `get_repository_info`, `GitHubAPIError` | 7 |
| **Visualization** | `create_git_analysis_report`, `visualize_git_branches`, `visualize_commit_activity`, `create_git_workflow_diagram`, `analyze_repository_structure`, `get_repository_metadata` | 6 (optional) |

## MCP Integration

The MCP server exposes 31 git tools that delegate to this module's core functions. These are among the most-used tools during PAI OBSERVE, BUILD, and EXECUTE phases.

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_check_availability` | Check if git is available on the system | Safe |
| `git_is_repo` | Check if a directory is a git repository | Safe |
| `git_repo_status` | Get repository status (modified, staged, untracked files) | Safe |
| `git_current_branch` | Get the current branch name | Safe |
| `git_diff` | Get diff of uncommitted changes (optionally staged only) | Safe |
| `git_log` | Get recent commit history with configurable count | Safe |
| `git_init` | Initialize a new git repository at a path | Safe |
| `git_clone` | Clone a repository from URL to local path | Safe |
| `git_commit` | Stage files and create a commit with a message | Safe |
| `git_create_branch` | Create a new branch | Safe |
| `git_switch_branch` | Switch to a different branch | Safe |
| `git_delete_branch` | Delete a local branch (with optional force) | Safe |
| `git_merge` | Merge a source branch into a target branch | Safe |
| `git_rebase` | Rebase current branch onto a target branch | Safe |
| `git_cherry_pick` | Cherry-pick a specific commit onto the current branch | Safe |
| `git_revert` | Revert a commit by creating an inverse commit | Safe |
| `git_reset` | Reset repository to a commit (soft, mixed, or hard mode) | Safe |
| `git_amend` | Amend the most recent commit message or content | Safe |
| `git_pull` | Pull latest changes from a remote repository | Safe |
| `git_push` | Push local commits to a remote repository | Safe |
| `git_fetch` | Fetch changes from remote without merging | Safe |
| `git_add_remote` | Add a named remote URL | Safe |
| `git_remove_remote` | Remove a named remote | Safe |
| `git_list_remotes` | List all configured remotes | Safe |
| `git_stash` | Stash uncommitted changes with optional message | Safe |
| `git_stash_apply` | Apply a stash entry to the working directory | Safe |
| `git_stash_list` | List all stash entries | Safe |
| `git_create_tag` | Create a lightweight or annotated tag | Safe |
| `git_list_tags` | List all tags in the repository | Safe |
| `git_blame` | Show line-by-line commit attribution for a file | Safe |
| `git_commit_details` | Get detailed metadata for a specific commit by SHA | Safe |
| `git_get_config` | Read a git configuration value by key | Safe |
| `git_set_config` | Set a git configuration value (local or global) | Safe |
| `git_clean` | Delete untracked files from the working tree (irreversible) | Safe |

## PAI Algorithm Phase Mapping

| Phase | Git Operations Contribution |
|-------|---------------------------|
| **OBSERVE** | `get_status`, `get_diff`, `get_current_branch`, `get_commit_history` — understand repository state |
| **THINK** | `get_blame`, `get_commit_details` — analyze code ownership and commit context to inform decision-making |
| **PLAN** | `list_remotes`, `get_repository_info` — assess project structure and remote configuration |
| **BUILD** | `create_branch`, `add_files`, `commit_changes` — create artifacts and version them |
| **EXECUTE** | `push_changes`, `pull_changes`, `merge_branch`, `create_pull_request` — execute git workflows |
| **VERIFY** | `get_diff` — validate changes match intent; `get_status` — confirm clean state |
| **LEARN** | `get_commit_history` — review past changes for patterns |

## Architecture Role

**Core Layer** — Depends on `logging_monitoring` and `environment_setup` (Foundation). Used by Service and Application layer modules for version control operations.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Bridge**: [../model_context_protocol/PAI.md](../model_context_protocol/PAI.md) — MCP tools that wrap git operations
