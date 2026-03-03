# Git Core Commands - Agent Coordination

> **Codomyrmex v1.0.8** | Sub-module of `git_operations.core` | March 2026

## Overview

This sub-module provides the low-level Git command wrappers that agents use for
version control operations. Functions call `subprocess.run` directly and return
typed Python values (strings, booleans, dicts, lists). Many are decorated with
`@mcp_tool` for automatic PAI bridge discovery.

## Key Files

| File | Purpose |
|------|---------|
| `branching.py` | `create_branch`, `switch_branch`, `delete_branch`, `get_current_branch`, `list_branches` |
| `commit.py` | `commit_changes` -- stages files and commits with optional author override |
| `status.py` | `add_files`, `get_status` -- staging area and porcelain status parsing |
| `history.py` | `get_commit_history` -- structured commit log retrieval |
| `merge.py` | `merge_branch` -- merge with optional strategy parameter |
| `remote.py` | `fetch_remote` -- fetch from a named remote |
| `sync.py` | `push_changes` -- push commits to a remote branch |
| `stash.py` | `stash_changes` -- stash working tree changes |
| `tags.py` | `create_tag` -- annotated and lightweight tags |
| `config.py` | `get_config` -- read local or global git config |
| `repository.py` | `check_git_availability`, `is_git_repository` |
| `submodules.py` | `init_submodules` -- recursive submodule init/update |

## MCP Tools Available

| Tool Name | Function | Module |
|-----------|----------|--------|
| `git_commit` | `commit_changes` | `commit.py` |
| `git_add` | `add_files` | `status.py` |
| `git_repo_status` | `get_status` | `status.py` |
| `git_log` | `get_commit_history` | `history.py` |
| `git_merge` | `merge_branch` | `merge.py` |
| `git_fetch` | `fetch_remote` | `remote.py` |
| `git_push` | `push_changes` | `sync.py` |
| `git_stash` | `stash_changes` | `stash.py` |
| `git_create_tag` | `create_tag` | `tags.py` |
| `git_check_availability` | `check_git_availability` | `repository.py` |
| `git_is_repo` | `is_git_repository` | `repository.py` |
| `get_config` | `get_config` | `config.py` |
| `init_submodules` | `init_submodules` | `submodules.py` |

## Agent Instructions

1. **Use `get_status()` before committing** to verify which files are staged,
   modified, or untracked.
2. **Prefer `commit_changes(file_paths=[...])` over `stage_all=True`** when
   committing specific files to avoid accidentally including unrelated changes.
3. **Check `is_git_repository()` before any git operation** in workflows that
   may run outside a repository.
4. **Handle `subprocess.CalledProcessError`** -- all functions use `check=True`
   and will raise on non-zero git exit codes.
5. **Destructive operations (`push_changes`, `delete_branch(force=True)`,
   `merge_branch`) require PAI trust level TRUSTED** -- these are gated by
   the trust gateway.

## Operating Contracts

- All functions accept an optional `repository_path` parameter (defaults to
  `os.getcwd()`).
- Boolean-returning functions return `True` on success; they raise
  `subprocess.CalledProcessError` on git errors rather than returning `False`
  silently.
- `get_commit_history` returns a list of dicts with keys: `hash`,
  `author_name`, `author_email`, `date`, `message`.
- `get_status` returns a dict with keys: `modified`, `added`, `deleted`,
  `untracked`, `renamed`, and `conflicted` (lists of file paths).

## Common Patterns

```python
# Pattern: safe commit workflow
from codomyrmex.git_operations.core.commands.status import add_files, get_status
from codomyrmex.git_operations.core.commands.commit import commit_changes

status = get_status("/path/to/repo")
if status.get("modified"):
    sha = commit_changes(
        message="fix: resolve edge case",
        file_paths=status["modified"],
        repository_path="/path/to/repo",
    )
```

## PAI Agent Role Access Matrix

| Agent Role | Permitted Operations |
|------------|---------------------|
| Engineer   | Full access -- all commands including push, merge, delete |
| Architect  | Read-only -- status, history, config, branch listing |
| QATester   | Read-only + stash (for test isolation) |

## Navigation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Module overview and quick start |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../../README.md) | `git_operations` module overview |
