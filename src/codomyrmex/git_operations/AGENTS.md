# Agent Guidelines - Git Operations

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Git repository operations: commits, branches, merges, and history.

## Key Classes

- **GitRepo** — Repository operations
- **Commit** — Commit representation
- **Branch** — Branch management
- **DiffManager** — View diffs

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

1. **Check status first** — Verify clean state
2. **Branch often** — Feature branches for work
3. **Small commits** — Atomic, focused commits
4. **Meaningful messages** — Descriptive commit messages
5. **Pull before push** — Avoid merge conflicts

## Common Patterns

```python
from codomyrmex.git_operations import GitRepo, Branch

# Open repository
repo = GitRepo(".")

# Check status
status = repo.status()
if status.is_dirty:
    print(f"Modified: {status.modified_files}")

# Commit changes
repo.add(["src/main.py"])
repo.commit("feat: add new feature")

# Branch operations
branch = Branch(repo)
branch.create("feature/new-thing")
branch.checkout("feature/new-thing")

# View history
for commit in repo.log(limit=10):
    print(f"{commit.hash[:7]} - {commit.message}")
```

## Testing Patterns

```python
# Verify status
repo = GitRepo(".")
status = repo.status()
assert hasattr(status, "is_dirty")

# Verify log
commits = repo.log(limit=5)
assert len(commits) <= 5

# Verify branch listing
branches = repo.branches()
assert "main" in branches or "master" in branches
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full git lifecycle | All 34 `git_*` tools including all Destructive operations | TRUSTED |
| **Architect** | History analysis | `git_log`, `git_repo_status`, `git_diff`, `git_commit_details`, `git_blame`, `git_list_remotes`, `git_list_tags` (Safe only) | OBSERVED |
| **QATester** | State verification | `git_repo_status`, `git_diff`, `git_current_branch`, `git_log` | OBSERVED |
| **Researcher** | Read-only history | `git_log`, `git_commit_details`, `git_blame` | OBSERVED |

### Engineer Agent
**Access**: Full — all 34 tools including all Destructive operations (commit, push, branch, merge, rebase, reset).
**Use Cases**: Committing BUILD-phase artifacts, creating feature branches, pushing to remotes in EXECUTE phase, managing tags on release, cherry-picking hotfixes.

### Architect Agent
**Access**: Read-only — all Safe tools for history and diff analysis.
**Use Cases**: Analyzing commit history patterns, reviewing diffs for architectural decisions, understanding blame attribution, assessing branch topology.

### QATester Agent
**Access**: State verification — Safe read tools to confirm expected repository state after EXECUTE.
**Use Cases**: Verifying commits were created correctly, checking that the right files were staged, confirming branch state matches expected post-execution state.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
