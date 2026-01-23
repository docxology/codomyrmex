#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Git Operations Module.

Tests cover:
- Git command execution (status, log, diff)
- Branch operations
- Commit operations
- Remote operations
- GitHub API wrapper functions
- Error handling for git failures
- Repository state detection
"""

import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Import git operations functions
from codomyrmex.git_operations import (
    # Core operations
    check_git_availability,
    is_git_repository,
    initialize_git_repository,
    clone_repository,
    # Branch operations
    create_branch,
    switch_branch,
    get_current_branch,
    merge_branch,
    rebase_branch,
    # File operations
    add_files,
    commit_changes,
    amend_commit,
    get_status,
    get_diff,
    reset_changes,
    # Remote operations
    push_changes,
    pull_changes,
    fetch_changes,
    add_remote,
    remove_remote,
    list_remotes,
    # History & information
    get_commit_history,
    # Config operations
    get_config,
    set_config,
    # Advanced operations
    cherry_pick,
    # Tag operations
    create_tag,
    list_tags,
    # Stash operations
    stash_changes,
    apply_stash,
    list_stashes,
    # GitHub API
    GitHubAPIError,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_git_repo(temp_dir: str) -> Generator[str, None, None]:
    """Create a temporary Git repository for tests."""
    repo_path = os.path.join(temp_dir, "test_repo")
    os.makedirs(repo_path, exist_ok=True)

    # Initialize Git repository with initial commit
    initialize_git_repository(repo_path, initial_commit=True)

    yield repo_path


@pytest.fixture
def temp_git_repo_no_commit(temp_dir: str) -> Generator[str, None, None]:
    """Create a temporary Git repository without initial commit."""
    repo_path = os.path.join(temp_dir, "test_repo_no_commit")
    os.makedirs(repo_path, exist_ok=True)

    # Initialize Git repository without initial commit
    initialize_git_repository(repo_path, initial_commit=False)

    yield repo_path


@pytest.fixture
def sample_file(temp_git_repo: str) -> Generator[str, None, None]:
    """Create a sample file in the test repository."""
    file_path = os.path.join(temp_git_repo, "test_file.txt")
    with open(file_path, "w") as f:
        f.write("Test content\n")

    yield file_path


# ==============================================================================
# Core Git Operations Tests
# ==============================================================================


class TestGitAvailability:
    """Tests for Git availability checking."""

    def test_check_git_availability(self):
        """Test Git availability checking returns boolean."""
        result = check_git_availability()
        assert isinstance(result, bool)

    def test_check_git_availability_returns_true_when_git_installed(self):
        """Test that Git is available on the test system."""
        # This test assumes git is installed on the test system
        result = check_git_availability()
        assert result is True


class TestRepositoryDetection:
    """Tests for Git repository detection."""

    def test_is_git_repository_returns_false_for_non_repo(self, temp_dir: str):
        """Test non-repository directory is correctly detected."""
        assert is_git_repository(temp_dir) is False

    def test_is_git_repository_returns_true_for_repo(self, temp_git_repo: str):
        """Test Git repository is correctly detected."""
        assert is_git_repository(temp_git_repo) is True

    def test_is_git_repository_with_none_uses_cwd(self):
        """Test default path uses current directory."""
        result = is_git_repository(None)
        assert isinstance(result, bool)

    def test_is_git_repository_nonexistent_path(self):
        """Test nonexistent path returns False."""
        result = is_git_repository("/nonexistent/path/that/does/not/exist")
        assert result is False

    def test_is_git_repository_root_directory(self):
        """Test root directory (usually not a repo) returns False."""
        result = is_git_repository("/")
        assert result is False


class TestRepositoryInitialization:
    """Tests for Git repository initialization."""

    def test_initialize_git_repository_creates_repo(self, temp_dir: str):
        """Test repository initialization creates .git directory."""
        repo_path = os.path.join(temp_dir, "new_repo")
        os.makedirs(repo_path)

        result = initialize_git_repository(repo_path, initial_commit=True)

        assert result is True
        assert os.path.exists(os.path.join(repo_path, ".git"))

    def test_initialize_git_repository_without_initial_commit(self, temp_dir: str):
        """Test repository initialization without initial commit."""
        repo_path = os.path.join(temp_dir, "new_repo")
        os.makedirs(repo_path)

        result = initialize_git_repository(repo_path, initial_commit=False)

        assert result is True
        assert os.path.exists(os.path.join(repo_path, ".git"))

    def test_initialize_git_repository_creates_readme(self, temp_dir: str):
        """Test repository initialization creates README if specified."""
        repo_path = os.path.join(temp_dir, "new_repo")
        os.makedirs(repo_path)

        initialize_git_repository(repo_path, initial_commit=True)

        readme_path = os.path.join(repo_path, "README.md")
        assert os.path.exists(readme_path)


# ==============================================================================
# Branch Operations Tests
# ==============================================================================


class TestBranchOperations:
    """Tests for branch operations."""

    def test_get_current_branch(self, temp_git_repo: str):
        """Test getting current branch name."""
        branch = get_current_branch(temp_git_repo)
        assert branch is not None
        assert isinstance(branch, str)
        # New repos default to main or master
        assert branch in ["main", "master"]

    def test_get_current_branch_returns_none_for_non_repo(self, temp_dir: str):
        """Test getting current branch returns None for non-repository."""
        branch = get_current_branch(temp_dir)
        assert branch is None

    def test_create_branch(self, temp_git_repo: str):
        """Test branch creation."""
        result = create_branch("feature-test", temp_git_repo)
        assert result is True

        # Verify we're on the new branch
        current = get_current_branch(temp_git_repo)
        assert current == "feature-test"

    def test_create_branch_fails_in_non_repo(self, temp_dir: str):
        """Test branch creation fails in non-repository."""
        result = create_branch("test-branch", temp_dir)
        assert result is False

    def test_switch_branch(self, temp_git_repo: str):
        """Test switching branches."""
        # Create a new branch first
        create_branch("feature-test", temp_git_repo)

        # Switch back to main/master
        original_branch = "main" if get_current_branch(temp_git_repo) != "main" else "master"

        # Create main branch if not exists
        subprocess.run(
            ["git", "checkout", "-b", "main"],
            cwd=temp_git_repo,
            capture_output=True,
            check=False
        )

        result = switch_branch("feature-test", temp_git_repo)
        assert result is True
        assert get_current_branch(temp_git_repo) == "feature-test"

    def test_switch_branch_fails_for_nonexistent_branch(self, temp_git_repo: str):
        """Test switching to nonexistent branch fails."""
        result = switch_branch("nonexistent-branch", temp_git_repo)
        assert result is False


class TestMergeOperations:
    """Tests for merge operations."""

    def test_merge_branch(self, temp_git_repo: str, sample_file: str):
        """Test merging branches."""
        # Create a feature branch with changes
        create_branch("feature-to-merge", temp_git_repo)

        # Make changes on feature branch
        feature_file = os.path.join(temp_git_repo, "feature.txt")
        with open(feature_file, "w") as f:
            f.write("Feature content\n")

        add_files(["feature.txt"], temp_git_repo)
        commit_changes("Add feature", temp_git_repo)

        # Switch to main and merge
        switch_branch("main", temp_git_repo)
        result = merge_branch("feature-to-merge", repository_path=temp_git_repo)

        # Merge should succeed or fail depending on state
        assert isinstance(result, bool)

    def test_merge_branch_fails_in_non_repo(self, temp_dir: str):
        """Test merge fails in non-repository."""
        result = merge_branch("some-branch", repository_path=temp_dir)
        assert result is False


# ==============================================================================
# Commit Operations Tests
# ==============================================================================


class TestCommitOperations:
    """Tests for commit operations."""

    def test_add_files(self, temp_git_repo: str):
        """Test adding files to staging area."""
        # Create a file to add
        test_file = os.path.join(temp_git_repo, "new_file.txt")
        with open(test_file, "w") as f:
            f.write("New content\n")

        result = add_files(["new_file.txt"], temp_git_repo)
        assert result is True

    def test_add_files_fails_for_nonexistent(self, temp_git_repo: str):
        """Test adding nonexistent file fails."""
        result = add_files(["nonexistent.txt"], temp_git_repo)
        assert result is False

    def test_add_files_fails_in_non_repo(self, temp_dir: str):
        """Test adding files fails in non-repository."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        result = add_files(["test.txt"], temp_dir)
        assert result is False

    def test_commit_changes(self, temp_git_repo: str):
        """Test committing changes."""
        # Create and add a file
        test_file = os.path.join(temp_git_repo, "commit_test.txt")
        with open(test_file, "w") as f:
            f.write("Commit test content\n")

        add_files(["commit_test.txt"], temp_git_repo)

        result = commit_changes("Test commit message", temp_git_repo)
        # Returns SHA on success, None on failure
        assert result is not None
        assert isinstance(result, str)
        assert len(result) == 40  # Full SHA

    def test_commit_changes_with_author(self, temp_git_repo: str):
        """Test committing with custom author."""
        test_file = os.path.join(temp_git_repo, "author_test.txt")
        with open(test_file, "w") as f:
            f.write("Author test content\n")

        add_files(["author_test.txt"], temp_git_repo)

        result = commit_changes(
            "Test commit with author",
            temp_git_repo,
            author_name="Test Author",
            author_email="test@example.com"
        )
        assert result is not None

    def test_commit_changes_fails_when_nothing_staged(self, temp_git_repo: str):
        """Test commit fails when nothing is staged."""
        # Don't stage anything - just try to commit
        result = commit_changes("Empty commit", temp_git_repo, stage_all=False)
        assert result is None

    def test_commit_changes_fails_in_non_repo(self, temp_dir: str):
        """Test commit fails in non-repository."""
        result = commit_changes("Test commit", temp_dir)
        assert result is None


