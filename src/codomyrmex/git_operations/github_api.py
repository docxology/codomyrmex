from datetime import datetime
from typing import Optional
import json
import os
import sys

import requests

from codomyrmex.logging_monitoring.logger_config import get_logger






#!/usr/bin/env python3
"""
GitHub API Operations for Codomyrmex Git Operations Module.

This module provides GitHub API integration for repository creation,
pull request management, and other GitHub-specific operations.
"""



# Add project root for sibling module imports if run directly
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    pass
#     sys.path.insert(0, PROJECT_ROOT)  # Removed sys.path manipulation


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


def _validate_github_token(token: Optional[str]) -> str:
    """Validate and return GitHub token, raising error if invalid."""
    if not token:
        token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise GitHubAPIError(
            "GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter."
        )

    return token


def create_github_repository(
    name: str,
    private: bool = True,
    description: str = "",
    github_token: Optional[str] = None,
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
            raise GitHubAPIError(error_msg)

    except requests.RequestException as e:
        error_msg = f"Network error creating repository: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg)


def delete_github_repository(
    owner: str, repo_name: str, github_token: Optional[str] = None
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
            raise GitHubAPIError(error_msg)

    except requests.RequestException as e:
        error_msg = f"Network error deleting repository: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg)


def create_pull_request(
    repo_owner: str,
    repo_name: str,
    head_branch: str,
    base_branch: str,
    title: str,
    body: str = "",
    github_token: Optional[str] = None,
) -> dict:
    """
    Create a pull request.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        head_branch: Source branch for the PR
        base_branch: Target branch for the PR
        title: PR title
        body: PR body/description
        github_token: GitHub personal access token

    Returns:
        Dictionary containing PR information

    Raises:
        GitHubAPIError: If PR creation fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    pr_data = {"title": title, "head": head_branch, "base": base_branch, "body": body}

    logger.info(
        f"Creating PR in {repo_owner}/{repo_name}: {head_branch} -> {base_branch}"
    )

    try:
        response = requests.post(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls",
            headers=headers,
            json=pr_data,
        )

        if response.status_code == 201:
            pr_info = response.json()
            logger.info(
                f"Successfully created PR #{pr_info['number']}: {pr_info['title']}"
            )

            return {
                "success": True,
                "pull_request": {
                    "number": pr_info["number"],
                    "title": pr_info["title"],
                    "body": pr_info["body"],
                    "html_url": pr_info["html_url"],
                    "state": pr_info["state"],
                    "head": {
                        "ref": pr_info["head"]["ref"],
                        "sha": pr_info["head"]["sha"],
                    },
                    "base": {
                        "ref": pr_info["base"]["ref"],
                        "sha": pr_info["base"]["sha"],
                    },
                    "user": pr_info["user"]["login"],
                    "created_at": pr_info["created_at"],
                },
                "created_at": datetime.now().isoformat(),
            }
        else:
            error_msg = f"Failed to create PR: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', response.text)}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f" - {response.text}"

            logger.error(error_msg)
            raise GitHubAPIError(error_msg)

    except requests.RequestException as e:
        error_msg = f"Network error creating PR: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg)


def get_pull_requests(
    repo_owner: str,
    repo_name: str,
    state: str = "open",
    github_token: Optional[str] = None,
) -> list[dict]:
    """
    Get pull requests for a repository.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        state: PR state ("open", "closed", "all")
        github_token: GitHub personal access token

    Returns:
        List of PR dictionaries

    Raises:
        GitHubAPIError: If fetching fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    params = {"state": state}

    logger.info(f"Fetching {state} PRs from {repo_owner}/{repo_name}")

    try:
        response = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            prs = response.json()
            logger.info(f"Found {len(prs)} {state} PRs")

            return [
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "body": pr["body"],
                    "html_url": pr["html_url"],
                    "state": pr["state"],
                    "head": {"ref": pr["head"]["ref"], "sha": pr["head"]["sha"]},
                    "base": {"ref": pr["base"]["ref"], "sha": pr["base"]["sha"]},
                    "user": pr["user"]["login"],
                    "created_at": pr["created_at"],
                    "updated_at": pr["updated_at"],
                }
                for pr in prs
            ]
        else:
            error_msg = f"Failed to fetch PRs: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', response.text)}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f" - {response.text}"

            logger.error(error_msg)
            raise GitHubAPIError(error_msg)

    except requests.RequestException as e:
        error_msg = f"Network error fetching PRs: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg)


def get_pull_request(
    repo_owner: str, repo_name: str, pr_number: int, github_token: Optional[str] = None
) -> dict:
    """
    Get a specific pull request.

    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        pr_number: PR number
        github_token: GitHub personal access token

    Returns:
        Dictionary containing detailed PR information

    Raises:
        GitHubAPIError: If fetching fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    logger.info(f"Fetching PR #{pr_number} from {repo_owner}/{repo_name}")

    try:
        response = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}",
            headers=headers,
        )

        if response.status_code == 200:
            pr = response.json()
            logger.info(f"Found PR #{pr['number']}: {pr['title']}")

            return {
                "number": pr["number"],
                "title": pr["title"],
                "body": pr["body"],
                "html_url": pr["html_url"],
                "state": pr["state"],
                "merged": pr["merged"],
                "mergeable": pr["mergeable"],
                "head": {"ref": pr["head"]["ref"], "sha": pr["head"]["sha"]},
                "base": {"ref": pr["base"]["ref"], "sha": pr["base"]["sha"]},
                "user": pr["user"]["login"],
                "created_at": pr["created_at"],
                "updated_at": pr["updated_at"],
                "merged_at": pr["merged_at"],
                "comments": pr["comments"],
                "review_comments": pr["review_comments"],
                "commits": pr["commits"],
                "additions": pr["additions"],
                "deletions": pr["deletions"],
                "changed_files": pr["changed_files"],
            }
        else:
            error_msg = f"Failed to fetch PR #{pr_number}: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', response.text)}"
                except (ValueError, json.JSONDecodeError):
                    error_msg += f" - {response.text}"

            logger.error(error_msg)
            raise GitHubAPIError(error_msg)

    except requests.RequestException as e:
        error_msg = f"Network error fetching PR #{pr_number}: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg)


def get_repository_info(
    repo_owner: str, repo_name: str, github_token: Optional[str] = None
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
            raise GitHubAPIError(error_msg)

    except requests.RequestException as e:
        error_msg = f"Network error fetching repository info: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg)


if __name__ == "__main__":
    """Example usage and testing."""
    logger.info("GitHub API module loaded successfully")

    # Example: Check if GitHub token is available
    try:
        token = _validate_github_token(None)
        logger.info("GitHub token found and validated")

        # Example: Get repository info (if token is available)
        # repo_info = get_repository_info("octocat", "Hello-World", token)
        # logger.info(f"Example repository info: {repo_info['full_name']}")

    except GitHubAPIError as e:
        logger.warning(f"GitHub token not available: {e}")
        logger.info(
            "Set GITHUB_TOKEN environment variable to test GitHub API functions"
        )
