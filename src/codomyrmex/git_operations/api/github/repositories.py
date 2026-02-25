"""GitHub API repository operations."""

import json
from datetime import datetime

import requests

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .base import (
    GitHubAPIError,
    _async_request,
    _get_github_headers,
    _validate_github_token,
)

logger = get_logger(__name__)

def create_github_repository(
    name: str,
    private: bool = True,
    description: str = "",
    github_token: str | None = None,
    auto_init: bool = True,
    gitignore_template: str = "Python",
    license_template: str = "mit",
) -> dict:
    """
    Create a new GitHub repository.

    Args:
        name: Repository name
        private: Whether the repository should be private (default True)
        description: Repository description
        github_token: GitHub personal access token (or use GITHUB_TOKEN env var)
        auto_init: Whether to initialize the repository with a README
        gitignore_template: Gitignore template to use
        license_template: License template to use

    Returns:
        Dictionary containing repository information

    Raises:
        GitHubAPIError: If repository creation fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    # Prepare repository data
    repo_data = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": auto_init,
    }

    if gitignore_template:
        repo_data["gitignore_template"] = gitignore_template

    if license_template:
        repo_data["license_template"] = license_template

    logger.info(f"Creating GitHub repository: {name} (private: {private})")

    try:
        response = requests.post(
            "https://api.github.com/user/repos", headers=headers, json=repo_data
        )

        if response.status_code == 201:
            repo_info = response.json()
            logger.info(f"Successfully created repository: {repo_info['full_name']}")

            return {
                "success": True,
                "repository": {
                    "name": repo_info["name"],
                    "full_name": repo_info["full_name"],
                    "html_url": repo_info["html_url"],
                    "clone_url": repo_info["clone_url"],
                    "ssh_url": repo_info["ssh_url"],
                    "private": repo_info["private"],
                    "description": repo_info["description"],
                    "default_branch": repo_info["default_branch"],
                },
                "created_at": datetime.now().isoformat(),
            }
        else:
            error_msg = f"Failed to create repository: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', response.text)}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f" - {response.text}"

            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error creating repository: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def delete_github_repository(
    owner: str, repo_name: str, github_token: str | None = None
) -> bool:
    """
    Delete a GitHub repository.

    Args:
        owner: Repository owner (username or organization)
        repo_name: Repository name
        github_token: GitHub personal access token

    Returns:
        True if successful, False otherwise

    Raises:
        GitHubAPIError: If deletion fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    logger.info(f"Deleting GitHub repository: {owner}/{repo_name}")

    try:
        response = requests.delete(
            f"https://api.github.com/repos/{owner}/{repo_name}", headers=headers
        )

        if response.status_code == 204:
            logger.info(f"Successfully deleted repository: {owner}/{repo_name}")
            return True
        else:
            error_msg = f"Failed to delete repository: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', response.text)}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f" - {response.text}"

            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error deleting repository: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def get_repository_info(
    repo_owner: str, repo_name: str, github_token: str | None = None
) -> dict:
    """
    Get detailed repository information.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        github_token: GitHub personal access token

    Returns:
        Dictionary containing repository information

    Raises:
        GitHubAPIError: If fetching fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    logger.info(f"Fetching repository info for {repo_owner}/{repo_name}")

    try:
        response = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers
        )

        if response.status_code == 200:
            repo = response.json()
            logger.info(f"Found repository: {repo['full_name']}")

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
        else:
            error_msg = f"Failed to fetch repository info: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', response.text)}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f" - {response.text}"

            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error fetching repository info: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_get_repo_info(
    repo_owner: str, repo_name: str, github_token: str | None = None
) -> dict:
    """
    Get detailed repository information asynchronously.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        github_token: GitHub personal access token

    Returns:
        Dictionary containing repository information

    Raises:
        GitHubAPIError: If fetching fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    logger.info(f"[ASYNC] Fetching repository info for {repo_owner}/{repo_name}")

    status, data = await _async_request(
        "GET",
        f"https://api.github.com/repos/{repo_owner}/{repo_name}",
        headers,
    )

    if status == 200:
        repo = data
        logger.info(f"[ASYNC] Found repository: {repo['full_name']}")

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
    else:
        error_msg = f"Failed to fetch repository info: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