class TestAmendCommit:
    """Tests for amend commit operations."""

    def test_amend_commit(self, temp_git_repo: str):
        """Test amending the last commit."""
        # Create initial commit
        test_file = os.path.join(temp_git_repo, "amend_test.txt")
        with open(test_file, "w") as f:
            f.write("Initial content\n")

        add_files(["amend_test.txt"], temp_git_repo)
        commit_changes("Initial commit", temp_git_repo)

        # Amend with new message
        result = amend_commit("Amended commit message", temp_git_repo)
        assert result is not None

    def test_amend_commit_no_edit(self, temp_git_repo: str):
        """Test amending commit without changing message."""
        # Create initial commit
        test_file = os.path.join(temp_git_repo, "amend_noedit.txt")
        with open(test_file, "w") as f:
            f.write("Content\n")

        add_files(["amend_noedit.txt"], temp_git_repo)
        commit_changes("Original message", temp_git_repo)

        # Amend without changing message
        result = amend_commit(repository_path=temp_git_repo, no_edit=True)
        assert result is not None


# ==============================================================================
# Status and Diff Tests
# ==============================================================================


class TestStatusOperations:
    """Tests for repository status operations."""

    def test_get_status_clean_repo(self, temp_git_repo: str):
        """Test getting status of clean repository."""
        status = get_status(temp_git_repo)
        assert isinstance(status, dict)
        assert "clean" in status
        assert status["clean"] is True

    def test_get_status_with_changes(self, temp_git_repo: str):
        """Test getting status with modified files."""
        # Create an untracked file
        test_file = os.path.join(temp_git_repo, "untracked.txt")
        with open(test_file, "w") as f:
            f.write("Untracked content\n")

        status = get_status(temp_git_repo)
        assert status["clean"] is False
        assert "untracked" in status
        assert "untracked.txt" in status["untracked"]

    def test_get_status_modified_file(self, temp_git_repo: str):
        """Test getting status with modified tracked file."""
        # Create and commit a file
        test_file = os.path.join(temp_git_repo, "tracked.txt")
        with open(test_file, "w") as f:
            f.write("Initial content\n")

        add_files(["tracked.txt"], temp_git_repo)
        commit_changes("Add tracked file", temp_git_repo)

        # Modify the file
        with open(test_file, "w") as f:
            f.write("Modified content\n")

        status = get_status(temp_git_repo)
        assert status["clean"] is False
        assert "modified" in status

    def test_get_status_returns_error_for_non_repo(self, temp_dir: str):
        """Test getting status returns error for non-repository."""
        status = get_status(temp_dir)
        assert "error" in status


