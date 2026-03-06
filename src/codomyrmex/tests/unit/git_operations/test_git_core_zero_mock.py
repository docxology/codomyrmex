"""
Zero-mock unit tests for core Git operations.
These tests use real temporary Git repositories to verify functionality.
"""

import subprocess

import pytest

from codomyrmex.git_operations.core.git import (
    add_files,
    apply_stash,
    commit_changes,
    create_branch,
    get_commit_history,
    get_current_branch,
    get_diff,
    get_status,
    initialize_git_repository,
    list_stashes,
    merge_branch,
    stash_changes,
    switch_branch,
)


@pytest.fixture
def repo_path(tmp_path):
    """Create a temporary Git repository for testing."""
    path = tmp_path / "test_repo"
    path.mkdir()

    # Initialize the repo
    initialize_git_repository(str(path), initial_commit=False)

    # Configure git user for the temp repo
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test User"], check=True)
    # Default branch name might vary by git version, let's force it to 'main'
    subprocess.run(["git", "-C", str(path), "checkout", "-b", "main"], check=False)

    return path

def test_commit_operations(repo_path):
    """Test commit related operations."""
    test_file = repo_path / "test.txt"
    test_file.write_text("initial content")

    # Add and commit
    assert add_files(["test.txt"], repository_path=str(repo_path))
    sha = commit_changes("initial commit", repository_path=str(repo_path))
    assert sha is not None
    assert len(sha) == 40

    # Verify log
    history = get_commit_history(limit=1, repository_path=str(repo_path))
    assert len(history) == 1
    assert history[0]["message"] == "initial commit"
    assert history[0]["hash"] == sha

def test_branch_operations(repo_path):
    """Test branch related operations."""
    # Need at least one commit before branching in some git versions
    (repo_path / "init.txt").write_text("init")
    add_files(["init.txt"], repository_path=str(repo_path))
    commit_changes("init", repository_path=str(repo_path))

    assert get_current_branch(str(repo_path)) == "main"

    # Create and switch branch
    assert create_branch("feature", repository_path=str(repo_path))
    assert get_current_branch(str(repo_path)) == "feature"

    # Switch back
    assert switch_branch("main", repository_path=str(repo_path))
    assert get_current_branch(str(repo_path)) == "main"

def test_merge_operations(repo_path):
    """Test merge operations."""
    # 1. Initial commit on main
    (repo_path / "main.txt").write_text("main")
    add_files(["main.txt"], repository_path=str(repo_path))
    commit_changes("base", repository_path=str(repo_path))

    # 2. Create feature branch and commit
    create_branch("feature", repository_path=str(repo_path))
    (repo_path / "feature.txt").write_text("feature")
    add_files(["feature.txt"], repository_path=str(repo_path))
    commit_changes("feature commit", repository_path=str(repo_path))

    # 3. Switch back to main and merge
    switch_branch("main", repository_path=str(repo_path))
    assert merge_branch("feature", repository_path=str(repo_path))

    # 4. Verify merge result
    assert (repo_path / "feature.txt").exists()
    history = get_commit_history(limit=5, repository_path=str(repo_path))
    assert any("feature commit" in c["message"] for c in history)

def test_status_and_diff_operations(repo_path):
    """Test status and diff operations."""
    # Initial state
    status = get_status(str(repo_path))
    assert status["clean"] is True

    # Create a file
    test_file = repo_path / "status_test.txt"
    test_file.write_text("hello")

    # Check status (untracked)
    status = get_status(str(repo_path))
    assert status["clean"] is False
    assert "status_test.txt" in status["untracked"]

    # Stage file
    add_files(["status_test.txt"], repository_path=str(repo_path))
    status = get_status(str(repo_path))
    assert "status_test.txt" in status["added"]

    # Diff (staged)
    diff = get_diff(repository_path=str(repo_path), cached=True)
    assert "+hello" in diff

    # Commit
    commit_changes("commit for diff", repository_path=str(repo_path))

    # Modify file
    test_file.write_text("hello world")

    # Diff (unstaged)
    diff = get_diff(repository_path=str(repo_path))
    assert "-hello" in diff
    assert "+hello world" in diff

def test_stash_operations(repo_path):
    """Test stash operations."""
    # Need initial commit
    (repo_path / "init.txt").write_text("init")
    add_files(["init.txt"], repository_path=str(repo_path))
    commit_changes("init", repository_path=str(repo_path))

    # Modify file
    (repo_path / "init.txt").write_text("modified")

    # Stash
    assert stash_changes(message="test stash", repository_path=str(repo_path))

    # Verify stash list
    stashes = list_stashes(repository_path=str(repo_path))
    assert len(stashes) >= 1
    assert "test stash" in stashes[0]["message"]

    # Verify working directory is clean
    status = get_status(str(repo_path))
    assert status["clean"] is True

    # Apply stash
    assert apply_stash(repository_path=str(repo_path))

    # Verify modification is back
    assert (repo_path / "init.txt").read_text() == "modified"
