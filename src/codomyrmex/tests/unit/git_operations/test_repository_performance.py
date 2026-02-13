"""Tests for RepositoryManager bulk operations (bulk_clone, bulk_update).

Zero-Mock compliant — uses real RepositoryManager with temporary
library files and real git repos. The ThreadPoolExecutor runs in process.
"""

import os
import subprocess

import pytest

from codomyrmex.git_operations.core.repository import (
    Repository,
    RepositoryManager,
    RepositoryType,
)


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


@pytest.fixture
def lib_env(tmp_path):
    """Create two local bare repos and a library file referencing them."""
    base = tmp_path / "repos"
    base.mkdir()

    # Create two bare remotes
    remotes = {}
    for name in ("repo1", "repo2"):
        bare = str(tmp_path / f"{name}.git")
        subprocess.run(["git", "init", "--bare", bare], capture_output=True, check=True)
        remotes[name] = bare

    # Write a library file
    lib_file = str(tmp_path / "library.txt")
    with open(lib_file, "w") as f:
        f.write(f"OWN|owner|repo1|{remotes['repo1']}|Repo 1|owner/repo1\n")
        f.write(f"OWN|owner|repo2|{remotes['repo2']}|Repo 2|owner/repo2\n")

    manager = RepositoryManager(library_file=lib_file, base_path=str(base))
    return manager, remotes


class TestBulkClone:
    """Test bulk_clone with real concurrency."""

    def test_bulk_clone_returns_results(self, lib_env):
        manager, _ = lib_env
        results = manager.bulk_clone(max_workers=2)
        assert len(results) == 2
        assert all(isinstance(v, bool) for v in results.values())


class TestBulkUpdate:
    """Test bulk_update with real concurrency."""

    def test_bulk_update_returns_results(self, lib_env):
        manager, _ = lib_env
        # Clone first so update has something to update
        manager.bulk_clone(max_workers=2)
        results = manager.bulk_update(max_workers=2)
        assert len(results) == 2
        assert all(isinstance(v, bool) for v in results.values())