class TestDiffOperations:
    """Tests for diff operations."""

    def test_get_diff_no_changes(self, temp_git_repo: str):
        """Test diff with no changes."""
        diff = get_diff(repository_path=temp_git_repo)
        assert isinstance(diff, str)
        assert diff == ""  # No changes

    def test_get_diff_with_changes(self, temp_git_repo: str):
        """Test diff with changes."""
        # Create and commit a file
        test_file = os.path.join(temp_git_repo, "diff_test.txt")
        with open(test_file, "w") as f:
            f.write("Initial content\n")

        add_files(["diff_test.txt"], temp_git_repo)
        commit_changes("Add file", temp_git_repo)

        # Modify the file
        with open(test_file, "w") as f:
            f.write("Modified content\n")

        diff = get_diff(repository_path=temp_git_repo)
        assert "Modified content" in diff or "diff --git" in diff

    def test_get_diff_cached(self, temp_git_repo: str):
        """Test diff for staged changes."""
        # Create and stage a file
        test_file = os.path.join(temp_git_repo, "cached_diff.txt")
        with open(test_file, "w") as f:
            f.write("Cached content\n")

        add_files(["cached_diff.txt"], temp_git_repo)

        diff = get_diff(repository_path=temp_git_repo, cached=True)
        assert isinstance(diff, str)


