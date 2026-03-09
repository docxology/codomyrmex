"""GitHub API repository operations."""

import json
from datetime import datetime

import requests

from codomyrmex.logging_monitoring import get_logger

from .base import (
    GitHubAPIError,
    _async_request,
    _get_github_headers,
    _validate_github_token,
)

logger = get_logger(__name__)


def _extract_repo_fields(repo: dict) -> dict:
    """Extract standard repo fields from a GitHub API response dict."""
    return {
        "name": repo["name"],
        "full_name": repo["full_name"],
        "html_url": repo["html_url"],
        "clone_url": repo["clone_url"],
        "ssh_url": repo["ssh_url"],
        "private": repo["private"],
        "description": repo["description"],
        "default_branch": repo["default_branch"],
        "owner": repo["owner"]["login"],
        "created_at": repo["created_at"],
        "updated_at": repo["updated_at"],
        "language": repo["language"],
        "size": repo["size"],
        "stargazers_count": repo["stargazers_count"],
        "watchers_count": repo["watchers_count"],
        "forks_count": repo["forks_count"],
        "open_issues_count": repo["open_issues_count"],
    }


def _parse_error_response(response_text: str, status_code: int, prefix: str) -> str:
    """Build an error message from a failed API response."""
    msg = f"{prefix}: {status_code}"
    if response_text:
        try:
            data = json.loads(response_text)
            msg += f" - {data.get('message', response_text)}"
        except (ValueError, json.JSONDecodeError):
            msg += f" - {response_text}"
    return msg


def create_github_repository(
    name: str,
    private: bool = True,
    description: str = "",
    github_token: str | None = None,
    auto_init: bool = True,
    gitignore_template: str = "Python",
    license_template: str = "mit",
) -> dict:
    """Create a new GitHub repository."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)
    repo_data: dict = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": auto_init,
    }
    if gitignore_template:
        repo_data["gitignore_template"] = gitignore_template
    if license_template:
        repo_data["license_template"] = license_template

    logger.info("Creating GitHub repository: %s (private: %s)", name, private)
    try:
        response = requests.post(
            "https://api.github.com/user/repos", headers=headers, json=repo_data
        )
        if response.status_code == 201:
            repo_info = response.json()
            logger.info("Successfully created repository: %s", repo_info["full_name"])
            return {
                "success": True,
                "repository": {
                    k: repo_info[k]
                    for k in (
                        "name",
                        "full_name",
                        "html_url",
                        "clone_url",
                        "ssh_url",
                        "private",
                        "description",
                        "default_branch",
                    )
                },
                "created_at": datetime.now().isoformat(),
            }
        error_msg = _parse_error_response(
            response.text, response.status_code, "Failed to create repository"
        )
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None
    except requests.RequestException as e:
        error_msg = f"Network error creating repository: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None


def delete_github_repository(
    owner: str, repo_name: str, github_token: str | None = None
) -> bool:
    """Delete a GitHub repository."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)
    logger.info("Deleting GitHub repository: %s/%s", owner, repo_name)
    try:
        response = requests.delete(
            f"https://api.github.com/repos/{owner}/{repo_name}", headers=headers
        )
        if response.status_code == 204:
            logger.info("Successfully deleted repository: %s/%s", owner, repo_name)
            return True
        error_msg = _parse_error_response(
            response.text, response.status_code, "Failed to delete repository"
        )
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None
    except requests.RequestException as e:
        error_msg = f"Network error deleting repository: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None


def get_repository_info(
    repo_owner: str, repo_name: str, github_token: str | None = None
) -> dict:
    """Get detailed repository information."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)
    logger.info("Fetching repository info for %s/%s", repo_owner, repo_name)
    try:
        response = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers
        )
        if response.status_code == 200:
            repo = response.json()
            logger.info("Found repository: %s", repo["full_name"])
            return _extract_repo_fields(repo)
        error_msg = _parse_error_response(
            response.text, response.status_code, "Failed to fetch repository info"
        )
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None
    except requests.RequestException as e:
        error_msg = f"Network error fetching repository info: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None


async def async_get_repo_info(
    repo_owner: str, repo_name: str, github_token: str | None = None
) -> dict:
    """Get detailed repository information asynchronously."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)
    logger.info("[ASYNC] Fetching repository info for %s/%s", repo_owner, repo_name)
    status, data = await _async_request(
        "GET",
        f"https://api.github.com/repos/{repo_owner}/{repo_name}",
        headers,
    )
    if status == 200:
        logger.info("[ASYNC] Found repository: %s", data["full_name"])
        return _extract_repo_fields(data)
    error_msg = f"Failed to fetch repository info: {status}"
    if isinstance(data, dict):
        error_msg += f" - {data.get('message', str(data))}"
    elif data:
        error_msg += f" - {data}"
    logger.error(error_msg)
    raise GitHubAPIError(error_msg) from None
