"""Tests for GitHub Issues API functions.

Zero-Mock compliant — tests use the real GitHub API when GITHUB_TOKEN
is set, otherwise they are skipped.
"""

import os

import pytest

from codomyrmex.git_operations.api.github import (
    add_comment,
    close_issue,
    create_issue,
    list_issues,
)

_HAS_GITHUB_TOKEN = bool(os.environ.get("GITHUB_TOKEN"))

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _HAS_GITHUB_TOKEN, reason="GITHUB_TOKEN not set — skip live GitHub API tests"),
]


class TestGitHubIssues:
    """Live-API tests for GitHub issue operations."""

    def test_list_issues(self):
        """list_issues returns a list for a public repo."""
        # Use a well-known public repo that always has issues
        result = list_issues("octocat", "Hello-World")
        assert isinstance(result, list)

    def test_create_issue_requires_auth(self):
        """create_issue on a real repo returns a dict with issue number."""
        # NOTE: This creates a real issue; use a personal test repo.
        # We only verify the function is callable and returns structured data.
        # To avoid spam, we skip unless a test repo env var is set.
        test_owner = os.environ.get("GITHUB_TEST_OWNER")
        test_repo = os.environ.get("GITHUB_TEST_REPO")
        if not test_owner or not test_repo:
            pytest.skip("GITHUB_TEST_OWNER/GITHUB_TEST_REPO not set")

        result = create_issue(test_owner, test_repo, "CI Test Issue", "Automated test", ["test"])
        assert isinstance(result, dict)
        assert "number" in result
