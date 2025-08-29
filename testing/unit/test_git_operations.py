#!/usr/bin/env python3
"""
Unit tests for the Git Operations module.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.git_operations.git_manager import (
    check_git_availability,
    is_git_repository,
    get_current_branch,
    get_status
)


class TestGitOperations(unittest.TestCase):
    """Test cases for git operations functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_check_git_availability(self):
        """Test Git availability checking."""
        result = check_git_availability()
        self.assertIsInstance(result, bool)

    def test_is_git_repository(self):
        """Test Git repository detection."""
        # Test non-repository directory
        self.assertFalse(is_git_repository(self.test_dir))

        # Test current directory (should be a repo if running from project)
        current_dir_is_repo = is_git_repository()
        self.assertIsInstance(current_dir_is_repo, bool)

    def test_get_current_branch(self):
        """Test getting current branch."""
        # Test in non-repository directory
        branch = get_current_branch(self.test_dir)
        self.assertIsNone(branch)

        # Test in current directory
        current_branch = get_current_branch()
        if is_git_repository():  # Only test if we're in a repo
            self.assertIsInstance(current_branch, (str, type(None)))

    def test_get_status(self):
        """Test getting repository status."""
        # Test in non-repository directory
        status = get_status(self.test_dir)
        self.assertIn("error", status)

        # Test in current directory
        current_status = get_status()
        self.assertIsInstance(current_status, dict)

        if is_git_repository():
            expected_keys = ["modified", "added", "deleted", "renamed", "untracked", "clean"]
            for key in expected_keys:
                self.assertIn(key, current_status)

    def test_get_commit_history(self):
        """Test getting commit history."""
        from codomyrmex.git_operations.git_manager import get_commit_history

        # Test in non-repository directory
        history = get_commit_history(repository_path=self.test_dir)
        self.assertEqual(history, [])

        # Test in current directory
        current_history = get_commit_history(limit=5)
        self.assertIsInstance(current_history, list)

        if is_git_repository():
            for commit in current_history:
                if commit:  # Skip empty commits
                    expected_keys = ["hash", "author_name", "author_email", "date", "message"]
                    for key in expected_keys:
                        self.assertIn(key, commit)

    def test_add_files(self):
        """Test adding files to staging area."""
        from codomyrmex.git_operations.git_manager import add_files

        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")

        # Test in non-repository directory (should fail)
        result = add_files([os.path.basename(test_file)], repository_path=self.test_dir)
        self.assertFalse(result)

    def test_commit_changes(self):
        """Test committing changes."""
        from codomyrmex.git_operations.git_manager import commit_changes

        # Test in non-repository directory (should fail)
        result = commit_changes("Test commit", repository_path=self.test_dir)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()