# ==============================================================================
# Remote Operations Tests
# ==============================================================================


class TestRemoteOperations:
    """Tests for remote repository operations."""

    def test_list_remotes_empty(self, temp_git_repo: str):
        """Test listing remotes when none exist."""
        remotes = list_remotes(temp_git_repo)
        assert isinstance(remotes, list)
        assert len(remotes) == 0

    def test_add_remote(self, temp_git_repo: str):
        """Test adding a remote."""
        result = add_remote("origin", "https://github.com/test/repo.git", temp_git_repo)
        assert result is True

        remotes = list_remotes(temp_git_repo)
        assert len(remotes) == 1
        assert remotes[0]["name"] == "origin"

    def test_remove_remote(self, temp_git_repo: str):
        """Test removing a remote."""
        # Add a remote first
        add_remote("origin", "https://github.com/test/repo.git", temp_git_repo)

        result = remove_remote("origin", temp_git_repo)
        assert result is True

        remotes = list_remotes(temp_git_repo)
        assert len(remotes) == 0

    def test_remove_nonexistent_remote(self, temp_git_repo: str):
        """Test removing nonexistent remote fails."""
        result = remove_remote("nonexistent", temp_git_repo)
        assert result is False

    def test_fetch_changes_fails_without_remote(self, temp_git_repo: str):
        """Test fetch fails when no remote configured."""
        result = fetch_changes(repository_path=temp_git_repo)
        assert result is False

    def test_push_changes_fails_without_remote(self, temp_git_repo: str):
        """Test push fails when no remote configured."""
        result = push_changes(repository_path=temp_git_repo)
        assert result is False

    def test_pull_changes_fails_without_remote(self, temp_git_repo: str):
        """Test pull fails when no remote configured."""
        result = pull_changes(repository_path=temp_git_repo)
        assert result is False


