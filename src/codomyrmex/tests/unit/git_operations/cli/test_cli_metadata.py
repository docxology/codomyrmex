"""Unit tests for git_operations/cli/metadata.py.

Tests the CLI command functions and argparse integration.
Uses a real RepositoryMetadataManager with a temporary metadata file.
Zero-Mock: no mocks, no stubs.
"""

import argparse
import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.git_operations.cli.metadata import (
    cmd_cleanup,
    cmd_report,
    cmd_show_metadata,
    cmd_update_metadata,
    main,
)
from codomyrmex.git_operations.core.metadata import RepositoryMetadataManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_metadata_file(tmp_path):
    """Empty metadata JSON file in a temp directory."""
    f = tmp_path / "test_metadata.json"
    f.write_text("{}")
    return str(f)


@pytest.fixture
def manager(temp_metadata_file):
    """RepositoryMetadataManager backed by a temp file."""
    return RepositoryMetadataManager(metadata_file=temp_metadata_file)


@pytest.fixture
def manager_with_repos(tmp_path):
    """Manager pre-populated with two test repositories."""
    meta_file = tmp_path / "populated_metadata.json"
    mgr = RepositoryMetadataManager(metadata_file=str(meta_file))
    # Add two repos via the public API
    mgr.create_or_update_metadata(
        full_name="owner/repo-a",
        owner="owner",
        name="repo-a",
        repo_type="OWN",
        url="https://github.com/owner/repo-a.git",
        description="Test repo A",
        local_path=str(tmp_path / "repo-a"),
    )
    mgr.create_or_update_metadata(
        full_name="owner/repo-b",
        owner="owner",
        name="repo-b",
        repo_type="USE",
        url="https://github.com/owner/repo-b.git",
        description="Test repo B",
        local_path="",
    )
    return mgr


