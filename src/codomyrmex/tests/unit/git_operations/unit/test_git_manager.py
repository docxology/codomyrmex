"""
Unit tests for git_manager.py core functions.
"""

import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.git_operations import (
    add_files,
    check_git_availability,
    commit_changes,
    create_branch,
    get_current_branch,
    get_status,
    is_git_repository,
)


class TestCheckGitAvailability:
    """Tests for check_git_availability function."""

    def test_git_available(self):
        """Test when Git is available."""
        result = check_git_availability()
        assert isinstance(result, bool)
        # Should be True if Git is installed (which it should be in test environment)

    @patch("codomyrmex.git_operations.core.git.subprocess.run")
    def test_git_not_available(self, mock_run):
        """Test when Git is not available."""
        mock_run.side_effect = FileNotFoundError()
        result = check_git_availability()
        assert result is False

    @patch("codomyrmex.git_operations.core.git.subprocess.run")
    def test_git_command_fails(self, mock_run):
        """Test when Git command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        result = check_git_availability()
        assert result is False


class TestIsGitRepository:
    """Tests for is_git_repository function."""

    def test_is_git_repo_true(self, temp_git_repo):
        """Test with actual Git repository."""
        result = is_git_repository(temp_git_repo)
        assert result is True

    def test_is_git_repo_false(self, temp_dir):
        """Test with non-Git directory."""
        result = is_git_repository(temp_dir)
        assert result is False

    def test_is_git_repo_none_path(self):
        """Test with None path (uses current directory)."""
        # If current directory is a Git repo (like this project), should return True
        result = is_git_repository()
        assert isinstance(result, bool)

    def test_is_git_repo_invalid_path(self):
        """Test with invalid path."""
        result = is_git_repository("/nonexistent/path/that/does/not/exist")
        assert result is False


class TestGetStatus:
    """Tests for get_status function."""

    def test_get_status_clean_repo(self, temp_git_repo):
        """Test status of clean repository."""
        status = get_status(temp_git_repo)
        assert isinstance(status, dict)
        assert "clean" in status
        assert status["clean"] is True

    def test_get_status_with_changes(self, temp_git_repo, sample_file):
        """Test status with uncommitted changes."""
        status = get_status(temp_git_repo)
        assert isinstance(status, dict)
        assert "untracked" in status or "modified" in status

    def test_get_status_invalid_repo(self, temp_dir):
        """Test status with non-Git directory."""
        status = get_status(temp_dir)
        assert isinstance(status, dict)
        assert "error" in status


class TestGetCurrentBranch:
    """Tests for get_current_branch function."""

    def test_get_current_branch(self, temp_git_repo):
        """Test getting current branch."""
        branch = get_current_branch(temp_git_repo)
        assert isinstance(branch, str)
        assert len(branch) > 0
        # Should be "main" or "master" for new repo
        assert branch in ["main", "master"]

    def test_get_current_branch_invalid_repo(self, temp_dir):
        """Test getting branch from non-Git directory."""
        branch = get_current_branch(temp_dir)
        assert branch is None


class TestCreateBranch:
    """Tests for create_branch function."""

    def test_create_branch(self, temp_git_repo):
        """Test creating a new branch."""
        result = create_branch("test-branch", temp_git_repo)
        assert result is True
        
        # Verify branch was created
        current = get_current_branch(temp_git_repo)
        assert current == "test-branch"

    def test_create_branch_already_exists(self, temp_git_repo):
        """Test creating a branch that already exists."""
        # Create branch first time
        result1 = create_branch("existing-branch", temp_git_repo)
        assert result1 is True
        
        # Switch back to main
        from codomyrmex.git_operations import switch_branch
        switch_branch("main", temp_git_repo)
        
        # Try to create again (should fail)
        result2 = create_branch("existing-branch", temp_git_repo)
        assert result2 is False

    def test_create_branch_invalid_repo(self, temp_dir):
        """Test creating branch in non-Git directory."""
        result = create_branch("test-branch", temp_dir)
        assert result is False


class TestAddFiles:
    """Tests for add_files function."""

    def test_add_files(self, temp_git_repo, sample_file):
        """Test adding files to staging."""
        result = add_files([os.path.basename(sample_file)], temp_git_repo)
        assert result is True

    def test_add_files_multiple(self, temp_git_repo):
        """Test adding multiple files."""
        # Create multiple files
        file1 = os.path.join(temp_git_repo, "file1.txt")
        file2 = os.path.join(temp_git_repo, "file2.txt")
        
        with open(file1, "w") as f:
            f.write("Content 1")
        with open(file2, "w") as f:
            f.write("Content 2")
        
        result = add_files(["file1.txt", "file2.txt"], temp_git_repo)
        assert result is True

    def test_add_files_nonexistent(self, temp_git_repo):
        """Test adding non-existent files."""
        result = add_files(["nonexistent_file.txt"], temp_git_repo)
        assert result is False

    def test_add_files_invalid_repo(self, temp_dir):
        """Test adding files in non-Git directory."""
        result = add_files(["test.txt"], temp_dir)
        assert result is False


class TestCommitChanges:
    """Tests for commit_changes function."""

    def test_commit_changes(self, temp_git_repo, sample_file):
        """Test committing changes."""
        # Add file first
        add_files([os.path.basename(sample_file)], temp_git_repo)
        
        # Commit
        result = commit_changes("Test commit", temp_git_repo)
        assert result is not None
        assert isinstance(result, str)  # Should return commit SHA
        assert len(result) > 0

    def test_commit_changes_no_staged(self, temp_git_repo):
        """Test committing with no staged changes."""
        result = commit_changes("Test commit", temp_git_repo)
        # Should return None or empty string if nothing to commit
        # (depends on implementation - may return False or None)

    def test_commit_changes_invalid_repo(self, temp_dir):
        """Test committing in non-Git directory."""
        result = commit_changes("Test commit", temp_dir)
        assert result is None

