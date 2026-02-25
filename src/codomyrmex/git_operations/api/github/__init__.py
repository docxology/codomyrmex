"""GitHub API Operations for Codomyrmex Git Operations Module.

Provides programmatic access to GitHub repositories, pull requests, issues,
and more. Synchronous and aiohttp-based asynchronous operations are available.
"""

from .base import (
    GitHubAPIError,
    _async_request,
    _get_github_headers,
    _validate_github_token,
)
from .issues import (
    add_comment,
    async_add_comment,
    async_close_issue,
    async_create_issue,
    async_list_issues,
    close_issue,
    create_issue,
    list_issues,
)
from .pull_requests import (
    async_create_pull_request,
    async_get_pull_request,
    async_list_pull_requests,
    create_pull_request,
    get_pull_request,
    get_pull_requests,
)
from .repositories import (
    async_get_repo_info,
    create_github_repository,
    delete_github_repository,
    get_repository_info,
)

__all__ = [
    "GitHubAPIError",
    "_get_github_headers",
    "_validate_github_token",
    "_async_request",
    "create_github_repository",
    "delete_github_repository",
    "get_repository_info",
    "async_get_repo_info",
    "create_pull_request",
    "get_pull_requests",
    "get_pull_request",
    "async_list_pull_requests",
    "async_create_pull_request",
    "async_get_pull_request",
    "create_issue",
    "list_issues",
    "close_issue",
    "add_comment",
    "async_create_issue",
    "async_list_issues",
    "async_close_issue",
    "async_add_comment",
]
