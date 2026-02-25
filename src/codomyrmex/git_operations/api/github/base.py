"""GitHub API base functionality."""

import json
import os

import aiohttp

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""

    pass

def _get_github_headers(token: str) -> dict[str, str]:
    """Get GitHub API headers with authentication."""
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

def _validate_github_token(token: str | None) -> str:
    """Validate and return GitHub token, raising error if invalid."""
    if not token:
        token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise GitHubAPIError(
            "GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter."
        )

    return token

async def _async_request(
    method: str,
    url: str,
    headers: dict[str, str],
    json_data: dict | None = None,
    params: dict | None = None,
    timeout: int = 30,
) -> tuple[int, dict | list | str]:
    """
    Make an async HTTP request using aiohttp.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE)
        url: Request URL
        headers: Request headers
        json_data: JSON payload for POST/PATCH requests
        params: Query parameters
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status_code, response_data)

    Raises:
        GitHubAPIError: If network error occurs
    """
    try:
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            kwargs = {"headers": headers}
            if json_data is not None:
                kwargs["json"] = json_data
            if params is not None:
                kwargs["params"] = params

            async with session.request(method, url, **kwargs) as response:
                status = response.status
                try:
                    data = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    data = await response.text()
                return status, data
    except aiohttp.ClientError as e:
        raise GitHubAPIError(f"Network error: {e}") from None