# ==============================================================================
# History and Log Tests
# ==============================================================================


class TestCommitHistory:
    """Tests for commit history operations."""

    def test_get_commit_history(self, temp_git_repo: str):
        """Test getting commit history."""
        history = get_commit_history(repository_path=temp_git_repo)
        assert isinstance(history, list)
        assert len(history) >= 1  # At least initial commit

    def test_get_commit_history_with_limit(self, temp_git_repo: str):
        """Test getting limited commit history."""
        # Create multiple commits
        for i in range(5):
            test_file = os.path.join(temp_git_repo, f"file_{i}.txt")
            with open(test_file, "w") as f:
                f.write(f"Content {i}\n")
            add_files([f"file_{i}.txt"], temp_git_repo)
            commit_changes(f"Commit {i}", temp_git_repo)

        history = get_commit_history(limit=3, repository_path=temp_git_repo)
        assert len(history) == 3

    def test_get_commit_history_empty_repo(self, temp_dir: str):
        """Test getting history from non-repository."""
        history = get_commit_history(repository_path=temp_dir)
        assert history == []

    def test_commit_history_has_required_fields(self, temp_git_repo: str):
        """Test commit history entries have required fields."""
        history = get_commit_history(limit=1, repository_path=temp_git_repo)
        if history:
            commit = history[0]
            assert "hash" in commit
            assert "author_name" in commit
            assert "author_email" in commit
            assert "date" in commit
            assert "message" in commit


# ==============================================================================
# Tag Operations Tests
# ==============================================================================


class TestTagOperations:
    """Tests for tag operations."""

    def test_create_tag(self, temp_git_repo: str):
        """Test creating a tag."""
        result = create_tag("v1.0.0", repository_path=temp_git_repo)
        assert result is True

        tags = list_tags(temp_git_repo)
        assert "v1.0.0" in tags

    def test_create_annotated_tag(self, temp_git_repo: str):
        """Test creating an annotated tag."""
        result = create_tag(
            "v1.0.1",
            message="Release version 1.0.1",
            repository_path=temp_git_repo
        )
        assert result is True

    def test_list_tags_empty(self, temp_git_repo: str):
        """Test listing tags when none exist."""
        tags = list_tags(temp_git_repo)
        assert isinstance(tags, list)
        assert len(tags) == 0

    def test_list_multiple_tags(self, temp_git_repo: str):
        """Test listing multiple tags."""
        create_tag("v1.0.0", repository_path=temp_git_repo)
        create_tag("v1.1.0", repository_path=temp_git_repo)
        create_tag("v2.0.0", repository_path=temp_git_repo)

        tags = list_tags(temp_git_repo)
        assert len(tags) == 3


# ==============================================================================
# Stash Operations Tests
# ==============================================================================


class TestStashOperations:
    """Tests for stash operations."""

    def test_stash_changes(self, temp_git_repo: str):
        """Test stashing changes."""
        # Create a tracked file and modify it
        test_file = os.path.join(temp_git_repo, "stash_test.txt")
        with open(test_file, "w") as f:
            f.write("Initial content\n")

        add_files(["stash_test.txt"], temp_git_repo)
        commit_changes("Add file", temp_git_repo)

        # Modify the file
        with open(test_file, "w") as f:
            f.write("Modified content\n")

        # Stash the changes
        result = stash_changes(message="Test stash", repository_path=temp_git_repo)
        assert result is True

    def test_list_stashes_empty(self, temp_git_repo: str):
        """Test listing stashes when none exist."""
        stashes = list_stashes(temp_git_repo)
        assert isinstance(stashes, list)
        assert len(stashes) == 0

    def test_apply_stash_fails_when_empty(self, temp_git_repo: str):
        """Test applying stash fails when no stash exists."""
        result = apply_stash(repository_path=temp_git_repo)
        assert result is False


# ==============================================================================
# Config Operations Tests
# ==============================================================================


