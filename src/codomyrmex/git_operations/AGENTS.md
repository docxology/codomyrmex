# Agent Guidelines - Git Operations

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Git repository operations: commits, branches, merges, history, remotes, tags, stash, diffs, and GitHub API integration. Exposes a comprehensive function-based API (not class-based) organized into command modules covering branching, commit, config, history, merge, remote, repository lifecycle, stash, status, submodules, sync, and tags. The module also provides `Repository` and `RepositoryManager` for higher-level repository management, `RepositoryMetadataManager` for clone/metadata tracking, and GitHub API operations for pull requests and repository management. All 34 MCP tools are auto-discovered via `@mcp_tool` decorators.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports all public functions and classes; optional visualization integration |
| `core/git.py` | Re-exports all command functions from the `commands/` subpackage |
| `core/commands/branching.py` | `create_branch()`, `delete_branch()`, `switch_branch()`, `get_current_branch()`, `list_branches()` |
| `core/commands/commit.py` | `commit_changes()`, `amend_commit()`, `cherry_pick()`, `revert_commit()` |
| `core/commands/config.py` | `get_config()`, `set_config()` |
| `core/commands/history.py` | `get_commit_history()`, `get_commit_history_filtered()`, `get_commit_details()`, `get_blame()` |
| `core/commands/merge.py` | `merge_branch()`, `rebase_branch()` |
| `core/commands/remote.py` | `add_remote()`, `remove_remote()`, `list_remotes()`, `fetch_remote()`, `prune_remote()` |
| `core/commands/repository.py` | `check_git_availability()`, `is_git_repository()`, `initialize_git_repository()`, `clone_repository()` |
| `core/commands/stash.py` | `stash_changes()`, `apply_stash()`, `list_stashes()` |
| `core/commands/status.py` | `get_status()`, `get_diff()`, `get_diff_files()`, `add_files()`, `reset_changes()`, `clean_repository()` |
| `core/commands/submodules.py` | `init_submodules()`, `update_submodules()` |
| `core/commands/sync.py` | `push_changes()`, `pull_changes()`, `fetch_changes()` |
| `core/commands/tags.py` | `create_tag()`, `list_tags()` |
| `core/repository.py` | `Repository` dataclass, `RepositoryManager`, `RepositoryType` enum |
| `core/metadata.py` | `RepositoryMetadata`, `RepositoryMetadataManager`, `CloneStatus` |
| `api/github.py` | `create_github_repository()`, `delete_github_repository()`, `create_pull_request()`, `get_pull_requests()`, `get_pull_request()`, `get_repository_info()`, `GitHubAPIError` |
| `api/visualization.py` | Optional: `visualize_git_branches()`, `visualize_commit_activity()`, `create_git_analysis_report()` |
| `mcp_tools.py` | 34 MCP tools auto-discovered via `@mcp_tool` decorators |

## Key Classes

- **Repository** -- Dataclass representing a git repository with path, name, and type.
- **RepositoryManager** -- High-level repository lifecycle management (create, list, remove).
- **RepositoryType** -- Enum for repository types.
- **RepositoryMetadata** -- Metadata about a cloned/managed repository.
- **RepositoryMetadataManager** -- Tracks clone status and metadata for managed repositories.
- **CloneStatus** -- Enum for clone states.
- **GitHubAPIError** -- Exception for GitHub API failures.

**Note:** The git_operations module uses a **function-based API** (e.g., `commit_changes()`, `create_branch()`, `push_changes()`), not a class-based one. All functions accept a `repository_path` argument to specify the target repo.

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge. The 34 tools are grouped by category below.

**Setup & Status**

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_check_availability` | Check if git is available on this system | Safe |
| `git_is_repo` | Check if a directory is a git repository | Safe |
| `git_repo_status` | Get repository status (modified, staged, untracked files) | Safe |
| `git_current_branch` | Get the current branch name | Safe |
| `git_get_config` | Read a git configuration value by key | Safe |
| `git_set_config` | Set a git configuration value (local or global scope) | Destructive |

**Commits & Staging**

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_commit` | Stage files and create a commit with a message | Destructive |
| `git_amend` | Amend the most recent commit message or content | Destructive |
| `git_commit_details` | Get detailed metadata for a specific commit by SHA | Safe |
| `git_log` | Get recent commit history | Safe |
| `git_log_filtered` | Get commit history with filters (author, date, etc) | Safe |
| `git_blame` | Show git blame output for a file (line-by-line attribution) | Safe |

**Branches & Merging**

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_create_branch` | Create a new branch | Destructive |
| `git_switch_branch` | Switch to a different branch | Destructive |
| `git_delete_branch` | Delete a local branch (force option for unmerged) | Destructive |
| `git_merge` | Merge a source branch into a target branch | Destructive |
| `git_rebase` | Rebase current branch onto a target branch | Destructive |
| `git_cherry_pick` | Cherry-pick a specific commit onto the current branch | Destructive |
| `git_revert` | Revert a commit by creating a new inverse commit | Destructive |
| `git_reset` | Reset repository to a commit (soft/mixed/hard mode) | Destructive |

**Remote Operations**

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_clone` | Clone a repository from a URL to a local path | Destructive |
| `git_init` | Initialize a new git repository | Destructive |
| `git_pull` | Pull latest changes from a remote | Destructive |
| `git_push` | Push local commits to a remote | Destructive |
| `git_fetch` | Fetch changes from a remote without merging | Safe |
| `git_add_remote` | Add a named remote URL | Destructive |
| `git_remove_remote` | Remove a named remote | Destructive |
| `git_list_remotes` | List all configured remotes | Safe |

