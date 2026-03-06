# GitHub API Client - Agent Coordination

> **Codomyrmex v1.1.4** | Sub-module of `git_operations.api` | March 2026

## Overview

The `github` sub-module gives agents programmatic access to GitHub repositories,
pull requests, and issues through both synchronous and asynchronous interfaces.
All operations require a valid GitHub personal access token provided via the
`GITHUB_TOKEN` environment variable or passed explicitly.

## Key Files

| File | Purpose |
|------|---------|
| `base.py` | `GitHubAPIError`, token validation, auth header construction, async HTTP helper |
| `repositories.py` | Create, delete, and inspect repositories (sync + async) |
| `pull_requests.py` | Create, list, and retrieve pull requests (sync + async) |
| `issues.py` | Create, list, close issues and add comments (sync + async) |
| `__init__.py` | Re-exports all 21 public symbols |

## MCP Tools Available

No MCP tools defined in this sub-module. GitHub operations are available to
agents through direct Python imports or via higher-level `git_operations` MCP
tools.

## Agent Instructions

1. **Always validate token availability first** -- call
   `_validate_github_token(None)` or check `os.environ.get("GITHUB_TOKEN")`
   before attempting any API call. Missing tokens raise `GitHubAPIError`.
2. **Use async variants in concurrent workflows** -- functions prefixed with
   `async_` use `aiohttp` and do not block the event loop.
3. **Handle `GitHubAPIError` explicitly** -- it is raised for network failures,
   authentication errors, rate limiting, and non-2xx responses.
4. **Repository deletion is destructive** -- `delete_github_repository` is
   trust-gated; ensure PAI trust level is TRUSTED before calling.
5. **Use labels and assignees when creating issues** -- `create_issue` accepts
   `labels: list[str]` and `assignees: list[str]` to keep issues organised.

## Operating Contracts

- Sync functions use the `requests` library; async functions use `aiohttp`.
- All functions that accept a `github_token` parameter fall back to
  `os.environ.get("GITHUB_TOKEN")` when `None` is passed.
- Successful API calls return parsed JSON as Python dicts or lists.
- Non-2xx responses raise `GitHubAPIError` with the status code and response
  body.
- The `_async_request` helper returns `(status_code, response_data)` tuples.

## Common Patterns

```python
# Pattern: create a PR after pushing a branch
from codomyrmex.git_operations.api.github import create_pull_request

pr = create_pull_request(
    repo_owner="myorg",
    repo_name="myrepo",
    head_branch="fix/parser-bug",
    base_branch="main",
    title="Fix parser edge case",
    body="Resolves #42",
)
print(f"PR #{pr['number']}: {pr['html_url']}")
```

```python
# Pattern: async issue listing
import asyncio
from codomyrmex.git_operations.api.github import async_list_issues

issues = asyncio.run(async_list_issues("owner", "repo", state="open"))
```

## PAI Agent Role Access Matrix

| Agent Role | Permitted Operations |
|------------|---------------------|
| Engineer   | Full access -- create/delete repos, PRs, issues, comments |
| Architect  | Read-only -- get repo info, list PRs/issues |
| QATester   | Create issues and comments (bug reports) |

## Navigation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Module overview and quick start |
| [SPEC.md](SPEC.md) | Technical specification |
| [Parent README](../../README.md) | `git_operations` module overview |