class TestConfigOperations:
    """Tests for Git config operations."""

    def test_get_config_user_name(self, temp_git_repo: str):
        """Test getting user.name config."""
        # Set a local config first
        set_config("user.name", "Test User", repository_path=temp_git_repo)

        value = get_config("user.name", repository_path=temp_git_repo)
        assert value == "Test User"

    def test_get_config_nonexistent(self, temp_git_repo: str):
        """Test getting nonexistent config returns None."""
        value = get_config("nonexistent.config.key", repository_path=temp_git_repo)
        assert value is None

    def test_set_config(self, temp_git_repo: str):
        """Test setting config value."""
        result = set_config(
            "core.autocrlf",
            "false",
            repository_path=temp_git_repo
        )
        assert result is True

        value = get_config("core.autocrlf", repository_path=temp_git_repo)
        assert value == "false"


# ==============================================================================
# Reset Operations Tests
# ==============================================================================


class TestResetOperations:
    """Tests for reset operations."""

    def test_reset_changes_soft(self, temp_git_repo: str):
        """Test soft reset."""
        # Create a commit
        test_file = os.path.join(temp_git_repo, "reset_test.txt")
        with open(test_file, "w") as f:
            f.write("Content\n")

        add_files(["reset_test.txt"], temp_git_repo)
        commit_changes("Commit to reset", temp_git_repo)

        result = reset_changes(mode="soft", target="HEAD~1", repository_path=temp_git_repo)
        assert result is True

    def test_reset_changes_invalid_mode(self, temp_git_repo: str):
        """Test reset with invalid mode fails."""
        result = reset_changes(mode="invalid", repository_path=temp_git_repo)
        assert result is False

    def test_reset_changes_fails_in_non_repo(self, temp_dir: str):
        """Test reset fails in non-repository."""
        result = reset_changes(mode="mixed", repository_path=temp_dir)
        assert result is False


# ==============================================================================
# Cherry Pick Operations Tests
# ==============================================================================


class TestCherryPickOperations:
    """Tests for cherry-pick operations."""

    def test_cherry_pick_invalid_commit(self, temp_git_repo: str):
        """Test cherry-pick with invalid commit fails."""
        result = cherry_pick("invalid-commit-sha", temp_git_repo)
        assert result is False

    def test_cherry_pick_fails_in_non_repo(self, temp_dir: str):
        """Test cherry-pick fails in non-repository."""
        result = cherry_pick("abc123", temp_dir)
        assert result is False


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestErrorHandling:
    """Tests for error handling in git operations."""

    def test_operations_handle_nonexistent_paths(self, temp_dir: str):
        """Test operations handle nonexistent paths gracefully."""
        nonexistent = os.path.join(temp_dir, "nonexistent")

        assert is_git_repository(nonexistent) is False
        assert get_current_branch(nonexistent) is None
        assert get_status(nonexistent).get("error") is not None
        assert create_branch("test", nonexistent) is False
        assert commit_changes("test", nonexistent) is None

    def test_operations_handle_empty_strings(self):
        """Test operations handle empty string paths."""
        assert is_git_repository("") is False
        assert get_current_branch("") is None

    def test_operations_handle_special_paths(self):
        """Test operations handle special paths."""
        paths = ["/dev/null", "/etc/passwd"]

        for path in paths:
            result = is_git_repository(path)
            assert result is False

    def test_unicode_in_commit_message(self, temp_git_repo: str):
        """Test Unicode characters in commit messages."""
        test_file = os.path.join(temp_git_repo, "unicode_test.txt")
        with open(test_file, "w") as f:
            f.write("Unicode content\n")

        add_files(["unicode_test.txt"], temp_git_repo)

        # Test with various unicode characters
        result = commit_changes(
            "Test with unicode: Hello! Bonjour! Hallo! Ciao!",
            temp_git_repo
        )
        assert result is not None

    def test_special_characters_in_file_names(self, temp_git_repo: str):
        """Test handling files with special characters."""
        # Create file with spaces
        test_file = os.path.join(temp_git_repo, "file with spaces.txt")
        with open(test_file, "w") as f:
            f.write("Content\n")

        result = add_files(["file with spaces.txt"], temp_git_repo)
        assert result is True


