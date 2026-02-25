"""GitHub API issue operations."""

import requests

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .base import (
    GitHubAPIError,
    _async_request,
    _get_github_headers,
    _validate_github_token,
)

logger = get_logger(__name__)

def create_issue(
    owner: str,
    repo_name: str,
    title: str,
    body: str = "",
    labels: list[str] = None,
    assignees: list[str] = None,
    github_token: str | None = None,
) -> dict:
    """Create a new issue."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    data = {"title": title, "body": body}
    if labels:
        data["labels"] = labels
    if assignees:
        data["assignees"] = assignees

    logger.info(f"Creating issue in {owner}/{repo_name}: {title}")

    try:
        response = requests.post(
            f"https://api.github.com/repos/{owner}/{repo_name}/issues",
            headers=headers,
            json=data,
        )

        if response.status_code == 201:
            issue = response.json()
            logger.info(f"Successfully created issue #{issue['number']}")
            return issue
        else:
            error_msg = f"Failed to create issue: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error creating issue: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def list_issues(
    owner: str,
    repo_name: str,
    state: str = "open",
    labels: list[str] = None,
    github_token: str | None = None,
) -> list[dict]:
    """List issues in a repository."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    params = {"state": state}
    if labels:
        params["labels"] = ",".join(labels)

    logger.info(f"Listing {state} issues in {owner}/{repo_name}")

    try:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo_name}/issues",
            headers=headers,
            params=params,
        )

        if response.status_code == 200:
            # Issues endpoint returns both issues and PRs. Filter out PRs if desired,
            # though typically 'issues' includes PRs in GitHub's model unless filtered.
            # GitHub API: "Pull requests are issues."
            # To get only issues, check if 'pull_request' key is present in item.
            all_items = response.json()
            issues = [item for item in all_items if "pull_request" not in item]
            logger.info(f"Found {len(issues)} issues")
            return issues
        else:
            error_msg = f"Failed to list issues: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error listing issues: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def close_issue(
    owner: str,
    repo_name: str,
    issue_number: int,
    github_token: str | None = None,
) -> dict:
    """Close an issue."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    data = {"state": "closed"}

    logger.info(f"Closing issue #{issue_number} in {owner}/{repo_name}")

    try:
        response = requests.patch(
            f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}",
            headers=headers,
            json=data,
        )

        if response.status_code == 200:
            logger.info(f"Successfully closed issue #{issue_number}")
            return response.json()
        else:
            error_msg = f"Failed to close issue: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error closing issue: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

def add_comment(
    owner: str,
    repo_name: str,
    issue_number: int,
    body: str,
    github_token: str | None = None,
) -> dict:
    """Add a comment to an issue (or PR)."""
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    data = {"body": body}

    logger.info(f"Adding comment to #{issue_number} in {owner}/{repo_name}")

    try:
        response = requests.post(
            f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/comments",
            headers=headers,
            json=data,
        )

        if response.status_code == 201:
            logger.info(f"Successfully added comment to #{issue_number}")
            return response.json()
        else:
            error_msg = f"Failed to add comment: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise GitHubAPIError(error_msg) from None

    except requests.RequestException as e:
        error_msg = f"Network error adding comment: {e}"
        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_create_issue(
    owner: str,
    repo_name: str,
    title: str,
    body: str = "",
    labels: list[str] | None = None,
    assignees: list[str] | None = None,
    github_token: str | None = None,
) -> dict:
    """
    Create a new issue asynchronously.

    Args:
        owner: Repository owner
        repo_name: Repository name
        title: Issue title
        body: Issue body/description
        labels: List of label names
        assignees: List of assignee usernames
        github_token: GitHub personal access token

    Returns:
        Dictionary containing created issue information

    Raises:
        GitHubAPIError: If issue creation fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    issue_data: dict = {"title": title, "body": body}
    if labels:
        issue_data["labels"] = labels
    if assignees:
        issue_data["assignees"] = assignees

    logger.info(f"[ASYNC] Creating issue in {owner}/{repo_name}: {title}")

    status, data = await _async_request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo_name}/issues",
        headers,
        json_data=issue_data,
    )

    if status == 201:
        issue = data
        logger.info(f"[ASYNC] Successfully created issue #{issue['number']}")
        return issue
    else:
        error_msg = f"Failed to create issue: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_list_issues(
    owner: str,
    repo_name: str,
    state: str = "open",
    labels: list[str] | None = None,
    github_token: str | None = None,
) -> list[dict]:
    """
    List issues in a repository asynchronously.

    Args:
        owner: Repository owner
        repo_name: Repository name
        state: Issue state ("open", "closed", "all")
        labels: Filter by label names
        github_token: GitHub personal access token

    Returns:
        List of issue dictionaries

    Raises:
        GitHubAPIError: If fetching fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    params: dict = {"state": state}
    if labels:
        params["labels"] = ",".join(labels)

    logger.info(f"[ASYNC] Listing {state} issues in {owner}/{repo_name}")

    status, data = await _async_request(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo_name}/issues",
        headers,
        params=params,
    )

    if status == 200:
        all_items = data
        # Filter out pull requests (GitHub API includes PRs in issues endpoint)
        issues = [item for item in all_items if "pull_request" not in item]
        logger.info(f"[ASYNC] Found {len(issues)} issues")
        return issues
    else:
        error_msg = f"Failed to list issues: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_close_issue(
    owner: str,
    repo_name: str,
    issue_number: int,
    github_token: str | None = None,
) -> dict:
    """
    Close an issue asynchronously.

    Args:
        owner: Repository owner
        repo_name: Repository name
        issue_number: Issue number to close
        github_token: GitHub personal access token

    Returns:
        Dictionary containing updated issue information

    Raises:
        GitHubAPIError: If closing fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    logger.info(f"[ASYNC] Closing issue #{issue_number} in {owner}/{repo_name}")

    status, data = await _async_request(
        "PATCH",
        f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}",
        headers,
        json_data={"state": "closed"},
    )

    if status == 200:
        logger.info(f"[ASYNC] Successfully closed issue #{issue_number}")
        return data
    else:
        error_msg = f"Failed to close issue: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

async def async_add_comment(
    owner: str,
    repo_name: str,
    issue_number: int,
    body: str,
    github_token: str | None = None,
) -> dict:
    """
    Add a comment to an issue (or PR) asynchronously.

    Args:
        owner: Repository owner
        repo_name: Repository name
        issue_number: Issue or PR number
        body: Comment body
        github_token: GitHub personal access token

    Returns:
        Dictionary containing created comment information

    Raises:
        GitHubAPIError: If adding comment fails
    """
    token = _validate_github_token(github_token)
    headers = _get_github_headers(token)

    logger.info(f"[ASYNC] Adding comment to #{issue_number} in {owner}/{repo_name}")

    status, data = await _async_request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/comments",
        headers,
        json_data={"body": body},
    )

    if status == 201:
        logger.info(f"[ASYNC] Successfully added comment to #{issue_number}")
        return data
    else:
        error_msg = f"Failed to add comment: {status}"
        if isinstance(data, dict):
            error_msg += f" - {data.get('message', str(data))}"
        elif data:
            error_msg += f" - {data}"

        logger.error(error_msg)
        raise GitHubAPIError(error_msg) from None

