
import os
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from codomyrmex.git_operations.core.git import (
    add_remote,
    remove_remote,
    list_remotes,
    fetch_remote,
    reset_changes,
    revert_commit,
    clean_repository,
    get_diff,
    get_blame,
    get_commit_details,
    get_config,
    set_config,
    cherry_pick,
    init_submodules,
    update_submodules
)

@pytest.fixture
def repo_path(tmp_path):
    return str(tmp_path)

@patch("subprocess.run")
def test_add_remote(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert add_remote("origin", "https://github.com/test/repo.git", repo_path) is True
    mock_run.assert_called_with(
        ["git", "remote", "add", "origin", "https://github.com/test/repo.git"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )

@patch("subprocess.run")
def test_list_remotes(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "origin\thttps://github.com/test/repo.git (fetch)\norigin\thttps://github.com/test/repo.git (push)\n"
    
    remotes = list_remotes(repo_path)
    assert len(remotes) == 1
    assert remotes[0]["name"] == "origin"
    assert remotes[0]["url"] == "https://github.com/test/repo.git"

@patch("subprocess.run")
def test_remove_remote(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert remove_remote("origin", repo_path) is True

@patch("subprocess.run")
def test_fetch_remote(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert fetch_remote("origin", repo_path) is True

@patch("subprocess.run")
def test_reset_changes(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert reset_changes("hard", "HEAD~1", repo_path) is True
    mock_run.assert_called_with(
        ["git", "reset", "--hard", "HEAD~1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )

@patch("subprocess.run")
def test_revert_commit(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert revert_commit("abcdef1", repo_path) is True
    mock_run.assert_called_with(
        ["git", "revert", "--no-edit", "abcdef1"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )

@patch("subprocess.run")
def test_clean_repository(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert clean_repository(force=True, directories=True, repository_path=repo_path) is True
    mock_run.assert_called_with(
        ["git", "clean", "-f", "-d", "-x"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )

@patch("subprocess.run")
def test_get_diff(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "diff output"
    assert get_diff("HEAD", repo_path) == "diff output"

@patch("subprocess.run")
def test_get_commit_details(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    # format: hash|author|email|date|subject|body
    mock_run.return_value.stdout = "abc1234|Test User|test@example.com|2023-01-01|Commit Msg|Body content"
    
    details = get_commit_details("abc1234", repo_path)
    assert details["hash"] == "abc1234"
    assert details["author"] == "Test User"
    assert details["subject"] == "Commit Msg"

@patch("subprocess.run")
def test_config_ops(mock_run, repo_path):
    # Set config
    mock_run.return_value.returncode = 0
    assert set_config("user.name", "Tester", "local", repo_path) is True
    
    # Get config
    mock_run.return_value.stdout = "Tester\n"
    assert get_config("user.name", repo_path) == "Tester"

@patch("subprocess.run")
def test_cherry_pick(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert cherry_pick("abc1234", repo_path) is True
    mock_run.assert_called_with(
        ["git", "cherry-pick", "abc1234"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )

@patch("subprocess.run")
def test_submodules(mock_run, repo_path):
    mock_run.return_value.returncode = 0
    assert init_submodules(repo_path) is True
    assert update_submodules(repo_path) is True
