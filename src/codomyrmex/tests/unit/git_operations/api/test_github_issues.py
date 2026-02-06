import unittest
from unittest.mock import patch

import pytest

from codomyrmex.git_operations.api.github import (
    add_comment,
    close_issue,
    create_issue,
    list_issues,
)


@pytest.mark.unit
class TestGitHubIssues(unittest.TestCase):

    @patch('codomyrmex.git_operations.api.github.requests.post')
    @patch('codomyrmex.git_operations.api.github._validate_github_token')
    def test_create_issue(self, mock_validate, mock_post):
        mock_validate.return_value = "fake_token"
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"number": 1, "title": "Test Issue"}

        result = create_issue("owner", "repo", "Test Issue", "Body", ["bug"])

        self.assertEqual(result["number"], 1)
        mock_post.assert_called_with(
            "https://api.github.com/repos/owner/repo/issues",
            headers={
                "Authorization": "token fake_token",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            },
            json={"title": "Test Issue", "body": "Body", "labels": ["bug"]}
        )

    @patch('codomyrmex.git_operations.api.github.requests.get')
    @patch('codomyrmex.git_operations.api.github._validate_github_token')
    def test_list_issues(self, mock_validate, mock_get):
        mock_validate.return_value = "fake_token"
        mock_get.return_value.status_code = 200
        # Return mix of issues and PRs (PRs have pull_request key)
        mock_get.return_value.json.return_value = [
            {"number": 1, "title": "Issue 1"},
            {"number": 2, "title": "PR 1", "pull_request": {}}
        ]

        result = list_issues("owner", "repo")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["number"], 1)

    @patch('codomyrmex.git_operations.api.github.requests.patch')
    @patch('codomyrmex.git_operations.api.github._validate_github_token')
    def test_close_issue(self, mock_validate, mock_patch):
        mock_validate.return_value = "fake_token"
        mock_patch.return_value.status_code = 200
        mock_patch.return_value.json.return_value = {"number": 1, "state": "closed"}

        result = close_issue("owner", "repo", 1)

        self.assertEqual(result["state"], "closed")
        mock_patch.assert_called_with(
            "https://api.github.com/repos/owner/repo/issues/1",
            headers={
                "Authorization": "token fake_token",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            },
            json={"state": "closed"}
        )

    @patch('codomyrmex.git_operations.api.github.requests.post')
    @patch('codomyrmex.git_operations.api.github._validate_github_token')
    def test_add_comment(self, mock_validate, mock_post):
        mock_validate.return_value = "fake_token"
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"id": 123, "body": "Comment"}

        result = add_comment("owner", "repo", 1, "Comment")

        self.assertEqual(result["id"], 123)
        mock_post.assert_called_with(
            "https://api.github.com/repos/owner/repo/issues/1/comments",
            headers={
                "Authorization": "token fake_token",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
            },
            json={"body": "Comment"}
        )

if __name__ == '__main__':
    unittest.main()
