# GitHub API Client

> **Codomyrmex v1.1.9** | Sub-module of `git_operations.api` | March 2026

## Overview

The `github` sub-module provides typed Python wrappers around the GitHub REST
API v3 for repository management, pull requests, and issues. Both synchronous
(via `requests`) and asynchronous (via `aiohttp`) variants are available for
every operation. Authentication is handled through a `GITHUB_TOKEN` environment
variable or an explicit token parameter.

## PAI Integration

| PAI Phase | Usage |
|-----------|-------|
| EXECUTE   | Create repositories, open pull requests, file issues |
| OBSERVE   | List PRs, issues, and repository metadata |
| VERIFY    | Check PR status, review issue state |

## Key Exports

| Export | Source | Description |
|--------|--------|-------------|
| `GitHubAPIError` | `base.py` | Custom exception for all GitHub API errors |
| `_get_github_headers` | `base.py` | Build auth headers for GitHub API v3 |
| `_validate_github_token` | `base.py` | Validate token from param or `GITHUB_TOKEN` env var |
| `_async_request` | `base.py` | Generic async HTTP request via `aiohttp` |
| `create_github_repository` | `repositories.py` | Create a new GitHub repository |
| `delete_github_repository` | `repositories.py` | Delete a GitHub repository |
| `get_repository_info` | `repositories.py` | Fetch repository metadata |
| `async_get_repo_info` | `repositories.py` | Async variant of repository info retrieval |
| `create_pull_request` | `pull_requests.py` | Open a new pull request |
| `get_pull_requests` | `pull_requests.py` | List pull requests for a repository |
| `get_pull_request` | `pull_requests.py` | Fetch a single PR by number |
| `async_list_pull_requests` | `pull_requests.py` | Async PR listing |
| `async_create_pull_request` | `pull_requests.py` | Async PR creation |
| `async_get_pull_request` | `pull_requests.py` | Async single PR retrieval |
| `create_issue` | `issues.py` | Create a new issue |
| `list_issues` | `issues.py` | List issues for a repository |
| `close_issue` | `issues.py` | Close an existing issue |
| `add_comment` | `issues.py` | Add a comment to an issue or PR |
| `async_create_issue` | `issues.py` | Async issue creation |
| `async_list_issues` | `issues.py` | Async issue listing |
| `async_close_issue` | `issues.py` | Async issue closing |
| `async_add_comment` | `issues.py` | Async comment creation |

## Quick Start

```python
from codomyrmex.git_operations.api.github import (
    create_pull_request,
    list_issues,
    get_repository_info,
)

# Uses GITHUB_TOKEN env var by default
repo = get_repository_info("owner", "repo-name")

pr = create_pull_request(
    repo_owner="owner",
    repo_name="repo-name",
    head_branch="feature/my-change",
    base_branch="main",
    title="Add new feature",
    body="Description of changes",
)

issues = list_issues("owner", "repo-name", state="open")
```

## Architecture

```
git_operations/api/github/
  __init__.py          # Re-exports all public symbols
  base.py              # GitHubAPIError, auth helpers, async request utility
  issues.py            # Issue CRUD (sync + async)
  pull_requests.py     # PR CRUD (sync + async)
  repositories.py      # Repository create/delete/info (sync + async)
```

## Testing

```bash
# Requires GITHUB_TOKEN -- skipped when absent
uv run pytest src/codomyrmex/tests/unit/git_operations/ -v -k github
```

## Navigation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../../README.md) | `git_operations` module overview |
