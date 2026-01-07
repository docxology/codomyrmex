"""
Integration tests for complete Git workflows.
"""

import os
from pathlib import Path

import pytest

from codomyrmex.git_operations import (
    add_files,
    commit_changes,
    create_branch,
    get_current_branch,
    get_status,
    initialize_git_repository,
    merge_branch,
    switch_branch,
)


class TestCompleteWorkflow:
    """Tests for complete Git workflows."""

    def test_feature_branch_workflow(self, temp_git_repo):
        """Test complete feature branch workflow."""
        # Create feature branch
        assert create_branch("feature/test-feature", temp_git_repo) is True
        assert get_current_branch(temp_git_repo) == "feature/test-feature"
        
        # Create and add files
        test_file = os.path.join(temp_git_repo, "feature_file.py")
        with open(test_file, "w") as f:
            f.write("# Feature implementation\n")
        
        assert add_files(["feature_file.py"], temp_git_repo) is True
        commit_sha = commit_changes("Add feature implementation", temp_git_repo)
        assert commit_sha is not None
        
        # Switch back to main
        assert switch_branch("main", temp_git_repo) is True
        assert get_current_branch(temp_git_repo) == "main"
        
        # Merge feature branch
        assert merge_branch("feature/test-feature", "main", temp_git_repo) is True
        
        # Verify file exists in main
        assert os.path.exists(test_file)

    def test_multiple_commits_workflow(self, temp_git_repo):
        """Test workflow with multiple commits."""
        # First commit
        file1 = os.path.join(temp_git_repo, "file1.txt")
        with open(file1, "w") as f:
            f.write("Content 1")
        
        assert add_files(["file1.txt"], temp_git_repo) is True
        sha1 = commit_changes("Add file1", temp_git_repo)
        assert sha1 is not None
        
        # Second commit
        file2 = os.path.join(temp_git_repo, "file2.txt")
        with open(file2, "w") as f:
            f.write("Content 2")
        
        assert add_files(["file2.txt"], temp_git_repo) is True
        sha2 = commit_changes("Add file2", temp_git_repo)
        assert sha2 is not None
        assert sha2 != sha1
        
        # Verify both files exist
        assert os.path.exists(file1)
        assert os.path.exists(file2)

    def test_branch_switching_workflow(self, temp_git_repo):
        """Test workflow with multiple branch switches."""
        # Create branch1
        assert create_branch("branch1", temp_git_repo) is True
        
        file1 = os.path.join(temp_git_repo, "branch1_file.txt")
        with open(file1, "w") as f:
            f.write("Branch 1 content")
        
        assert add_files(["branch1_file.txt"], temp_git_repo) is True
        commit_changes("Add branch1 file", temp_git_repo)
        
        # Switch to branch2
        assert switch_branch("main", temp_git_repo) is True
        assert create_branch("branch2", temp_git_repo) is True
        
        file2 = os.path.join(temp_git_repo, "branch2_file.txt")
        with open(file2, "w") as f:
            f.write("Branch 2 content")
        
        assert add_files(["branch2_file.txt"], temp_git_repo) is True
        commit_changes("Add branch2 file", temp_git_repo)
        
        # Verify files in correct branches
        assert get_current_branch(temp_git_repo) == "branch2"
        assert os.path.exists(file2)
        
        # Switch back to branch1
        assert switch_branch("branch1", temp_git_repo) is True
        assert get_current_branch(temp_git_repo) == "branch1"
        assert os.path.exists(file1)

    def test_status_tracking_workflow(self, temp_git_repo):
        """Test status tracking through workflow."""
        # Initial status should be clean
        status = get_status(temp_git_repo)
        assert status.get("clean", False) is True
        
        # Create untracked file
        untracked_file = os.path.join(temp_git_repo, "untracked.txt")
        with open(untracked_file, "w") as f:
            f.write("Untracked content")
        
        # Status should show untracked file
        status = get_status(temp_git_repo)
        assert status.get("clean", True) is False
        assert "untracked" in status
        assert len(status.get("untracked", [])) > 0
        
        # Add file
        assert add_files(["untracked.txt"], temp_git_repo) is True
        
        # Status should show staged file
        status = get_status(temp_git_repo)
        assert "added" in status or "staged" in status or len(status.get("added", [])) > 0
        
        # Commit
        commit_changes("Add untracked file", temp_git_repo)
        
        # Status should be clean again
        status = get_status(temp_git_repo)
        assert status.get("clean", False) is True

    def test_repository_initialization_workflow(self, temp_dir):
        """Test complete repository initialization workflow."""
        repo_path = os.path.join(temp_dir, "new_repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Initialize with initial commit
        assert initialize_git_repository(repo_path, initial_commit=True) is True
        
        # Verify it's a Git repository
        from codomyrmex.git_operations import is_git_repository
        assert is_git_repository(repo_path) is True
        
        # Verify README exists (from initial commit)
        readme_path = os.path.join(repo_path, "README.md")
        assert os.path.exists(readme_path)
        
        # Verify we can get status
        status = get_status(repo_path)
        assert isinstance(status, dict)
        assert status.get("clean", False) is True

    def test_empty_repository_workflow(self, temp_dir):
        """Test workflow with repository initialized without initial commit."""
        repo_path = os.path.join(temp_dir, "empty_repo")
        os.makedirs(repo_path, exist_ok=True)
        
        # Initialize without initial commit
        assert initialize_git_repository(repo_path, initial_commit=False) is True
        
        # Verify it's a Git repository
        from codomyrmex.git_operations import is_git_repository
        assert is_git_repository(repo_path) is True
        
        # Create first file and commit
        first_file = os.path.join(repo_path, "first.txt")
        with open(first_file, "w") as f:
            f.write("First content")
        
        assert add_files(["first.txt"], repo_path) is True
        commit_sha = commit_changes("Initial commit", repo_path)
        assert commit_sha is not None

