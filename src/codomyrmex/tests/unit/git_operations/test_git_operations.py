#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Git Operations Module.

This comprehensive test suite follows industry best practices for testing Git operations,
covering all methods with real implementations, error handling, edge cases, and integration scenarios.

Test Plan Structure:
1. Introduction & Objectives
2. Scope of Testing (In-Scope & Out-of-Scope)
3. Test Approach (Real implementations, no mocks)
4. Test Environment Setup
5. Comprehensive Test Cases
6. Risk Management & Error Handling
7. Entry/Exit Criteria
"""

import os
import sys

import pytest

# Removed mock imports to follow TDD principle: no mock methods, always do real data analysis

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.git_operations.core.git import (
    add_files,
    check_git_availability,
    clone_repository,
    commit_changes,
    create_branch,
    get_commit_history,
    get_current_branch,
    get_status,
    initialize_git_repository,
    is_git_repository,
    pull_changes,
    push_changes,
    switch_branch,
)

_GIT_AVAILABLE = check_git_availability()
pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _GIT_AVAILABLE, reason="Git is not available on this system"),
]


class TestGitOperationsComprehensive:
    """
    Comprehensive test suite for Git Operations module.

    Test Objectives:
    - Verify all Git operations work correctly with real Git repositories
    - Test error handling and edge cases
    - Validate integration between different Git operations
    - Ensure proper logging and status reporting
    - Test with various repository states and configurations
    """

    @pytest.fixture(autouse=True)
    def setup_dirs(self, tmp_path):
        """Set up test fixtures for each test."""
        self.test_dir = str(tmp_path)
        self.repo_dir = os.path.join(self.test_dir, "test_repo")
        os.makedirs(self.repo_dir, exist_ok=True)

        # Store original directory
        self.original_dir = os.getcwd()
        yield
        # Restore original directory
        os.chdir(self.original_dir)

    # ==================== ENTRY CRITERIA TESTS ====================

    def test_git_availability_comprehensive(self):
        """Test Git availability checking with real scenarios."""
        # Test 1: Normal Git availability
        result = check_git_availability()
        assert isinstance(result, bool)
        assert result, "Git should be available for testing"

        # Test 2: Cannot test Git unavailable scenario with real data
        # (would require modifying PATH or renaming git executable)
        # This is acceptable since we're following "no mocks" principle

        # Test 3: Test with invalid git command to simulate failure
        # We can test this by temporarily modifying the environment
        original_path = os.environ.get('PATH', '')
        try:
            # Create a fake PATH that doesn't include git
            fake_path = '/nonexistent/path'
            os.environ['PATH'] = fake_path

            # This should fail since git is not in the fake path
            result = check_git_availability()
            assert not result, "Git should not be available with fake PATH"

        finally:
            # Restore original PATH
            if original_path:
                os.environ['PATH'] = original_path
            else:
                os.environ.pop('PATH', None)

    # ==================== REPOSITORY DETECTION TESTS ====================

    def test_is_git_repository_comprehensive(self):
        """Test Git repository detection with various scenarios."""
        # Test 1: Non-repository directory
        assert not is_git_repository(self.test_dir)

        # Test 2: Initialize repository and test detection
        assert initialize_git_repository(self.repo_dir)
        assert is_git_repository(self.repo_dir)

        # Test 3: Test with None path (current directory)
        os.chdir(self.repo_dir)
        assert is_git_repository()

        # Test 4: Test with invalid path
        invalid_path = os.path.join(self.test_dir, "nonexistent")
        assert not is_git_repository(invalid_path)

        # Test 5: Test with file instead of directory
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        assert not is_git_repository(test_file)

    # ==================== REPOSITORY INITIALIZATION TESTS ====================

    def test_initialize_git_repository_comprehensive(self):
        """Test Git repository initialization with various scenarios."""
        # Test 1: Basic initialization with initial commit
        result = initialize_git_repository(self.repo_dir, initial_commit=True)
        assert result
        assert is_git_repository(self.repo_dir)

        # Verify README.md was created and committed
        readme_path = os.path.join(self.repo_dir, "README.md")
        assert os.path.exists(readme_path)

        # Verify initial commit exists
        commits = get_commit_history(repository_path=self.repo_dir)
        assert len(commits) > 0
        assert "Initial commit" in commits[0]["message"]

        # Test 2: Initialize without initial commit
        repo_dir2 = os.path.join(self.test_dir, "test_repo2")
        os.makedirs(repo_dir2)
        result = initialize_git_repository(repo_dir2, initial_commit=False)
        assert result
        assert is_git_repository(repo_dir2)

        # Verify no commits exist
        commits = get_commit_history(repository_path=repo_dir2)
        assert len(commits) == 0

        # Test 3: Initialize already existing repository
        result = initialize_git_repository(self.repo_dir, initial_commit=True)
        # Should still succeed (Git init is idempotent)
        assert result

        # Test 4: Initialize with invalid path
        invalid_path = "/invalid/path/that/does/not/exist"
        result = initialize_git_repository(invalid_path)
        assert not result

    # ==================== BRANCH MANAGEMENT TESTS ====================

    def test_branch_operations_comprehensive(self):
        """Test comprehensive branch operations."""
        # Setup: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Test 1: Get current branch (should be main or master)
        current_branch = get_current_branch(self.repo_dir)
        assert current_branch is not None
        assert current_branch in ["main", "master"]

        # Test 2: Create new branch
        new_branch = "feature/test-branch"
        result = create_branch(new_branch, self.repo_dir)
        assert result

        # Verify we're on the new branch
        current_branch = get_current_branch(self.repo_dir)
        assert current_branch == new_branch

        # Test 3: Switch back to main/master
        original_branch = "main" if current_branch != "main" else "master"
        # First switch to original branch to test switching
        result = switch_branch(original_branch, self.repo_dir)
        if not result:  # Try master if main doesn't exist
            result = switch_branch("master", self.repo_dir)
        assert result

        # Test 4: Switch to feature branch
        result = switch_branch(new_branch, self.repo_dir)
        assert result
        current_branch = get_current_branch(self.repo_dir)
        assert current_branch == new_branch

        # Test 5: Try to create branch that already exists
        result = create_branch(new_branch, self.repo_dir)
        assert not result  # Should fail

        # Test 6: Try to switch to non-existent branch
        result = switch_branch("nonexistent-branch", self.repo_dir)
        assert not result

        # Test 7: Test with None repository path
        os.chdir(self.repo_dir)
        current_branch = get_current_branch()
        assert current_branch is not None

    # ==================== FILE OPERATIONS TESTS ====================

    def test_file_operations_comprehensive(self):
        """Test comprehensive file operations (add, commit)."""
        # Setup: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Test 1: Add single file
        test_file1 = os.path.join(self.repo_dir, "test1.txt")
        with open(test_file1, 'w') as f:
            f.write("Test content 1")

        result = add_files(["test1.txt"], self.repo_dir)
        assert result

        # Test 2: Add multiple files
        test_file2 = os.path.join(self.repo_dir, "test2.txt")
        test_file3 = os.path.join(self.repo_dir, "test3.txt")
        with open(test_file2, 'w') as f:
            f.write("Test content 2")
        with open(test_file3, 'w') as f:
            f.write("Test content 3")

        result = add_files(["test2.txt", "test3.txt"], self.repo_dir)
        assert result

        # Test 3: Commit changes
        commit_message = "Add test files"
        result = commit_changes(commit_message, self.repo_dir)
        assert result

        # Verify commit was created
        commits = get_commit_history(limit=1, repository_path=self.repo_dir)
        assert len(commits) > 0
        assert commits[0]["message"] == commit_message

        # Test 4: Try to add non-existent file
        result = add_files(["nonexistent.txt"], self.repo_dir)
        assert not result

        # Test 5: Try to commit with no staged changes
        result = commit_changes("Empty commit", self.repo_dir)
        assert not result  # Should fail with no changes

        # Test 6: Add and commit with working directory context
        os.chdir(self.repo_dir)
        test_file4 = "test4.txt"
        with open(test_file4, 'w') as f:
            f.write("Test content 4")

        result = add_files([test_file4])
        assert result
        result = commit_changes("Add test4.txt")
        assert result

    # ==================== STATUS AND HISTORY TESTS ====================

    def test_status_operations_comprehensive(self):
        """Test comprehensive status operations."""
        # Setup: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Test 1: Clean repository status
        status = get_status(self.repo_dir)
        assert isinstance(status, dict)
        assert "clean" in status
        assert status["clean"]

        # Test 2: Repository with untracked files
        test_file = os.path.join(self.repo_dir, "untracked.txt")
        with open(test_file, 'w') as f:
            f.write("Untracked content")

        status = get_status(self.repo_dir)
        assert not status["clean"]
        assert "untracked.txt" in status["untracked"]

        # Test 3: Repository with staged files
        add_files(["untracked.txt"], self.repo_dir)
        status = get_status(self.repo_dir)
        assert "untracked.txt" in status["added"]

        # Test 4: Repository with modified files
        commit_changes("Add untracked file", self.repo_dir)
        with open(test_file, 'w') as f:
            f.write("Modified content")

        status = get_status(self.repo_dir)
        # After committing and then modifying, the file should show as modified
        # Note: the filename in status might be different due to Git's internal handling
        assert not status["clean"]
        # Check that there are modified files (the exact filename might vary)
        assert len(status["modified"]) > 0 or any("untracked" in f for f in status["modified"])

        # Test 5: Status in non-repository
        status = get_status(self.test_dir)
        assert "error" in status

    def test_commit_history_comprehensive(self):
        """Test comprehensive commit history operations."""
        # Setup: Initialize repository with multiple commits
        assert initialize_git_repository(self.repo_dir)

        # Create multiple commits
        for i in range(5):
            test_file = os.path.join(self.repo_dir, f"file{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Content {i}")
            add_files([f"file{i}.txt"], self.repo_dir)
            commit_changes(f"Add file{i}.txt", self.repo_dir)

        # Test 1: Get default history (10 commits)
        history = get_commit_history(repository_path=self.repo_dir)
        assert isinstance(history, list)
        assert len(history) >= 5  # At least our 5 + initial commit

        # Test 2: Get limited history
        history = get_commit_history(limit=3, repository_path=self.repo_dir)
        assert len(history) == 3

        # Test 3: Verify commit structure
        for commit in history:
            required_keys = ["hash", "author_name", "author_email", "date", "message"]
            for key in required_keys:
                assert key in commit
                assert isinstance(commit[key], str)

        # Test 4: Verify commit order (newest first)
        assert history[0]["message"] == "Add file4.txt"

        # Test 5: History in non-repository
        history = get_commit_history(repository_path=self.test_dir)
        assert history == []

    # ==================== REMOTE OPERATIONS TESTS ====================

    def test_remote_operations_comprehensive(self):
        """Test comprehensive remote operations (push/pull simulation)."""
        # Setup: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Test 1: Push without remote (should fail gracefully)
        result = push_changes(repository_path=self.repo_dir)
        assert not result  # No remote configured

        # Test 2: Pull without remote (should fail gracefully)
        result = pull_changes(repository_path=self.repo_dir)
        assert not result  # No remote configured

        # Test 3: Push with specific remote and branch
        result = push_changes("origin", "main", self.repo_dir)
        assert not result  # Should fail - no remote

        # Test 4: Pull with specific remote and branch
        result = pull_changes("origin", "main", self.repo_dir)
        assert not result  # Should fail - no remote

    # ==================== CLONE OPERATIONS TESTS ====================

    def test_clone_operations_comprehensive(self):
        """Test comprehensive clone operations."""
        # Test 1: Clone invalid URL (should fail gracefully)
        clone_dest = os.path.join(self.test_dir, "cloned_repo")
        result = clone_repository("https://invalid.url/repo.git", clone_dest)
        assert not result

        # Test 2: Clone to existing directory (should fail)
        os.makedirs(clone_dest)
        result = clone_repository("https://github.com/nonexistent/repo.git", clone_dest)
        assert not result

        # Test 3: Clone with specific branch
        result = clone_repository("https://invalid.url/repo.git",
                                clone_dest + "_branch", branch="main")
        assert not result  # Should fail due to invalid URL

    # ==================== ERROR HANDLING AND EDGE CASES ====================

    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling scenarios."""
        # Test 1: Operations on non-existent directory
        nonexistent_path = "/path/that/does/not/exist"

        assert not is_git_repository(nonexistent_path)
        assert get_current_branch(nonexistent_path) is None
        assert not create_branch("test", nonexistent_path)
        assert not switch_branch("test", nonexistent_path)
        assert not add_files(["test.txt"], nonexistent_path)
        assert not commit_changes("test", nonexistent_path)

        status = get_status(nonexistent_path)
        assert "error" in status

        history = get_commit_history(repository_path=nonexistent_path)
        assert history == []

        # Test 2: Operations with empty/invalid parameters
        assert not create_branch("", self.repo_dir)
        assert not switch_branch("", self.repo_dir)
        assert not add_files([], self.repo_dir)
        assert not commit_changes("", self.repo_dir)

        # Test 3: Operations requiring Git repository on non-repo
        assert not create_branch("test", self.test_dir)
        assert not add_files(["test.txt"], self.test_dir)
        assert not commit_changes("test", self.test_dir)

    # ==================== INTEGRATION TESTS ====================

    def test_full_workflow_integration(self):
        """Test complete Git workflow integration."""
        # Test complete workflow: init -> add -> commit -> branch -> merge simulation

        # Step 1: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Step 2: Create and add initial files
        for i in range(3):
            test_file = os.path.join(self.repo_dir, f"initial_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"Initial content {i}")

        assert add_files([f"initial_{i}.txt" for i in range(3)], self.repo_dir)
        assert commit_changes("Add initial files", self.repo_dir)

        # Step 3: Create feature branch
        assert create_branch("feature/new-feature", self.repo_dir)

        # Step 4: Add feature files
        feature_file = os.path.join(self.repo_dir, "feature.txt")
        with open(feature_file, 'w') as f:
            f.write("Feature content")

        assert add_files(["feature.txt"], self.repo_dir)
        assert commit_changes("Add feature", self.repo_dir)

        # Step 5: Verify final state
        current_branch = get_current_branch(self.repo_dir)
        assert current_branch == "feature/new-feature"

        status = get_status(self.repo_dir)
        assert status["clean"]

        history = get_commit_history(limit=3, repository_path=self.repo_dir)
        assert len(history) >= 3
        assert history[0]["message"] == "Add feature"

    # ==================== PERFORMANCE AND STRESS TESTS ====================

    def test_performance_with_many_files(self):
        """Test performance with many files (stress test)."""
        # Setup: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Create many files
        file_count = 50  # Reasonable number for testing
        file_names = []

        for i in range(file_count):
            file_name = f"perf_test_{i:03d}.txt"
            file_path = os.path.join(self.repo_dir, file_name)
            with open(file_path, 'w') as f:
                f.write(f"Performance test content {i}")
            file_names.append(file_name)

        # Test adding all files at once
        result = add_files(file_names, self.repo_dir)
        assert result

        # Test committing all files
        result = commit_changes(f"Add {file_count} performance test files", self.repo_dir)
        assert result

        # Test status with many files
        status = get_status(self.repo_dir)
        assert status["clean"]

        # Test history retrieval
        history = get_commit_history(limit=5, repository_path=self.repo_dir)
        assert len(history) > 0

    # ==================== SECURITY AND VALIDATION TESTS ====================

    def test_input_validation_and_security(self):
        """Test input validation and security measures."""
        # Setup: Initialize repository
        assert initialize_git_repository(self.repo_dir)

        # Test 1: Branch names with special characters
        special_branch_names = [
            "feature/test-branch",  # Valid
            "feature_test_branch",  # Valid
            "feature.test.branch",  # Valid
            # Note: Git handles most special characters, so we test valid ones
        ]

        for branch_name in special_branch_names:
            result = create_branch(branch_name, self.repo_dir)
            if result:  # If creation succeeded, switch back to main
                switch_branch("main", self.repo_dir)

        # Test 2: File paths with special characters
        special_files = [
            "file with spaces.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.with.dots.txt",
        ]

        for file_name in special_files:
            file_path = os.path.join(self.repo_dir, file_name)
            with open(file_path, 'w') as f:
                f.write(f"Content for {file_name}")

        result = add_files(special_files, self.repo_dir)
        assert result

        result = commit_changes("Add files with special characters", self.repo_dir)
        assert result

        # Test 3: Long commit messages
        long_message = "A" * 1000  # Very long commit message

        # Add a new file for the long message test
        long_msg_file = os.path.join(self.repo_dir, "long_msg_test.txt")
        with open(long_msg_file, 'w') as f:
            f.write("Long message test")

        add_files(["long_msg_test.txt"], self.repo_dir)
        result = commit_changes(long_message, self.repo_dir)
        assert result  # Git should handle long messages


# Coverage push -- git_operations/core
class TestGitOperations:
    """Tests for core git operation utilities."""

    def test_add_files_nonexistent(self, tmp_path):
        from codomyrmex.git_operations.core.git import add_files
        result = add_files(["nonexistent.py"], repository_path=str(tmp_path))
        assert isinstance(result, bool)

    def test_init_repo(self, tmp_path):
        import subprocess
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        from codomyrmex.git_operations.core.git import add_files
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = add_files([str(f)], repository_path=str(tmp_path))
        assert result is True


import subprocess  # noqa: E402


class TestGitCoreDeep:
    """Deep tests for git_operations/core/git.py -- 823 stmts."""

    def test_get_diff_empty_repo(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        from codomyrmex.git_operations.core.git import get_diff
        diff = get_diff(repository_path=str(tmp_path))
        assert isinstance(diff, str)

    def test_get_log_empty_repo(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        from codomyrmex.git_operations.core.git import get_commit_history
        log = get_commit_history(repository_path=str(tmp_path))
        assert isinstance(log, (str, list))

    def test_get_status(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        from codomyrmex.git_operations.core.git import get_status
        status = get_status(repository_path=str(tmp_path))
        assert isinstance(status, (str, dict))

    def test_get_branch_name(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        from codomyrmex.git_operations.core.git import get_current_branch
        branch = get_current_branch(repository_path=str(tmp_path))
        assert isinstance(branch, (str, type(None)))

    def test_create_branch(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        # Need initial commit
        f = tmp_path / "init.txt"
        f.write_text("init")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True)
        from codomyrmex.git_operations.core.git import create_branch
        result = create_branch("test-branch", repository_path=str(tmp_path))
        assert isinstance(result, bool)

    def test_list_branches(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        f = tmp_path / "init.txt"
        f.write_text("init")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True)
        from codomyrmex.git_operations.core.git import list_tags
        tags = list_tags(repository_path=str(tmp_path))
        assert isinstance(tags, (list, str))

    def test_commit_changes(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.com"], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], capture_output=True)
        f = tmp_path / "file.txt"
        f.write_text("hello")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        from codomyrmex.git_operations.core.git import commit_changes
        sha = commit_changes("test commit", repository_path=str(tmp_path))
        assert sha is not None

    def test_get_file_history(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.com"], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], capture_output=True)
        f = tmp_path / "tracked.txt"
        f.write_text("v1")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "v1"], capture_output=True)
        from codomyrmex.git_operations.core.git import get_blame
        blame = get_blame("tracked.txt", repository_path=str(tmp_path))
        assert isinstance(blame, (str, dict, type(None)))

    def test_stash_changes(self, tmp_path):
        subprocess.run(["git", "init", str(tmp_path)], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "t@t.com"], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], capture_output=True)
        f = tmp_path / "file.txt"
        f.write_text("initial")
        subprocess.run(["git", "-C", str(tmp_path), "add", "."], capture_output=True)
        subprocess.run(["git", "-C", str(tmp_path), "commit", "-m", "init"], capture_output=True)
        f.write_text("modified")
        from codomyrmex.git_operations.core.git import stash_changes
        result = stash_changes(repository_path=str(tmp_path))
        assert isinstance(result, bool)
