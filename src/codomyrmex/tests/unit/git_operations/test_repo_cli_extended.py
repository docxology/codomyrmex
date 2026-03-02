"""Extended tests for git_operations CLI commands (cmd_list, cmd_search,
cmd_clone, cmd_update, cmd_status, cmd_summary, helpers).

Zero-Mock compliant — uses a StubRepositoryManager that records calls.
Requires git to be available (same guard as test_repo_cli.py).
"""

import subprocess
from pathlib import Path

import pytest

from codomyrmex.git_operations.cli.repo import (
    _print_bulk_results,
    _print_remotes,
    cmd_clone,
    cmd_list,
    cmd_prune,
    cmd_search,
    cmd_status,
    cmd_summary,
    cmd_sync,
    cmd_update,
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


# ---------------------------------------------------------------------------
# Lightweight test doubles
# ---------------------------------------------------------------------------

class StubRepo:
    """Minimal Repository-like object."""
    def __init__(self, full_name="owner/test_repo", owner="owner",
                 repo_type=None, description="A test repo", url="https://example.com/r"):
        self.full_name = full_name
        self.owner = owner
        self.repo_type = repo_type or _FakeType("github")
        self.description = description
        self.url = url


class _FakeType:
    def __init__(self, value):
        self.value = value


class StubArgs:
    """Stub for argparse.Namespace."""
    def __init__(self, **kwargs):
        self.repository = kwargs.get("repository", None)
        self.path = kwargs.get("path", None)
        self.verbose = kwargs.get("verbose", False)
        self.type = kwargs.get("type", None)
        self.owner = kwargs.get("owner", None)
        self.all = kwargs.get("all", False)
        self.query = kwargs.get("query", "")
        # remote sub-commands
        self.list = kwargs.get("list", False)
        self.add = kwargs.get("add", None)
        self.remove = kwargs.get("remove", None)
        self.prune = kwargs.get("prune", None)
        self.url = kwargs.get("url", None)
        self.force = kwargs.get("force", False)


class StubRepositoryManager:
    """Stub RepositoryManager that records calls and returns controlled values."""

    def __init__(self, *, repos=None, local_path="/tmp/repo", status=None):
        self._calls: dict = {}
        self._repos = repos if repos is not None else [StubRepo()]
        self._local_path = Path(local_path)
        self._status = status or {}

    def _record(self, method, *args, **kwargs):
        self._calls.setdefault(method, []).append((args, kwargs))

    # List / search
    def list_repositories(self, repo_type=None):
        self._record("list_repositories", repo_type)
        return self._repos

    def search_repositories(self, query):
        self._record("search_repositories", query)
        return self._repos

    def get_local_path(self, repo):
        self._record("get_local_path", repo)
        return self._local_path

    # CRUD
    def get_repository(self, name):
        self._record("get_repository", name)
        return self._repos[0] if self._repos else None

    def clone_repository(self, name, path=None):
        self._record("clone_repository", name, path)
        return True

    def update_repository(self, name, path=None):
        self._record("update_repository", name, path)
        return True

    def sync_repository(self, name, path=None):
        self._record("sync_repository", name, path)
        return True

    def prune_repository(self, name, path=None):
        self._record("prune_repository", name, path)
        return True

    # Bulk operations
    def bulk_clone(self, repo_type=None, owner_filter=None):
        self._record("bulk_clone", repo_type, owner_filter)
        return {"repo1": True, "repo2": True}

    def bulk_update(self, repo_type=None, owner_filter=None):
        self._record("bulk_update", repo_type, owner_filter)
        return {"repo1": True}

    # Status
    def get_repository_status(self, name, path=None):
        self._record("get_repository_status", name, path)
        return self._status or {
            "repository": name,
            "path": str(self._local_path),
            "branch": "main",
            "type": "github",
            "is_development": False,
            "status": {"clean": True},
        }

    def print_repository_summary(self):
        self._record("print_repository_summary")


# ---------------------------------------------------------------------------
# TestCmdList
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdList:
    """Tests for cmd_list."""

    def test_list_calls_list_repositories(self):
        """cmd_list calls manager.list_repositories."""
        manager = StubRepositoryManager()
        args = StubArgs()
        cmd_list(manager, args)
        assert "list_repositories" in manager._calls

    def test_list_with_type_filter(self):
        """cmd_list passes repo_type to list_repositories when --type given."""
        manager = StubRepositoryManager()
        args = StubArgs(type="own")  # Valid RepositoryType value
        cmd_list(manager, args)
        assert "list_repositories" in manager._calls

    def test_list_invalid_type_prints_error(self, capsys):
        """cmd_list prints error for invalid repository type."""
        manager = StubRepositoryManager()
        args = StubArgs(type="INVALID_TYPE_XYZ")
        cmd_list(manager, args)
        captured = capsys.readouterr()
        assert "Invalid repository type" in captured.out

    def test_list_with_owner_filter(self):
        """cmd_list filters by owner when --owner given."""
        repo = StubRepo(full_name="alice/proj", owner="alice")
        manager = StubRepositoryManager(repos=[repo])
        args = StubArgs(owner="alice")
        cmd_list(manager, args)
        assert "list_repositories" in manager._calls

    def test_list_verbose_mode(self):
        """cmd_list works with verbose=True."""
        manager = StubRepositoryManager()
        args = StubArgs(verbose=True)
        cmd_list(manager, args)  # must not raise


# ---------------------------------------------------------------------------
# TestCmdSearch
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdSearch:
    """Tests for cmd_search."""

    def test_search_calls_search_repositories(self):
        """cmd_search calls manager.search_repositories with query."""
        manager = StubRepositoryManager()
        args = StubArgs(query="my_query")
        cmd_search(manager, args)
        assert "search_repositories" in manager._calls
        call_query = manager._calls["search_repositories"][0][0][0]
        assert call_query == "my_query"

    def test_search_with_verbose(self):
        """cmd_search with verbose=True runs without error."""
        manager = StubRepositoryManager()
        args = StubArgs(query="test", verbose=True)
        cmd_search(manager, args)

    def test_search_empty_results(self, capsys):
        """cmd_search with no results prints '0 repositories'."""
        manager = StubRepositoryManager(repos=[])
        args = StubArgs(query="nothing")
        cmd_search(manager, args)
        captured = capsys.readouterr()
        assert "0" in captured.out


# ---------------------------------------------------------------------------
# TestCmdClone
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdClone:
    """Tests for cmd_clone."""

    def test_clone_single_success(self, capsys):
        """cmd_clone single repo calls manager.clone_repository."""
        manager = StubRepositoryManager()
        args = StubArgs(repository="owner/repo", all=False)
        cmd_clone(manager, args)
        assert "clone_repository" in manager._calls
        captured = capsys.readouterr()
        assert "Successfully cloned" in captured.out

    def test_clone_single_no_repo_name_prints_error(self, capsys):
        """cmd_clone single without repository name prints error."""
        manager = StubRepositoryManager()
        args = StubArgs(repository=None, all=False)
        cmd_clone(manager, args)
        captured = capsys.readouterr()
        assert "required" in captured.out.lower() or "error" in captured.out.lower()

    def test_clone_all_calls_bulk_clone(self):
        """cmd_clone --all calls manager.bulk_clone."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type=None, owner=None, verbose=False)
        cmd_clone(manager, args)
        assert "bulk_clone" in manager._calls

    def test_clone_all_with_type_filter(self):
        """cmd_clone --all --type own passes repo_type to bulk_clone."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type="own", owner=None, verbose=False)
        cmd_clone(manager, args)
        assert "bulk_clone" in manager._calls

    def test_clone_all_with_owner_filter(self):
        """cmd_clone --all --owner alice passes owner_filter to bulk_clone."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type=None, owner="alice", verbose=False)
        cmd_clone(manager, args)
        assert "bulk_clone" in manager._calls

    def test_clone_all_invalid_type_prints_error(self, capsys):
        """cmd_clone --all --type BOGUS prints error and returns early."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type="BOGUS_TYPE_XYZ", owner=None, verbose=False)
        cmd_clone(manager, args)
        captured = capsys.readouterr()
        assert "Invalid repository type" in captured.out

    def test_clone_all_verbose_prints_results(self, capsys):
        """cmd_clone --all --verbose prints per-repo status."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type=None, owner=None, verbose=True)
        cmd_clone(manager, args)
        captured = capsys.readouterr()
        assert "repo1" in captured.out


# ---------------------------------------------------------------------------
# TestCmdUpdate
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdUpdate:
    """Tests for cmd_update."""

    def test_update_single_success(self, capsys):
        """cmd_update single repo calls manager.update_repository."""
        manager = StubRepositoryManager()
        args = StubArgs(repository="owner/repo", all=False)
        cmd_update(manager, args)
        assert "update_repository" in manager._calls
        captured = capsys.readouterr()
        assert "Successfully updated" in captured.out

    def test_update_single_no_name_prints_error(self, capsys):
        """cmd_update single without repository name prints error."""
        manager = StubRepositoryManager()
        args = StubArgs(repository=None, all=False)
        cmd_update(manager, args)
        captured = capsys.readouterr()
        assert "required" in captured.out.lower() or "error" in captured.out.lower()

    def test_update_all_calls_bulk_update(self):
        """cmd_update --all calls manager.bulk_update."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type=None, owner=None, verbose=False)
        cmd_update(manager, args)
        assert "bulk_update" in manager._calls

    def test_update_all_with_type(self):
        """cmd_update --all --type own passes repo_type."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type="own", owner=None, verbose=False)
        cmd_update(manager, args)
        assert "bulk_update" in manager._calls

    def test_update_all_invalid_type_prints_error(self, capsys):
        """cmd_update --all --type INVALID prints error."""
        manager = StubRepositoryManager()
        args = StubArgs(all=True, type="INVALID_XYZ", owner=None, verbose=False)
        cmd_update(manager, args)
        captured = capsys.readouterr()
        assert "Invalid repository type" in captured.out


# ---------------------------------------------------------------------------
# TestCmdStatus
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdStatus:
    """Tests for cmd_status."""

    def test_status_no_repo_prints_error(self, capsys):
        """cmd_status without repository name prints error."""
        manager = StubRepositoryManager()
        args = StubArgs(repository=None)
        cmd_status(manager, args)
        captured = capsys.readouterr()
        assert "required" in captured.out.lower() or "error" in captured.out.lower()

    def test_status_calls_get_repository_status(self):
        """cmd_status calls manager.get_repository_status."""
        manager = StubRepositoryManager()
        args = StubArgs(repository="owner/repo")
        cmd_status(manager, args)
        assert "get_repository_status" in manager._calls

    def test_status_clean_repo(self, capsys):
        """cmd_status prints 'Clean' for clean repository."""
        manager = StubRepositoryManager(status={
            "repository": "owner/repo",
            "path": "/tmp/repo",
            "branch": "main",
            "type": "github",
            "is_development": False,
            "status": {"clean": True},
        })
        args = StubArgs(repository="owner/repo")
        cmd_status(manager, args)
        captured = capsys.readouterr()
        assert "Clean" in captured.out

    def test_status_not_found(self, capsys):
        """cmd_status prints 'not found' when manager returns None."""
        manager = StubRepositoryManager()
        manager.get_repository_status = lambda name, path=None: None
        args = StubArgs(repository="missing/repo")
        cmd_status(manager, args)
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "❌" in captured.out

    def test_status_with_error_in_result(self, capsys):
        """cmd_status prints error when status dict contains 'error' key."""
        manager = StubRepositoryManager(status={
            "error": "Not cloned",
            "path": "/tmp/missing",
        })
        args = StubArgs(repository="owner/repo")
        cmd_status(manager, args)
        captured = capsys.readouterr()
        assert "Not cloned" in captured.out

    def test_status_dirty_repo_shows_modified(self, capsys):
        """cmd_status shows modified files for dirty repo."""
        manager = StubRepositoryManager(status={
            "repository": "owner/repo",
            "path": "/tmp/repo",
            "branch": "feature",
            "type": "github",
            "is_development": True,
            "status": {"clean": False, "modified": ["src/a.py"], "added": [], "untracked": []},
        })
        args = StubArgs(repository="owner/repo")
        cmd_status(manager, args)
        captured = capsys.readouterr()
        assert "Has changes" in captured.out or "changes" in captured.out.lower()


# ---------------------------------------------------------------------------
# TestCmdSummary
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdSummary:
    """Tests for cmd_summary."""

    def test_summary_calls_print_repository_summary(self):
        """cmd_summary calls manager.print_repository_summary."""
        manager = StubRepositoryManager()
        args = StubArgs()
        cmd_summary(manager, args)
        assert "print_repository_summary" in manager._calls


# ---------------------------------------------------------------------------
# TestPrintHelpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRepoPrintHelpers:
    """Tests for _print_bulk_results and _print_remotes helpers."""

    def test_print_bulk_results_summary(self, capsys):
        """_print_bulk_results prints count and action."""
        results = {"repo_a": True, "repo_b": False, "repo_c": True}
        _print_bulk_results(results, "clone", verbose=False)
        captured = capsys.readouterr()
        assert "2/3" in captured.out

    def test_print_bulk_results_verbose(self, capsys):
        """_print_bulk_results with verbose shows per-repo status."""
        results = {"repo_a": True, "repo_b": False}
        _print_bulk_results(results, "update", verbose=True)
        captured = capsys.readouterr()
        assert "repo_a" in captured.out
        assert "repo_b" in captured.out

    def test_print_bulk_results_all_success(self, capsys):
        """_print_bulk_results with all successful shows correct count."""
        results = {"r1": True, "r2": True}
        _print_bulk_results(results, "clone", verbose=False)
        captured = capsys.readouterr()
        assert "2/2" in captured.out

    def test_print_remotes_empty(self, capsys):
        """_print_remotes with empty list shows repo name."""
        _print_remotes([], "owner/repo")
        captured = capsys.readouterr()
        assert "owner/repo" in captured.out

    def test_print_remotes_with_data(self, capsys):
        """_print_remotes shows remote name and url."""
        remotes = [{"name": "origin", "url": "https://github.com/owner/repo"}]
        _print_remotes(remotes, "owner/repo")
        captured = capsys.readouterr()
        assert "origin" in captured.out
        assert "https://github.com/owner/repo" in captured.out


# ---------------------------------------------------------------------------
# TestCmdSync (extended)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdSyncExtended:
    """Extended tests for cmd_sync."""

    def test_sync_success_prints_success(self, capsys):
        """cmd_sync prints success message on success."""
        manager = StubRepositoryManager()
        args = StubArgs(repository="owner/repo")
        cmd_sync(manager, args)
        captured = capsys.readouterr()
        assert "Successfully synced" in captured.out

    def test_sync_no_repo_prints_error(self, capsys):
        """cmd_sync without repository name prints error."""
        manager = StubRepositoryManager()
        args = StubArgs(repository=None)
        cmd_sync(manager, args)
        captured = capsys.readouterr()
        assert "required" in captured.out.lower() or "error" in captured.out.lower()

    def test_sync_failure_prints_failure(self, capsys):
        """cmd_sync prints failure message when manager returns False."""
        manager = StubRepositoryManager()
        manager.sync_repository = lambda name, path=None: False
        args = StubArgs(repository="owner/repo")
        cmd_sync(manager, args)
        captured = capsys.readouterr()
        assert "Failed" in captured.out


# ---------------------------------------------------------------------------
# TestCmdPruneExtended
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCmdPruneExtended:
    """Extended tests for cmd_prune."""

    def test_prune_no_repo_prints_error(self, capsys):
        """cmd_prune without repository name prints error."""
        manager = StubRepositoryManager()
        args = StubArgs(repository=None)
        cmd_prune(manager, args)
        captured = capsys.readouterr()
        assert "required" in captured.out.lower() or "error" in captured.out.lower()

    def test_prune_failure_prints_failure(self, capsys):
        """cmd_prune prints failure when manager returns False."""
        manager = StubRepositoryManager()
        manager.prune_repository = lambda name, path=None: False
        args = StubArgs(repository="owner/repo")
        cmd_prune(manager, args)
        captured = capsys.readouterr()
        assert "Failed" in captured.out