def _args(**kwargs) -> argparse.Namespace:
    """Build a minimal argparse.Namespace for test use."""
    defaults = {
        "repository": None,
        "from_library": None,
        "type": None,
        "description": None,
        "path": None,
        "verbose": False,
        "detailed": False,
        "export": None,
        "dry_run": False,
        "token": None,
        "metadata_file": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Tests: cmd_update_metadata
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCmdUpdateMetadata:
    """Tests for the update command."""

    def test_no_args_prints_error(self, manager, capsys):
        """Neither --repository nor --from-library → prints error, returns."""
        args = _args()
        cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Error" in captured.out or "Must specify" in captured.out

    def test_invalid_repo_format_prints_error(self, manager, capsys):
        """Repository not in owner/name format → prints error, returns."""
        args = _args(repository="not-valid-format")
        cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Error" in captured.out

    def test_valid_repository_format_creates_entry(self, manager):
        """owner/repo format → entry created in metadata."""
        args = _args(repository="testowner/testrepo", type="OWN")
        cmd_update_metadata(manager, args)
        assert "testowner/testrepo" in manager.metadata

    def test_valid_repository_verbose_output(self, manager, capsys):
        """--verbose flag produces extra lines."""
        args = _args(repository="a/b", type="USE", verbose=True)
        cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "✅" in captured.out
        # Verbose mode should show clone/access status
        assert "Clone Status" in captured.out or "Access Level" in captured.out

    def test_update_existing_repo_overwrites(self, manager):
        """Calling update twice for the same repo updates the entry."""
        args1 = _args(repository="x/y", type="OWN", description="first")
        args2 = _args(repository="x/y", type="FORK", description="second")
        cmd_update_metadata(manager, args1)
        cmd_update_metadata(manager, args2)
        assert manager.metadata["x/y"].description == "second"


# ---------------------------------------------------------------------------
# Tests: cmd_show_metadata
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCmdShowMetadata:
    """Tests for the show command."""

    def test_show_unknown_repo_prints_not_found(self, manager, capsys):
        """Requesting an unknown repo → prints "No metadata found"."""
        args = _args(repository="nobody/nothing")
        cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "No metadata found" in captured.out or "❌" in captured.out

    def test_show_existing_repo_prints_details(self, manager_with_repos, capsys):
        """Existing repo → prints metadata details."""
        args = _args(repository="owner/repo-a")
        cmd_show_metadata(manager_with_repos, args)
        captured = capsys.readouterr()
        assert "owner/repo-a" in captured.out

    def test_show_all_repos_summary(self, manager_with_repos, capsys):
        """No --repository → prints summary of all repos."""
        args = _args(verbose=False)  # No repository arg
        cmd_show_metadata(manager_with_repos, args)
        captured = capsys.readouterr()
        assert "Total Repositories" in captured.out or "Repository" in captured.out

    def test_show_empty_manager_no_repos_message(self, manager, capsys):
        """Empty manager → prints no repositories message."""
        args = _args()  # No repository arg
        cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert captured.out  # Some output is produced


# ---------------------------------------------------------------------------
# Tests: cmd_report
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCmdReport:
    """Tests for the report command."""

    def test_report_on_empty_manager(self, manager, capsys):
        """Report on empty manager doesn't raise and produces output."""
        args = _args(detailed=False, export=None)
        cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "REPORT" in captured.out or "Repository" in captured.out

    def test_report_with_repos(self, manager_with_repos, capsys):
        """Report with repos shows total count."""
        args = _args(detailed=False, export=None)
        cmd_report(manager_with_repos, args)
        captured = capsys.readouterr()
        assert "2" in captured.out  # Two repos

    def test_report_exports_to_json(self, manager_with_repos, tmp_path, capsys):
        """--export saves a valid JSON file."""
        export_path = str(tmp_path / "report.json")
        args = _args(detailed=False, export=export_path)
        cmd_report(manager_with_repos, args)
        assert Path(export_path).exists()
        data = json.loads(Path(export_path).read_text())
        assert "total_repositories" in data

    def test_report_detailed_mode(self, manager_with_repos, capsys):
        """--detailed produces more output than standard mode."""
        args_standard = _args(detailed=False, export=None)
        cmd_report(manager_with_repos, args_standard)
        standard_out = capsys.readouterr().out

        args_detailed = _args(detailed=True, export=None)
        cmd_report(manager_with_repos, args_detailed)
        detailed_out = capsys.readouterr().out

        assert len(detailed_out) >= len(standard_out)


# ---------------------------------------------------------------------------
# Tests: cmd_cleanup
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCmdCleanup:
    """Tests for the cleanup command."""

    def test_cleanup_dry_run_on_empty_manager(self, manager, capsys):
        """Dry-run on empty manager produces summary."""
        args = _args(dry_run=True)
        cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Cleanup Summary" in captured.out or "Total" in captured.out

    def test_cleanup_dry_run_does_not_remove(self, manager_with_repos):
        """Dry-run must not actually delete entries."""
        before_count = len(manager_with_repos.metadata)
        args = _args(dry_run=True)
        cmd_cleanup(manager_with_repos, args)
        assert len(manager_with_repos.metadata) == before_count


# ---------------------------------------------------------------------------
# Tests: main() CLI entry point
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestMain:
    """Tests for main() argparse integration."""

    def test_main_no_args_prints_help(self, capsys):
        """main([]) with no subcommand prints help and returns."""
        main([])
        # Should not raise; help goes to stdout (or no output)

    def test_main_help_flag_exits(self):
        """main(['--help']) raises SystemExit with code 0."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_main_invalid_metadata_file_returns_gracefully(self, capsys):
        """Nonexistent metadata file → returns gracefully (no crash)."""
        # Pointing to a nonexistent file — manager will start fresh
        import tempfile as tf
        with tf.TemporaryDirectory() as d:
            meta = str(Path(d) / "missing_subdir" / "meta.json")
            # This will fail to initialize (dir doesn't exist)
            # main should catch the exception and print error
            try:
                main(["--metadata-file", meta, "report"])
            except SystemExit:
                pass  # Acceptable if argparse exits
            # The key assertion: no unhandled exception propagated