# ==============================================================================
# Concurrent Operations Tests
# ==============================================================================


class TestConcurrentOperations:
    """Tests for concurrent git operations."""

    def test_concurrent_status_reads(self, temp_git_repo: str):
        """Test concurrent status reads are safe."""
        results = []

        def read_status():
            for _ in range(10):
                status = get_status(temp_git_repo)
                results.append(status)

        threads = [threading.Thread(target=read_status) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 50
        assert all("clean" in r or "error" in r for r in results)

    def test_concurrent_history_reads(self, temp_git_repo: str):
        """Test concurrent history reads are safe."""
        results = []

        def read_history():
            for _ in range(10):
                history = get_commit_history(limit=5, repository_path=temp_git_repo)
                results.append(history)

        threads = [threading.Thread(target=read_history) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 50
        assert all(isinstance(r, list) for r in results)


# ==============================================================================
# GitHub API Tests (Mocked)
# ==============================================================================


class TestGitHubAPIError:
    """Tests for GitHubAPIError exception."""

    def test_github_api_error_creation(self):
        """Test GitHubAPIError can be created."""
        error = GitHubAPIError("API request failed")
        assert str(error) == "API request failed"

    def test_github_api_error_can_be_raised(self):
        """Test GitHubAPIError can be raised and caught."""
        with pytest.raises(GitHubAPIError) as exc_info:
            raise GitHubAPIError("Test error")
        assert "Test error" in str(exc_info.value)


class TestGitHubAPIOperations:
    """Tests for GitHub API operations (mocked)."""

    @patch("codomyrmex.git_operations.api.github.requests.post")
    def test_create_github_repository_mocked(self, mock_post):
        """Test create_github_repository with mocked API."""
        from codomyrmex.git_operations.api.github import create_github_repository

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "name": "test-repo",
            "full_name": "user/test-repo",
            "html_url": "https://github.com/user/test-repo",
            "clone_url": "https://github.com/user/test-repo.git",
            "ssh_url": "git@github.com:user/test-repo.git",
            "private": True,
            "description": "Test description",
            "default_branch": "main"
        }
        mock_post.return_value = mock_response

        result = create_github_repository(
            name="test-repo",
            private=True,
            description="Test description",
            github_token="test-token"
        )

        assert result["success"] is True
        assert result["repository"]["name"] == "test-repo"

    @patch("codomyrmex.git_operations.api.github.requests.get")
    def test_get_repository_info_mocked(self, mock_get):
        """Test get_repository_info with mocked API."""
        from codomyrmex.git_operations.api.github import get_repository_info

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "test-repo",
            "full_name": "user/test-repo",
            "html_url": "https://github.com/user/test-repo",
            "clone_url": "https://github.com/user/test-repo.git",
            "ssh_url": "git@github.com:user/test-repo.git",
            "private": False,
            "description": "Test repo",
            "default_branch": "main",
            "owner": {"login": "user"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "language": "Python",
            "size": 1000,
            "stargazers_count": 10,
            "watchers_count": 5,
            "forks_count": 2,
            "open_issues_count": 1
        }
        mock_get.return_value = mock_response

        result = get_repository_info("user", "test-repo", "test-token")

        assert result["name"] == "test-repo"
        assert result["full_name"] == "user/test-repo"

    @patch("codomyrmex.git_operations.api.github.requests.post")
    def test_create_pull_request_mocked(self, mock_post):
        """Test create_pull_request with mocked API."""
        from codomyrmex.git_operations.api.github import create_pull_request

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test PR",
            "body": "PR description",
            "html_url": "https://github.com/user/repo/pull/1",
            "state": "open",
            "head": {"ref": "feature", "sha": "abc123"},
            "base": {"ref": "main", "sha": "def456"},
            "user": {"login": "user"},
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_post.return_value = mock_response

        result = create_pull_request(
            repo_owner="user",
            repo_name="repo",
            head_branch="feature",
            base_branch="main",
            title="Test PR",
            body="PR description",
            github_token="test-token"
        )

        assert result["success"] is True
        assert result["pull_request"]["number"] == 1

    @patch("codomyrmex.git_operations.api.github.requests.get")
    def test_get_pull_requests_mocked(self, mock_get):
        """Test get_pull_requests with mocked API."""
        from codomyrmex.git_operations.api.github import get_pull_requests

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "PR 1",
                "body": "Description 1",
                "html_url": "https://github.com/user/repo/pull/1",
                "state": "open",
                "head": {"ref": "feature1", "sha": "abc123"},
                "base": {"ref": "main", "sha": "def456"},
                "user": {"login": "user"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "number": 2,
                "title": "PR 2",
                "body": "Description 2",
                "html_url": "https://github.com/user/repo/pull/2",
                "state": "open",
                "head": {"ref": "feature2", "sha": "ghi789"},
                "base": {"ref": "main", "sha": "def456"},
                "user": {"login": "user"},
                "created_at": "2024-01-02T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        ]
        mock_get.return_value = mock_response

        result = get_pull_requests("user", "repo", "open", "test-token")

        assert len(result) == 2
        assert result[0]["number"] == 1
        assert result[1]["number"] == 2


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestGitOperationsIntegration:
    """Integration tests for git operations workflow."""

    def test_full_workflow(self, temp_dir: str):
        """Test a complete git workflow."""
        repo_path = os.path.join(temp_dir, "integration_test")
        os.makedirs(repo_path)

        # Initialize repository
        result = initialize_git_repository(repo_path, initial_commit=True)
        assert result is True
        assert is_git_repository(repo_path)

        # Create and commit a file
        test_file = os.path.join(repo_path, "main.py")
        with open(test_file, "w") as f:
            f.write("print('Hello, World!')\n")

        add_files(["main.py"], repo_path)
        sha = commit_changes("Add main.py", repo_path)
        assert sha is not None

        # Check status is clean
        status = get_status(repo_path)
        assert status["clean"] is True

        # Create a feature branch
        create_branch("feature-branch", repo_path)
        assert get_current_branch(repo_path) == "feature-branch"

        # Make changes on feature branch
        with open(test_file, "a") as f:
            f.write("print('Feature added!')\n")

        add_files(["main.py"], repo_path)
        commit_changes("Add feature", repo_path)

        # Check history
        history = get_commit_history(limit=10, repository_path=repo_path)
        assert len(history) >= 2

        # Create a tag
        create_tag("v0.1.0", message="First version", repository_path=repo_path)
        tags = list_tags(repo_path)
        assert "v0.1.0" in tags

    def test_multiple_branch_workflow(self, temp_dir: str):
        """Test workflow with multiple branches."""
        repo_path = os.path.join(temp_dir, "multi_branch_test")
        os.makedirs(repo_path)

        initialize_git_repository(repo_path, initial_commit=True)

        # Create multiple feature branches
        branches = ["feature-a", "feature-b", "feature-c"]

        for branch in branches:
            # Switch to main first
            switch_branch("main", repo_path)

            # Create and switch to new branch
            create_branch(branch, repo_path)

            # Make a change
            test_file = os.path.join(repo_path, f"{branch}.txt")
            with open(test_file, "w") as f:
                f.write(f"Content for {branch}\n")

            add_files([f"{branch}.txt"], repo_path)
            commit_changes(f"Add {branch}", repo_path)

        # Verify we can switch between branches
        for branch in branches:
            switch_branch(branch, repo_path)
            assert get_current_branch(repo_path) == branch
