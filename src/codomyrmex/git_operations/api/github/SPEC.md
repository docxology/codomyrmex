# GitHub API Client - Specification

> **Codomyrmex v1.1.9** | Sub-module of `git_operations.api` | March 2026

## Overview

This specification defines the interface contracts, authentication model, and
error semantics for the GitHub REST API v3 client in
`git_operations.api.github`.

## Design Principles

- **Zero-Mock Policy**: Tests that exercise GitHub API calls require a live
  `GITHUB_TOKEN`. Use `@pytest.mark.skipif` when the token is absent.
- **Explicit Failure**: All API errors raise `GitHubAPIError` with status code
  and response body -- never return `None` or empty dicts on failure.
- **Dual Interface**: Every operation is available in both synchronous
  (`requests`) and asynchronous (`aiohttp`) variants.
- **Token Flexibility**: Accept token as a function parameter or fall back to
  the `GITHUB_TOKEN` environment variable.

## Architecture

```
github/
  __init__.py          # Re-exports all 21 public symbols
  base.py              # Auth, headers, async HTTP utility, GitHubAPIError
  issues.py            # Issue CRUD (sync: requests, async: aiohttp)
  pull_requests.py     # PR CRUD (sync: requests, async: aiohttp)
  repositories.py      # Repo create/delete/info (sync: requests, async: aiohttp)
```

## Functional Requirements

### FR-1: Authentication (`base.py`)

- `_validate_github_token(token: str | None) -> str`: Return the token if
  non-empty; fall back to `GITHUB_TOKEN` env var; raise `GitHubAPIError` if
  neither is available.
- `_get_github_headers(token: str) -> dict`: Return headers with
  `Authorization: token <t>` and `Accept: application/vnd.github.v3+json`.

### FR-2: Async HTTP (`base.py`)

- `_async_request(method, url, headers, json_data, params, timeout)`:
  Execute an HTTP request via `aiohttp.ClientSession`. Return
  `(status_code, parsed_json_or_text)`. Raise `GitHubAPIError` on
  `aiohttp.ClientError`.

### FR-3: Repository Operations (`repositories.py`)

- `create_github_repository(name, private, description, github_token, auto_init, gitignore_template, license_template) -> dict`
- `delete_github_repository(owner, repo_name, github_token) -> bool`
- `get_repository_info(owner, repo_name, github_token) -> dict`
- `async_get_repo_info(owner, repo_name, github_token) -> dict`

### FR-4: Pull Request Operations (`pull_requests.py`)

- `create_pull_request(repo_owner, repo_name, head_branch, base_branch, title, body, github_token) -> dict`
- `get_pull_requests(repo_owner, repo_name, state, github_token) -> list[dict]`
- `get_pull_request(repo_owner, repo_name, pr_number, github_token) -> dict`
- `async_create_pull_request(...)`, `async_list_pull_requests(...)`,
  `async_get_pull_request(...)` -- async equivalents.

### FR-5: Issue Operations (`issues.py`)

- `create_issue(owner, repo_name, title, body, labels, assignees, github_token) -> dict`
- `list_issues(owner, repo_name, state, github_token) -> list[dict]`
- `close_issue(owner, repo_name, issue_number, github_token) -> dict`
- `add_comment(owner, repo_name, issue_number, body, github_token) -> dict`
- `async_create_issue(...)`, `async_list_issues(...)`, `async_close_issue(...)`,
  `async_add_comment(...)` -- async equivalents.

## Interface Contracts

### GitHubAPIError

```python
class GitHubAPIError(Exception):
    """Raised for authentication failures, non-2xx responses, and network errors."""
    pass
```

### Common Parameters

| Parameter | Type | Default | Semantics |
|-----------|------|---------|-----------|
| `github_token` | `str \| None` | `None` | Falls back to `GITHUB_TOKEN` env var |
| `repo_owner` / `owner` | `str` | required | GitHub organisation or username |
| `repo_name` | `str` | required | Repository name |

### Return Types

- Successful mutations (create, close) return the full GitHub API response as
  a Python dict.
- Listing operations return `list[dict]`.
- `delete_github_repository` returns `bool`.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `requests` | Synchronous HTTP calls to GitHub API |
| `aiohttp` | Asynchronous HTTP calls to GitHub API |
| `codomyrmex.logging_monitoring` | Structured logging |

## Constraints

- GitHub API rate limits apply (5,000 requests/hour for authenticated users).
- `aiohttp` must be installed for async operations (`uv sync --extra git_operations`).
- Token scopes must include `repo` for repository operations and `public_repo`
  for public-only access.
- `delete_github_repository` is irreversible and trust-gated.

## Navigation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Module overview and quick start |
| [AGENTS.md](AGENTS.md) | Agent coordination guidance |
| [Parent README](../../README.md) | `git_operations` module overview |
