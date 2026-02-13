"""Tests for advanced git operations (remote, reset, revert, clean, etc.).

Zero-Mock compliant — uses real git commands on temporary repositories.
"""

import os
import subprocess

import pytest

from codomyrmex.git_operations.core.git import (
    add_remote,
    cherry_pick,
    clean_repository,
    fetch_remote,
    get_commit_details,
    get_config,
    get_diff,
    init_submodules,
    list_remotes,
    remove_remote,
    reset_changes,
    revert_commit,
    set_config,
    update_submodules,
)


def _git_available():
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


_HAS_GIT = _git_available()
pytestmark = pytest.mark.skipif(not _HAS_GIT, reason="git not available")


@pytest.fixture
def git_repo(tmp_path):
    """Create a real temporary git repo with one commit."""
    repo = str(tmp_path / "repo")
    os.makedirs(repo)
    subprocess.run(["git", "init"], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo, capture_output=True)

    # Initial commit so HEAD exists
    readme = os.path.join(repo, "README.md")
    with open(readme, "w") as f:
        f.write("# Test\n")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, capture_output=True, check=True)
    return repo


@pytest.fixture
def bare_remote(tmp_path):
    """Create a bare remote for push/fetch tests."""
    remote = str(tmp_path / "remote.git")
    subprocess.run(["git", "init", "--bare", remote], capture_output=True, check=True)
    return remote


# ---------------------------------------------------------------------------
# Remote tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_add_remote(git_repo, bare_remote):
    result = add_remote("upstream", bare_remote, git_repo)
    assert result is True


@pytest.mark.unit
def test_list_remotes(git_repo, bare_remote):
    add_remote("upstream", bare_remote, git_repo)
    remotes = list_remotes(git_repo)
    assert isinstance(remotes, list)
    names = [r["name"] for r in remotes]
    assert "upstream" in names


@pytest.mark.unit
def test_remove_remote(git_repo, bare_remote):
    add_remote("upstream", bare_remote, git_repo)
    result = remove_remote("upstream", git_repo)
    assert result is True
    remotes = list_remotes(git_repo)
    names = [r["name"] for r in remotes]
    assert "upstream" not in names


@pytest.mark.unit
def test_fetch_remote(git_repo, bare_remote):
    add_remote("upstream", bare_remote, git_repo)
    result = fetch_remote("upstream", git_repo)
    assert result is True


# ---------------------------------------------------------------------------
# Reset / Revert / Clean
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_reset_changes(git_repo):
    # Create a second commit so we can reset back
    f = os.path.join(git_repo, "extra.txt")
    with open(f, "w") as fh:
        fh.write("extra")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "second"], cwd=git_repo, capture_output=True)

    result = reset_changes("hard", "HEAD~1", git_repo)
    assert result is True
    assert not os.path.exists(f)


@pytest.mark.unit
def test_revert_commit(git_repo):
    # Create a second commit to revert
    f = os.path.join(git_repo, "revertme.txt")
    with open(f, "w") as fh:
        fh.write("bye")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "to-revert"], cwd=git_repo, capture_output=True)

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=git_repo, capture_output=True, text=True).stdout.strip()
    result = revert_commit(sha, git_repo)
    assert result is True


@pytest.mark.unit
def test_clean_repository(git_repo):
    # Create untracked file
    junk = os.path.join(git_repo, "junk.tmp")
    with open(junk, "w") as f:
        f.write("junk")

    result = clean_repository(force=True, directories=True, repository_path=git_repo)
    assert result is True
    assert not os.path.exists(junk)


# ---------------------------------------------------------------------------
# Diff / Commit details
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_get_diff(git_repo):
    diff = get_diff("HEAD", git_repo)
    assert isinstance(diff, str)


@pytest.mark.unit
def test_get_commit_details(git_repo):
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=git_repo, capture_output=True, text=True).stdout.strip()
    details = get_commit_details(sha, git_repo)
    assert details["hash"] == sha
    assert details["author"] == "Tester"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_config_ops(git_repo):
    assert set_config("user.name", "NewTester", "local", git_repo) is True
    assert get_config("user.name", git_repo) == "NewTester"


# ---------------------------------------------------------------------------
# Cherry-pick
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_cherry_pick(git_repo):
    # Create branch with a commit, then cherry-pick it to main
    subprocess.run(["git", "checkout", "-b", "feature"], cwd=git_repo, capture_output=True)
    f = os.path.join(git_repo, "feature.txt")
    with open(f, "w") as fh:
        fh.write("feature")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feature commit"], cwd=git_repo, capture_output=True)

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=git_repo, capture_output=True, text=True).stdout.strip()

    subprocess.run(["git", "checkout", "main"], cwd=git_repo, capture_output=True)
    result = cherry_pick(sha, git_repo)
    assert result is True


# ---------------------------------------------------------------------------
# Submodules (no-op on a repo without submodules, should succeed or be benign)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_submodules(git_repo):
    result_init = init_submodules(git_repo)
    result_update = update_submodules(git_repo)
    assert isinstance(result_init, bool)
    assert isinstance(result_update, bool)
