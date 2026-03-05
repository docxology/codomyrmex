"""Tests for git_operations.core.commands.submodules — init and update.

Uses real git repositories on disk. No mocks.
"""

import shutil
import subprocess

import pytest

_GIT_AVAILABLE = shutil.which("git") is not None

from codomyrmex.git_operations.core.commands.submodules import (
    init_submodules,
    update_submodules,
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not available"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_git_repo(path):
    """Create a minimal git repo with one commit at *path*."""
    subprocess.run(
        ["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"], cwd=path, check=True, capture_output=True
    )
    (path / "README.md").write_text("hello\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True
    )


# ---------------------------------------------------------------------------
# init_submodules
# ---------------------------------------------------------------------------


class TestInitSubmodules:
    def test_init_submodules_on_repo_without_submodules(self, tmp_path):
        """Idempotent: no submodules means no-op, returns True."""
        _make_git_repo(tmp_path)
        result = init_submodules(repository_path=str(tmp_path))
        assert result is True

    def test_init_submodules_with_invalid_path(self, tmp_path):
        """Non-existent path should return False."""
        bad_path = str(tmp_path / "does_not_exist")
        result = init_submodules(repository_path=bad_path)
        assert result is False

    def test_init_submodules_on_non_repo(self, tmp_path):
        """Plain directory (not a git repo) should return False."""
        result = init_submodules(repository_path=str(tmp_path))
        assert result is False


# ---------------------------------------------------------------------------
# update_submodules
# ---------------------------------------------------------------------------


class TestUpdateSubmodules:
    def test_update_submodules_on_repo_without_submodules(self, tmp_path):
        """Idempotent: no submodules means no-op, returns True."""
        _make_git_repo(tmp_path)
        result = update_submodules(repository_path=str(tmp_path))
        assert result is True

    def test_update_submodules_with_invalid_path(self, tmp_path):
        """Non-existent path should return False."""
        bad_path = str(tmp_path / "does_not_exist")
        result = update_submodules(repository_path=bad_path)
        assert result is False

    def test_update_submodules_on_non_repo(self, tmp_path):
        """Plain directory (not a git repo) should return False."""
        result = update_submodules(repository_path=str(tmp_path))
        assert result is False
