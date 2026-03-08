# Git Core Commands - Specification

> **Codomyrmex v1.1.9** | Sub-module of `git_operations.core` | March 2026

## Overview

This specification defines the interface contracts, error semantics, and
behavioural guarantees for the low-level Git command wrappers in
`git_operations.core.commands`.

## Design Principles

- **Zero-Mock Policy**: Tests must operate on real Git repositories. Use
  temporary directories with `git init` in test fixtures rather than mocking
  subprocess.
- **Explicit Failure**: All functions use `subprocess.run(..., check=True)`.
  Git errors surface as `subprocess.CalledProcessError` -- never swallowed.
- **Consistent Defaults**: Every function that accepts `repository_path`
  defaults to `os.getcwd()` when `None`.
- **MCP Compatibility**: Functions decorated with `@mcp_tool` accept and return
  JSON-serialisable types only.

## Architecture

```
commands/
  branching.py      # Branch CRUD + current branch query
  commit.py         # Commit with author override and selective staging
  config.py         # Git config read (local + global)
  history.py        # Structured commit log
  merge.py          # Branch merge with strategy support
  remote.py         # Fetch from remotes
  repository.py     # Git availability and repository detection
  stash.py          # Stash push/pop
  status.py         # Porcelain status parser + staging
  submodules.py     # Recursive submodule init
  sync.py           # Push to remote
  tags.py           # Tag creation (annotated + lightweight)
```

## Functional Requirements

### FR-1: Branch Management (`branching.py`)

- `create_branch(name, repo_path) -> bool`: Run `git checkout -b <name>`.
- `switch_branch(name, repo_path) -> bool`: Run `git checkout <name>`.
- `delete_branch(name, repo_path, force) -> bool`: Run `git branch -d|-D`.
- `get_current_branch(repo_path) -> str`: Run `git branch --show-current`.
- `list_branches(repo_path) -> list[str]`: Run `git branch --list`, strip
  markers.

### FR-2: Commit (`commit.py`)

- `commit_changes(message, repo_path, author_name, author_email, stage_all, file_paths) -> str | None`:
  Stage files (via `add_files` or `git add -u`), then `git commit -m`.
  Return the new commit SHA on success, `None` on failure.
- MCP tool name: `git_commit`.

### FR-3: Status (`status.py`)

- `add_files(file_paths, repo_path) -> bool`: Run `git add <files>`.
  MCP tool name: `git_add`.
- `get_status(repo_path) -> dict[str, Any]`: Parse `git status --porcelain`
  into categorised file lists. MCP tool name: `git_repo_status`.

### FR-4: History (`history.py`)

- `get_commit_history(limit, repo_path) -> list[dict[str, str]]`:
  Parse `git log --pretty=format:%H|%an|%ae|%ad|%s` into list of dicts
  with keys `hash`, `author_name`, `author_email`, `date`, `message`.
  MCP tool name: `git_log`.

### FR-5: Merge (`merge.py`)

- `merge_branch(source, target, repo_path, strategy) -> bool`:
  Switch to target (if needed), run `git merge [--strategy=<s>] <source>`.
  MCP tool name: `git_merge`.

### FR-6: Remote Operations

- `fetch_remote(remote, repo_path) -> bool` (`remote.py`). MCP: `git_fetch`.
- `push_changes(remote, branch, repo_path) -> bool` (`sync.py`). MCP: `git_push`.

### FR-7: Stash, Tags, Submodules

- `stash_changes(message, repo_path) -> bool`. MCP: `git_stash`.
- `create_tag(name, message, repo_path) -> bool`. MCP: `git_create_tag`.
- `init_submodules(repo_path) -> bool`. MCP: `init_submodules`.

### FR-8: Repository Introspection

- `check_git_availability() -> bool`. MCP: `git_check_availability`.
- `is_git_repository(repo_path) -> bool`. MCP: `git_is_repo`.
- `get_config(key, repo_path, global_config) -> str | None`. MCP: `get_config`.

## Interface Contracts

All functions share these invariants:

| Parameter | Type | Default | Semantics |
|-----------|------|---------|-----------|
| `repository_path` | `str \ | None` | `None` (cwd) Absolute or relative path to a git working tree |

Return types are strictly `bool`, `str`, `str | None`, `list[str]`,
`list[dict]`, or `dict[str, Any]` -- all JSON-serialisable.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `subprocess` | All git command execution |
| `os` | Working directory resolution |
| `codomyrmex.logging_monitoring` | Structured logging |
| `codomyrmex.model_context_protocol.decorators` | `@mcp_tool` decorator |
| `codomyrmex.performance` | Optional `monitor_performance` in `repository.py` |

## Constraints

- Commands require `git` to be installed and on `PATH`.
- `commit_changes` with `stage_all=True` runs `git add -u` (tracked files
  only -- does not add untracked files).
- `merge_branch` auto-detects the current branch as target when `target_branch`
  is `None`.
- `delete_branch(force=True)` uses `-D` (force) -- destructive and
  trust-gated.

## Navigation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Module overview and quick start |
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [Parent README](../../README.md) | `git_operations` module overview |
