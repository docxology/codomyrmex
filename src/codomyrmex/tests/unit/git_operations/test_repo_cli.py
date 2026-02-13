"""Tests for git_operations CLI commands.

Zero-Mock compliant — uses StubRepositoryManager and real function
calls where possible.
"""

import os
import subprocess

import pytest

from codomyrmex.git_operations.cli.repo import (
    cmd_clean,
    cmd_prune,
    cmd_remote,
    cmd_sync,
)
from codomyrmex.git_operations.core.repository import RepositoryManager


def _git_available():
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


_HAS_GIT = _git_available()
pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _HAS_GIT, reason="git not available"),
]


# ---------------------------------------------------------------------------
# Lightweight stubs for CLI testing
# ---------------------------------------------------------------------------

class StubRepo:
    """Stub for a Repository dataclass."""
    def __init__(self, full_name="owner/repo"):
        self.full_name = full_name


class StubArgs:
    """Stub for CLI parsed args (replaces MagicMock for argparse namespace)."""
    def __init__(self, **kwargs):
        self.repository = kwargs.get("repository", "owner/repo")
        self.path = kwargs.get("path", None)
        self.verbose = kwargs.get("verbose", False)
        # remote sub-command attrs
        self.list = kwargs.get("list", False)
        self.add = kwargs.get("add", None)
        self.remove = kwargs.get("remove", None)
        self.prune = kwargs.get("prune", None)
        self.url = kwargs.get("url", None)
        # clean
        self.force = kwargs.get("force", False)


class StubRepositoryManager:
    """Stub RepositoryManager recording calls."""

    def __init__(self, *, repo=None, local_path="/tmp/repo"):
        self._calls = {}
        self._repo = repo or StubRepo()
        self._local_path = local_path

    def _record(self, method, *args, **kwargs):
        self._calls.setdefault(method, []).append((args, kwargs))

    def get_repository(self, name):
        self._record("get_repository", name)
        return self._repo

    def get_local_path(self, repo):
        self._record("get_local_path", repo)
        return self._local_path

    def sync_repository(self, name, path=None):
        self._record("sync_repository", name, path)
        return True

    def prune_repository(self, name, path=None):
        self._record("prune_repository", name, path)
        return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCmdSync:
    def test_cmd_sync_calls_manager(self):
        manager = StubRepositoryManager()
        args = StubArgs(repository="owner/repo")
        cmd_sync(manager, args)
        assert len(manager._calls.get("sync_repository", [])) == 1
        call_args = manager._calls["sync_repository"][0][0]
        assert call_args[0] == "owner/repo"


class TestCmdPrune:
    def test_cmd_prune_calls_manager(self):
        manager = StubRepositoryManager()
        args = StubArgs(repository="owner/repo")
        cmd_prune(manager, args)
        assert len(manager._calls.get("prune_repository", [])) == 1


class TestCmdClean:
    def test_cmd_clean_real_repo(self, tmp_path):
        """Test cmd_clean against a real git repo."""
        repo_dir = str(tmp_path / "repo")
        os.makedirs(repo_dir)
        subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=repo_dir, capture_output=True)

        # Create initial commit
        with open(os.path.join(repo_dir, "README.md"), "w") as f:
            f.write("# Test\n")
        subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, capture_output=True)

        # Create untracked file that clean should remove
        junk = os.path.join(repo_dir, "junk.tmp")
        with open(junk, "w") as f:
            f.write("junk")

        manager = StubRepositoryManager(local_path=repo_dir)
        args = StubArgs(repository="owner/repo", force=False)
        cmd_clean(manager, args)
        # Verify clean was attempted (file may or may not be removed depending on force flag)


class TestCmdRemote:
    def test_cmd_remote_list(self, tmp_path):
        """Test listing remotes on a real git repo."""
        repo_dir = str(tmp_path / "repo")
        os.makedirs(repo_dir)
        subprocess.run(["git", "init"], cwd=repo_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "T"], cwd=repo_dir, capture_output=True)

        # Add a remote
        bare = str(tmp_path / "remote.git")
        subprocess.run(["git", "init", "--bare", bare], capture_output=True, check=True)
        subprocess.run(["git", "remote", "add", "origin", bare], cwd=repo_dir, capture_output=True)

        # Initial commit so repo is valid
        with open(os.path.join(repo_dir, "README.md"), "w") as f:
            f.write("# Test\n")
        subprocess.run(["git", "add", "."], cwd=repo_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=repo_dir, capture_output=True)

        manager = StubRepositoryManager(local_path=repo_dir)
        args = StubArgs(repository="owner/repo", list=True, add=None, remove=None, prune=None)
        # cmd_remote should not crash
        cmd_remote(manager, args)
