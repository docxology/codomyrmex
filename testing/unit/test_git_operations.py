#!/usr/bin/env python3
"""
Unit tests for the Git Operations module.

Comprehensive test coverage including:
- Basic functionality tests
- Edge cases and error conditions
- Concurrent operations
- Repository state management
- Branch and merge operations
"""

import unittest
import tempfile
import os
import sys
import shutil
import subprocess
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import git operations functions
try:
    from codomyrmex.git_operations.git_manager import (
        check_git_availability,
        is_git_repository,
        get_current_branch,
        get_status,
        get_commit_history,
        add_files,
        commit_changes,
        create_branch,
        switch_branch,
        get_branches,
        merge_branch,
        pull_changes,
        push_changes,
        get_remote_info,
        get_diff,
        get_file_history,
        check_merge_conflicts,
        resolve_merge_conflicts,
        get_stash_list,
        stash_changes,
        unstash_changes,
        reset_changes,
        clean_repository,
        get_repository_info,
        validate_git_config,
        get_hook_status,
        update_submodules
    )
    FULL_GIT_AVAILABLE = True
except ImportError:
    # Fallback to basic imports if full module not available
    try:
        from codomyrmex.git_operations.git_manager import (
            check_git_availability,
            is_git_repository,
            get_current_branch,
            get_status
        )
        FULL_GIT_AVAILABLE = False
    except ImportError:
        FULL_GIT_AVAILABLE = False


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

    @unittest.skipUnless(FULL_GIT_AVAILABLE, "Full git operations not available")
    def test_create_and_switch_branches(self):
        """Test creating and switching branches."""
        from codomyrmex.git_operations.git_manager import create_branch, switch_branch, get_branches

        # Test in non-repository directory (should fail)
        result = create_branch("test-branch", repository_path=self.test_dir)
        self.assertFalse(result)

        result = switch_branch("test-branch", repository_path=self.test_dir)
        self.assertFalse(result)

        branches = get_branches(repository_path=self.test_dir)
        self.assertEqual(branches, [])

    @unittest.skipUnless(FULL_GIT_AVAILABLE, "Full git operations not available")
    def test_branch_operations_edge_cases(self):
        """Test branch operations with edge cases."""
        from codomyrmex.git_operations.git_manager import create_branch, switch_branch

        # Test with invalid branch names
        invalid_names = ["", " ", ".lock", "HEAD", "refs/heads/main"]

        for name in invalid_names:
            with self.subTest(branch_name=name):
                result = create_branch(name, repository_path=self.test_dir)
                self.assertFalse(result)

    @unittest.skipUnless(FULL_GIT_AVAILABLE, "Full git operations not available")
    def test_merge_operations(self):
        """Test merge operations."""
        from codomyrmex.git_operations.git_manager import merge_branch, check_merge_conflicts

        # Test in non-repository directory
        result = merge_branch("feature-branch", repository_path=self.test_dir)
        self.assertFalse(result)

        conflicts = check_merge_conflicts(repository_path=self.test_dir)
        self.assertIsInstance(conflicts, (bool, list))

    @unittest.skipUnless(FULL_GIT_AVAILABLE, "Full git operations not available")
    def test_remote_operations(self):
        """Test remote repository operations."""
        from codomyrmex.git_operations.git_manager import pull_changes, push_changes, get_remote_info

        # Test in non-repository directory
        result = pull_changes(repository_path=self.test_dir)
        self.assertFalse(result)

        result = push_changes(repository_path=self.test_dir)
        self.assertFalse(result)

        remote_info = get_remote_info(repository_path=self.test_dir)
        self.assertIsInstance(remote_info, (dict, type(None)))

    @unittest.skipUnless(FULL_GIT_AVAILABLE, "Full git operations not available")
    def test_stash_operations(self):
        """Test git stash operations."""
        from codomyrmex.git_operations.git_manager import stash_changes, unstash_changes, get_stash_list

        # Test in non-repository directory
        result = stash_changes("Test stash", repository_path=self.test_dir)
        self.assertFalse(result)

        result = unstash_changes(repository_path=self.test_dir)
        self.assertFalse(result)

        stashes = get_stash_list(repository_path=self.test_dir)
        self.assertIsInstance(stashes, list)

    @unittest.skipUnless(FULL_GIT_AVAILABLE, "Full git operations not available")
    def test_reset_and_clean_operations(self):
        """Test reset and clean operations."""
        from codomyrmex.git_operations.git_manager import reset_changes, clean_repository

        # Test in non-repository directory
        result = reset_changes("--hard", repository_path=self.test_dir)
        self.assertFalse(result)

        result = clean_repository(repository_path=self.test_dir)
        self.assertFalse(result)

    def test_repository_validation(self):
        """Test repository validation functions."""
        # Test with various directory types
        test_cases = [
            (self.test_dir, False),  # Empty directory
            ("/nonexistent/path", False),  # Non-existent path
            ("/", False),  # Root directory (usually not a git repo)
        ]

        for path, expected in test_cases:
            with self.subTest(path=path):
                result = is_git_repository(path)
                if expected is False:
                    self.assertFalse(result)
                # True case depends on actual repository state

    def test_git_config_validation(self):
        """Test git configuration validation."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import validate_git_config

        # Test in non-repository directory
        result = validate_git_config(repository_path=self.test_dir)
        self.assertIsInstance(result, dict)

        # Should have validation results
        self.assertIn("valid", result)
        self.assertIsInstance(result["valid"], bool)

    def test_hook_status_checking(self):
        """Test git hooks status checking."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import get_hook_status

        # Test in non-repository directory
        hooks = get_hook_status(repository_path=self.test_dir)
        self.assertIsInstance(hooks, (dict, list))

    def test_submodule_operations(self):
        """Test git submodule operations."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import update_submodules

        # Test in non-repository directory
        result = update_submodules(repository_path=self.test_dir)
        self.assertIsInstance(result, (bool, dict))

    def test_file_operations_edge_cases(self):
        """Test file operations with edge cases."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import add_files, get_file_history, get_diff

        # Test with non-existent files
        result = add_files(["nonexistent.txt"], repository_path=self.test_dir)
        self.assertFalse(result)

        # Test with empty file list
        result = add_files([], repository_path=self.test_dir)
        self.assertFalse(result)

        # Test file history for non-existent file
        history = get_file_history("nonexistent.txt", repository_path=self.test_dir)
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)

        # Test diff operations
        diff = get_diff(repository_path=self.test_dir)
        self.assertIsInstance(diff, (str, list, dict))

    def test_commit_operations_comprehensive(self):
        """Comprehensive test of commit operations."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import commit_changes

        # Test with various commit messages
        test_messages = [
            "Normal commit message",
            "",  # Empty message
            "Message with\nnewlines",
            "Very long message: " + "x" * 200,
        ]

        for message in test_messages:
            with self.subTest(message=message[:50]):
                result = commit_changes(message, repository_path=self.test_dir)
                self.assertFalse(result)  # Should fail in non-repo directory

    def test_concurrent_git_operations(self):
        """Test concurrent git operations."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import get_status

        results = []

        def worker():
            """Worker function for concurrent testing."""
            try:
                status = get_status(repository_path=self.test_dir)
                results.append(("success", status))
            except Exception as e:
                results.append(("error", str(e)))

        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join(timeout=5.0)

        # Verify results
        self.assertEqual(len(results), 5)
        for result in results:
            status, data = result
            self.assertEqual(status, "success")
            self.assertIsInstance(data, dict)

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling."""
        # Test with various invalid inputs
        invalid_paths = [
            None,
            "",
            "/dev/null",
            "/nonexistent/path/that/does/not/exist",
            "/etc/passwd",  # Usually not a git repo
        ]

        for path in invalid_paths:
            with self.subTest(path=path):
                # Test various operations with invalid paths
                result = is_git_repository(path)
                self.assertIsInstance(result, bool)

                if FULL_GIT_AVAILABLE:
                    from codomyrmex.git_operations.git_manager import get_status
                    status = get_status(path)
                    self.assertIsInstance(status, dict)
                    self.assertIn("error", status)

    def test_git_command_timeout_handling(self):
        """Test handling of git command timeouts."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        # Test operations that might timeout
        from codomyrmex.git_operations.git_manager import get_commit_history

        # Request large history which might be slow
        history = get_commit_history(limit=1000, repository_path=self.test_dir)
        self.assertIsInstance(history, list)

    def test_large_repository_handling(self):
        """Test handling of potentially large repository operations."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        from codomyrmex.git_operations.git_manager import get_repository_info

        # Test in non-repository directory
        info = get_repository_info(repository_path=self.test_dir)
        self.assertIsInstance(info, dict)

        # Should handle the case gracefully
        if "error" in info:
            self.assertIsInstance(info["error"], str)

    @patch('subprocess.run')
    def test_git_command_failure_simulation(self, mock_subprocess):
        """Test handling of git command failures."""
        # Mock subprocess to simulate git command failures
        mock_subprocess.side_effect = subprocess.CalledProcessError(128, 'git', 'fatal: not a git repository')

        # Test various operations that should handle the error
        result = check_git_availability()
        # This should still work as it tests git availability differently

        result = is_git_repository(self.test_dir)
        self.assertFalse(result)

        if FULL_GIT_AVAILABLE:
            from codomyrmex.git_operations.git_manager import get_status
            status = get_status(repository_path=self.test_dir)
            self.assertIn("error", status)

    def test_memory_usage_with_large_outputs(self):
        """Test memory usage when handling large git outputs."""
        if not FULL_GIT_AVAILABLE:
            self.skipTest("Full git operations not available")

        # Test operations that might return large outputs
        from codomyrmex.git_operations.git_manager import get_commit_history, get_diff

        # These should handle large outputs gracefully
        history = get_commit_history(limit=100, repository_path=self.test_dir)
        self.assertIsInstance(history, list)

        diff = get_diff(repository_path=self.test_dir)
        self.assertIsInstance(diff, (str, list, dict))

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters in git operations."""
        # Test with unicode commit messages, file names, etc.
        unicode_message = "Test commit with unicode: 🚀 αβγδε"

        if FULL_GIT_AVAILABLE:
            from codomyrmex.git_operations.git_manager import commit_changes
            result = commit_changes(unicode_message, repository_path=self.test_dir)
            self.assertFalse(result)  # Should fail gracefully in non-repo

    def test_repository_state_transitions(self):
        """Test repository state transitions and edge cases."""
        # This would typically require setting up actual git repositories
        # For now, test the functions handle various states

        states_to_test = [
            "nonexistent_directory",
            "empty_directory",
            "directory_with_files",
        ]

        for state in states_to_test:
            with self.subTest(state=state):
                if state == "empty_directory":
                    path = self.test_dir
                elif state == "directory_with_files":
                    # Create some files
                    test_file = os.path.join(self.test_dir, "test.txt")
                    with open(test_file, 'w') as f:
                        f.write("test content")
                    path = self.test_dir
                else:
                    path = "/nonexistent/path"

                # Test various operations
                result = is_git_repository(path)
                self.assertIsInstance(result, bool)

                if FULL_GIT_AVAILABLE:
                    from codomyrmex.git_operations.git_manager import get_status
                    status = get_status(path)
                    self.assertIsInstance(status, dict)

    def test_git_operations_idempotency(self):
        """Test that git operations are idempotent where appropriate."""
        # Operations like get_status should be idempotent
        result1 = get_status(repository_path=self.test_dir)
        result2 = get_status(repository_path=self.test_dir)

        # Results should be consistent (both should indicate non-repo or same error)
        self.assertEqual(result1.get("error"), result2.get("error"))

        if FULL_GIT_AVAILABLE:
            from codomyrmex.git_operations.git_manager import get_branches
            branches1 = get_branches(repository_path=self.test_dir)
            branches2 = get_branches(repository_path=self.test_dir)
            self.assertEqual(branches1, branches2)


if __name__ == '__main__':
    unittest.main()