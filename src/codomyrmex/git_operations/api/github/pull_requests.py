"""GitHub API pull request operations."""

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

def create_pull_request(
    repo_owner: str,
    repo_name: str,
    head_branch: str,
    base_branch: str,
    title: str,
    body: str = "",
    github_token: str | None = None,
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
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error creating PR: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def get_pull_requests(
    repo_owner: str,
    repo_name: str,
    state: str = "open",
    github_token: str | None = None,
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
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error fetching PRs: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def get_pull_request(
    repo_owner: str, repo_name: str, pr_number: int, github_token: str | None = None
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
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error fetching PR #{pr_number}: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_list_pull_requests(
    repo_owner: str,
    repo_name: str,
    state: str = "open",
    github_token: str | None = None,
) -> list[dict]:
    """
    Get pull requests for a repository asynchronously.

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

    logger.info(f"[ASYNC] Fetching {state} PRs from {repo_owner}/{repo_name}")

    status, data = await _async_request(
        "GET",
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls",
        headers,
        params=params,
    )

    if status == 200:
        prs = data
        logger.info(f"[ASYNC] Found {len(prs)} {state} PRs")

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
        error_msg = f"Failed to fetch PRs: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_create_pull_request(
    repo_owner: str,
    repo_name: str,
    head_branch: str,
    base_branch: str,
    title: str,
    body: str = "",
    github_token: str | None = None,
) -> dict:
    """
    Create a pull request asynchronously.

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
        f"[ASYNC] Creating PR in {repo_owner}/{repo_name}: {head_branch} -> {base_branch}"
    )

    status, data = await _async_request(
        "POST",
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls",
        headers,
        json_data=pr_data,
    )

    if status == 201:
        pr_info = data
        logger.info(
            f"[ASYNC] Successfully created PR #{pr_info['number']}: {pr_info['title']}"
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
        error_msg = f"Failed to create PR: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_get_pull_request(
    repo_owner: str, repo_name: str, pr_number: int, github_token: str | None = None
) -> dict:
    """
    Get a specific pull request asynchronously.

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

    logger.info(f"[ASYNC] Fetching PR #{pr_number} from {repo_owner}/{repo_name}")

    status, data = await _async_request(
        "GET",
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}",
        headers,
    )

    if status == 200:
        pr = data
        logger.info(f"[ASYNC] Found PR #{pr['number']}: {pr['title']}")

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
        error_msg = f"Failed to fetch PR #{pr_number}: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