**Diffs & Stash**

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_diff` | Get diff of uncommitted changes (staged or unstaged) | Safe |
| `git_stash` | Stash uncommitted changes with optional description | Destructive |
| `git_stash_apply` | Apply a stash entry to the working directory | Destructive |
| `git_stash_list` | List all stash entries | Safe |

**Tags & Cleanup**

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `git_create_tag` | Create a lightweight or annotated tag | Destructive |
| `git_list_tags` | List all tags in the repository | Safe |
| `git_clean` | Delete untracked files from the working tree (irreversible) | Destructive |

## Agent Instructions

1. **Check status first** -- Verify clean state before operations.
2. **Branch often** -- Feature branches for work.
3. **Small commits** -- Atomic, focused commits.
4. **Meaningful messages** -- Descriptive commit messages.
5. **Pull before push** -- Avoid merge conflicts.
6. **Lock awareness** -- Check for `.git/index.lock` before write operations in multi-agent environments.

## Operating Contracts

- All functions accept a `repository_path` argument (string path). They do not maintain global state.
- `check_git_availability()` must return True before any other operations are called.
- `is_git_repository()` must return True for the target path before calling commit/branch/merge operations.
- `push_changes()` with `force=True` requires explicit trust escalation -- never force-push to `main`/`master` without authorization.
- `reset_changes()` with `mode="hard"` is destructive and irreversible -- it discards uncommitted work.
- `clean_repository()` permanently deletes untracked files -- there is no undo.
- `amend_commit()` rewrites history -- never use on commits that have been pushed to a shared remote.
- In multi-agent environments, always check for `.git/index.lock` before write operations: `ls .git/index.lock 2>/dev/null`.
- Clear stale locks only when no git process is running: check `ps aux | grep git` first, then `rm -f .git/index.lock` if stale > 60s.
- **DO NOT** use `--no-verify` on commits unless explicitly authorized by the user.
- **DO NOT** call `delete_branch()` with `force=True` on branches that have unmerged work without user confirmation.
- **DO NOT** call `rebase_branch()` on branches that have been pushed to shared remotes -- this rewrites history.
- GitHub API functions (`create_pull_request()`, etc.) require a valid `GITHUB_TOKEN` environment variable.

## Common Patterns

### Basic Workflow

```python
from codomyrmex.git_operations import (
    check_git_availability, is_git_repository, get_status,
    add_files, commit_changes, create_branch, get_current_branch,
    get_commit_history
)

repo = "/path/to/repo"

if check_git_availability() and is_git_repository(repo):
    status = get_status(repo)
    print(f"Branch: {get_current_branch(repo)}")

    # Stage and commit
    add_files(repo, ["src/main.py"])
    commit_changes(repo, "feat: add new feature")

    # View history
    for entry in get_commit_history(limit=5, repository_path=repo):
        print(f"{entry['hash'][:7]} - {entry['message']}")
```

### Branch and Merge

```python
from codomyrmex.git_operations import (
    create_branch, switch_branch, merge_branch, delete_branch
)

create_branch(repo, "feature/new-thing")
switch_branch(repo, "feature/new-thing")
# ... do work, commit ...
switch_branch(repo, "main")
merge_branch(repo, "feature/new-thing")
delete_branch(repo, "feature/new-thing")
```

## Testing Patterns

```python
from codomyrmex.git_operations import (
    check_git_availability, is_git_repository, get_status,
    get_commit_history, get_current_branch
)

# Verify availability
assert check_git_availability()

# Verify repo detection
assert is_git_repository(".")

# Verify status fields
status = get_status(".")
assert isinstance(status, dict)

# Verify log
commits = get_commit_history(limit=5, repository_path=".")
assert len(commits) <= 5
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full git lifecycle | All 34 `git_*` tools including all Destructive operations | TRUSTED |
| **Architect** | History analysis | `git_log`, `git_repo_status`, `git_diff`, `git_commit_details`, `git_blame`, `git_list_remotes`, `git_list_tags` (Safe only) | OBSERVED |
| **QATester** | State verification | `git_repo_status`, `git_diff`, `git_current_branch`, `git_log` | OBSERVED |
| **Researcher** | Read-only history | `git_log`, `git_commit_details`, `git_blame` | OBSERVED |

### Engineer Agent
**Access**: Full -- all 34 tools including all Destructive operations (commit, push, branch, merge, rebase, reset).
**Use Cases**: Committing BUILD-phase artifacts, creating feature branches, pushing to remotes in EXECUTE phase, managing tags on release, cherry-picking hotfixes.

### Architect Agent
**Access**: Read-only -- all Safe tools for history and diff analysis.
**Use Cases**: Analyzing commit history patterns, reviewing diffs for architectural decisions, understanding blame attribution, assessing branch topology.

### QATester Agent
**Access**: State verification -- Safe read tools to confirm expected repository state after EXECUTE.
**Use Cases**: Verifying commits were created correctly, checking that the right files were staged, confirming branch state matches expected post-execution state.

### Researcher Agent
**Access**: Read-only history tools for analysis.
**Use Cases**: Mining commit history for patterns, analyzing contributor activity, studying code evolution.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
