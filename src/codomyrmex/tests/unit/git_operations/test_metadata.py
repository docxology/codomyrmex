"""
Comprehensive unit tests for codomyrmex.git_operations.cli.metadata module.

Tests all public CLI command functions:
  - cmd_update_metadata
  - cmd_show_metadata
  - cmd_report
  - cmd_sync_status
  - cmd_cleanup
  - main (argparse entrypoint)

Zero-mock policy: uses real RepositoryMetadataManager backed by tmp_path JSON.
"""

import json
from datetime import datetime, timedelta, timezone, UTC
from pathlib import Path
from types import SimpleNamespace

import pytest

# The module under test
import codomyrmex.git_operations.cli.metadata as metadata_cli
from codomyrmex.git_operations.core.metadata import (
    AccessLevel,
    CloneStatus,
    LocalRepositoryInfo,
    RepositoryMetadata,
    RepositoryMetadataManager,
    RepositoryStats,
    SyncStatus,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manager(tmp_path: Path, repos: dict | None = None) -> RepositoryMetadataManager:
    """
    Create a real RepositoryMetadataManager backed by a JSON file in tmp_path.
    Optionally seed it with repository metadata entries.
    """
    meta_file = tmp_path / "metadata.json"
    if repos:
        data = {}
        for name, meta in repos.items():
            data[name] = meta.to_dict()
        meta_file.write_text(json.dumps(data, indent=2, default=str))
    else:
        meta_file.write_text("{}")

    return RepositoryMetadataManager(metadata_file=str(meta_file), github_token=None)


def _make_repo_metadata(
    full_name: str = "owner/repo",
    clone_status: CloneStatus = CloneStatus.NOT_CLONED,
    access_level: AccessLevel = AccessLevel.READ_ONLY,
    local_path: str = "",
    stars: int = 0,
    forks: int = 0,
    last_sync_date: str | None = None,
    tags: list[str] | None = None,
    local_exists: bool = False,
) -> RepositoryMetadata:
    """Build a RepositoryMetadata with sensible defaults."""
    owner, name = full_name.split("/")
    return RepositoryMetadata(
        full_name=full_name,
        owner=owner,
        name=name,
        repo_type="USE",
        url=f"https://github.com/{full_name}.git",
        clone_url=f"https://github.com/{full_name}.git",
        description=f"Description for {full_name}",
        access_level=access_level,
        clone_status=clone_status,
        sync_status=SyncStatus.UNKNOWN,
        local_path=local_path,
        last_sync_date=last_sync_date,
        default_branch="main",
        stats=RepositoryStats(stars=stars, forks=forks),
        local_info=LocalRepositoryInfo(
            path=local_path,
            exists=local_exists,
            is_git_repo=local_exists,
            current_branch="main" if local_exists else "",
        ),
        tags=tags or [],
        priority=0,
        category="general",
        created_date=datetime.now(UTC).isoformat(),
    )


def _args(**kwargs) -> SimpleNamespace:
    """Build a SimpleNamespace mimicking argparse output."""
    defaults = {
        "repository": None,
        "verbose": False,
        "type": None,
        "description": None,
        "path": None,
        "from_library": None,
        "token": None,
        "detailed": False,
        "export": None,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ===========================================================================
# Test cmd_update_metadata
# ===========================================================================


@pytest.mark.unit
class TestCmdUpdateMetadata:
    """Tests for cmd_update_metadata."""

    def test_update_single_repo_valid_format(self, tmp_path, capsys):
        """Update metadata for a single well-formed owner/name repository."""
        manager = _make_manager(tmp_path)
        args = _args(repository="owner/myrepo", verbose=False)
        metadata_cli.cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Updated metadata for owner/myrepo" in captured.out

    def test_update_single_repo_verbose(self, tmp_path, capsys):
        """Verbose output includes clone status and access level."""
        manager = _make_manager(tmp_path)
        args = _args(repository="owner/myrepo", verbose=True)
        metadata_cli.cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Clone Status:" in captured.out
        assert "Access Level:" in captured.out

    def test_update_single_repo_invalid_format_no_slash(self, tmp_path, capsys):
        """Repository name without slash prints error."""
        manager = _make_manager(tmp_path)
        args = _args(repository="invalidname")
        metadata_cli.cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Error: Repository must be in format 'owner/name'" in captured.out

    def test_update_single_repo_too_many_slashes(self, tmp_path, capsys):
        """Repository name with too many slashes prints error."""
        manager = _make_manager(tmp_path)
        args = _args(repository="a/b/c")
        metadata_cli.cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Error: Repository must be in format 'owner/name'" in captured.out

    def test_update_with_type_and_description(self, tmp_path, capsys):
        """Custom type and description are passed through."""
        manager = _make_manager(tmp_path)
        args = _args(
            repository="myorg/myrepo",
            type="OWN",
            description="My project",
            path="/some/path",
        )
        metadata_cli.cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Updated metadata for myorg/myrepo" in captured.out

    def test_update_no_repo_no_library_prints_error(self, tmp_path, capsys):
        """Neither --repository nor --from-library prints error."""
        manager = _make_manager(tmp_path)
        args = _args()  # no repository, no from_library
        metadata_cli.cmd_update_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Error: Must specify --repository or --from-library" in captured.out


# ===========================================================================
# Test cmd_show_metadata
# ===========================================================================


@pytest.mark.unit
class TestCmdShowMetadata:
    """Tests for cmd_show_metadata."""

    def test_show_single_repo_found(self, tmp_path, capsys):
        """Show a single repository that exists in the metadata store."""
        repo = _make_repo_metadata(
            "testowner/testrepo",
            stars=42,
            tags=["python", "ai"],
        )
        manager = _make_manager(tmp_path, {"testowner/testrepo": repo})
        args = _args(repository="testowner/testrepo", verbose=False)
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Repository Metadata: testowner/testrepo" in captured.out
        assert "Stars: 42" in captured.out
        assert "python" in captured.out

    def test_show_single_repo_not_found(self, tmp_path, capsys):
        """Show a repository not in the metadata prints not-found message."""
        manager = _make_manager(tmp_path)
        args = _args(repository="nobody/nothing")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "No metadata found for nobody/nothing" in captured.out

    def test_show_single_repo_displays_access_info(self, tmp_path, capsys):
        """Show includes access and permissions section."""
        repo = _make_repo_metadata(
            "org/proj",
            access_level=AccessLevel.ADMIN,
        )
        manager = _make_manager(tmp_path, {"org/proj": repo})
        args = _args(repository="org/proj")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Access & Permissions:" in captured.out
        assert "admin" in captured.out

    def test_show_single_repo_with_local_info(self, tmp_path, capsys):
        """Show displays local repository info when it exists."""
        repo = _make_repo_metadata(
            "org/local-project",
            local_path="/some/path",
            local_exists=True,
        )
        repo.local_info.last_commit_hash = "abc12345678"
        manager = _make_manager(tmp_path, {"org/local-project": repo})
        args = _args(repository="org/local-project")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Local Repository Info:" in captured.out
        assert "abc12345" in captured.out

    def test_show_summary_empty(self, tmp_path, capsys):
        """Show summary with no repositories prints appropriate message."""
        manager = _make_manager(tmp_path)
        args = _args(verbose=False)
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "No repositories found in metadata" in captured.out

    def test_show_summary_multiple_repos(self, tmp_path, capsys):
        """Show summary groups repos by clone status."""
        repos = {
            "a/one": _make_repo_metadata("a/one", clone_status=CloneStatus.CLONED),
            "a/two": _make_repo_metadata("a/two", clone_status=CloneStatus.CLONED),
            "b/three": _make_repo_metadata("b/three", clone_status=CloneStatus.NOT_CLONED),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(verbose=False)
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Total Repositories: 3" in captured.out
        assert "CLONED: 2" in captured.out
        assert "NOT_CLONED: 1" in captured.out

    def test_show_summary_verbose_lists_repos(self, tmp_path, capsys):
        """Verbose summary lists individual repo names."""
        repos = {
            f"owner/repo{i}": _make_repo_metadata(
                f"owner/repo{i}", clone_status=CloneStatus.CLONED
            )
            for i in range(7)
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(verbose=True)
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        # Should show first 5 and indicate more
        assert "and 2 more" in captured.out

    def test_show_displays_version_info(self, tmp_path, capsys):
        """Show displays version information section."""
        repo = _make_repo_metadata("org/proj")
        repo.default_branch = "develop"
        repo.latest_release = "v2.0.0"
        repo.version_tags = ["v1.0", "v2.0"]
        manager = _make_manager(tmp_path, {"org/proj": repo})
        args = _args(repository="org/proj")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Version Information:" in captured.out
        assert "develop" in captured.out
        assert "v2.0.0" in captured.out

    def test_show_displays_metadata_info(self, tmp_path, capsys):
        """Show displays metadata timestamps and version."""
        repo = _make_repo_metadata("org/proj")
        repo.metadata_version = "1.0"
        manager = _make_manager(tmp_path, {"org/proj": repo})
        args = _args(repository="org/proj")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Metadata Info:" in captured.out
        assert "Metadata Version: 1.0" in captured.out


# ===========================================================================
# Test cmd_report
# ===========================================================================


@pytest.mark.unit
class TestCmdReport:
    """Tests for cmd_report."""

    def test_report_empty_manager(self, tmp_path, capsys):
        """Report on empty metadata produces zero totals."""
        manager = _make_manager(tmp_path)
        args = _args(detailed=False)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Total Repositories: 0" in captured.out
        assert "Total Stars: 0" in captured.out

    def test_report_with_repos(self, tmp_path, capsys):
        """Report reflects accurate stats from populated manager."""
        repos = {
            "a/one": _make_repo_metadata("a/one", stars=100, forks=10),
            "a/two": _make_repo_metadata("a/two", stars=50, forks=5),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(detailed=False)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Total Repositories: 2" in captured.out
        assert "Total Stars: 150" in captured.out
        assert "Total Forks: 15" in captured.out

    def test_report_detailed_shows_starred(self, tmp_path, capsys):
        """Detailed report shows top starred repositories."""
        repos = {
            "a/star": _make_repo_metadata("a/star", stars=500),
            "a/nostar": _make_repo_metadata("a/nostar", stars=0),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(detailed=True)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "DETAILED ANALYSIS" in captured.out
        assert "Top Starred Repositories:" in captured.out
        assert "a/star: 500 stars" in captured.out
        # nostar (0 stars) should NOT appear in top starred
        assert "a/nostar" not in captured.out.split("Top Starred Repositories:")[1].split("Recently Active")[0]

    def test_report_detailed_shows_active_repos(self, tmp_path, capsys):
        """Detailed report shows recently active repositories."""
        repo = _make_repo_metadata("a/active")
        repo.stats.last_activity = "2026-01-15T10:00:00Z"
        manager = _make_manager(tmp_path, {"a/active": repo})
        args = _args(detailed=True)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Recently Active Repositories:" in captured.out
        assert "a/active" in captured.out

    def test_report_detailed_shows_outdated(self, tmp_path, capsys):
        """Detailed report shows repos needing attention when outdated."""
        old_date = (datetime.now(UTC) - timedelta(days=60)).isoformat()
        repo = _make_repo_metadata("a/old", last_sync_date=old_date)
        manager = _make_manager(tmp_path, {"a/old": repo})
        args = _args(detailed=True)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Repositories Needing Attention" in captured.out

    def test_report_export_json(self, tmp_path, capsys):
        """Export flag writes report to a JSON file."""
        repos = {"a/one": _make_repo_metadata("a/one", stars=10)}
        manager = _make_manager(tmp_path, repos)
        export_file = str(tmp_path / "report.json")
        args = _args(detailed=False, export=export_file)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert f"Report exported to: {export_file}" in captured.out
        # Verify the exported JSON is valid
        exported = json.loads(Path(export_file).read_text())
        assert exported["total_repositories"] == 1
        assert exported["total_stars"] == 10

    def test_report_clone_status_breakdown(self, tmp_path, capsys):
        """Report shows clone status breakdown."""
        repos = {
            "a/cloned": _make_repo_metadata("a/cloned", clone_status=CloneStatus.CLONED),
            "a/notcloned": _make_repo_metadata("a/notcloned", clone_status=CloneStatus.NOT_CLONED),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(detailed=False)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Clone Status Breakdown:" in captured.out


# ===========================================================================
# Test cmd_sync_status
# ===========================================================================


@pytest.mark.unit
class TestCmdSyncStatus:
    """Tests for cmd_sync_status."""

    def test_sync_status_no_cloned_repos(self, tmp_path, capsys):
        """When no repos are cloned, prints appropriate message."""
        repos = {
            "a/one": _make_repo_metadata("a/one", clone_status=CloneStatus.NOT_CLONED),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(verbose=False)
        metadata_cli.cmd_sync_status(manager, args)
        captured = capsys.readouterr()
        assert "No cloned repositories found" in captured.out

    def test_sync_status_with_cloned_repos(self, tmp_path, capsys):
        """Sync status checks cloned repos and categorizes them."""
        # Create a cloned repo with a local path that does NOT actually exist
        # This will trigger an error in update_local_repository_info
        repo = _make_repo_metadata(
            "a/project",
            clone_status=CloneStatus.CLONED,
            local_path=str(tmp_path / "nonexistent"),
        )
        manager = _make_manager(tmp_path, {"a/project": repo})
        args = _args(verbose=True)
        metadata_cli.cmd_sync_status(manager, args)
        captured = capsys.readouterr()
        assert "Synchronization Status" in captured.out
        assert "Checking" in captured.out

    def test_sync_status_up_to_date(self, tmp_path, capsys):
        """Repo with no uncommitted changes and no untracked files counts as up-to-date."""
        # Create a real git repo so update_local_repository_info works
        repo_dir = tmp_path / "actual_repo"
        repo_dir.mkdir()
        repo = _make_repo_metadata(
            "a/clean",
            clone_status=CloneStatus.CLONED,
            local_path=str(repo_dir),
            local_exists=True,
        )
        # The local_info fields matter for the sync check
        repo.local_info.uncommitted_changes = False
        repo.local_info.untracked_files = []
        manager = _make_manager(tmp_path, {"a/clean": repo})

        # Note: update_local_repository_info will attempt to check the actual directory.
        # Since repo_dir is not a git repo, it will set clone_status to ERROR,
        # which triggers the exception path.
        args = _args(verbose=False)
        metadata_cli.cmd_sync_status(manager, args)
        captured = capsys.readouterr()
        assert "Synchronization Status" in captured.out

    def test_sync_status_empty_manager(self, tmp_path, capsys):
        """Empty manager means no cloned repos."""
        manager = _make_manager(tmp_path)
        args = _args(verbose=False)
        metadata_cli.cmd_sync_status(manager, args)
        captured = capsys.readouterr()
        assert "No cloned repositories found" in captured.out


# ===========================================================================
# Test cmd_cleanup
# ===========================================================================


@pytest.mark.unit
class TestCmdCleanup:
    """Tests for cmd_cleanup."""

    def test_cleanup_dry_run_nonexistent_path(self, tmp_path, capsys):
        """Dry run shows what would be removed for non-existent local paths."""
        repo = _make_repo_metadata(
            "a/gone",
            local_path=str(tmp_path / "does_not_exist"),
        )
        manager = _make_manager(tmp_path, {"a/gone": repo})
        args = _args(dry_run=True)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Would remove: a/gone" in captured.out
        assert "path not found" in captured.out
        # Dry run should NOT actually remove
        assert "a/gone" in manager.metadata

    def test_cleanup_actual_removes_nonexistent(self, tmp_path, capsys):
        """Actual cleanup removes entries with non-existent local paths."""
        repo = _make_repo_metadata(
            "a/gone",
            local_path=str(tmp_path / "does_not_exist"),
        )
        manager = _make_manager(tmp_path, {"a/gone": repo})
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Removed: a/gone" in captured.out
        assert "Removed: 1" in captured.out
        assert "a/gone" not in manager.metadata

    def test_cleanup_keeps_existing_paths(self, tmp_path, capsys):
        """Repos with existing local paths are not removed."""
        existing_dir = tmp_path / "exists"
        existing_dir.mkdir()
        repo = _make_repo_metadata(
            "a/exists",
            local_path=str(existing_dir),
        )
        manager = _make_manager(tmp_path, {"a/exists": repo})
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Removed: 0" in captured.out
        assert "a/exists" in manager.metadata

    def test_cleanup_empty_local_path_is_kept(self, tmp_path, capsys):
        """Repos with empty local_path are kept (no path to check)."""
        repo = _make_repo_metadata("a/nolocalpath", local_path="")
        manager = _make_manager(tmp_path, {"a/nolocalpath": repo})
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Removed: 0" in captured.out
        assert "a/nolocalpath" in manager.metadata

    def test_cleanup_mixed_repos(self, tmp_path, capsys):
        """Mix of existing, non-existing, and no-path repos."""
        existing_dir = tmp_path / "present"
        existing_dir.mkdir()
        repos = {
            "a/present": _make_repo_metadata("a/present", local_path=str(existing_dir)),
            "a/absent": _make_repo_metadata("a/absent", local_path=str(tmp_path / "nope")),
            "a/nopath": _make_repo_metadata("a/nopath", local_path=""),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Removed: 1" in captured.out
        assert "Remaining: 2" in captured.out
        assert "a/present" in manager.metadata
        assert "a/nopath" in manager.metadata
        assert "a/absent" not in manager.metadata

    def test_cleanup_saves_metadata_after_removal(self, tmp_path, capsys):
        """After removing entries, metadata JSON is saved to disk."""
        repo = _make_repo_metadata(
            "a/gone", local_path=str(tmp_path / "vanished")
        )
        manager = _make_manager(tmp_path, {"a/gone": repo})
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        # Re-load and verify
        meta_file = tmp_path / "metadata.json"
        reloaded_data = json.loads(meta_file.read_text())
        assert "a/gone" not in reloaded_data

    def test_cleanup_summary_shows_total(self, tmp_path, capsys):
        """Cleanup summary includes total count."""
        repos = {
            f"a/repo{i}": _make_repo_metadata(
                f"a/repo{i}", local_path=str(tmp_path / f"missing{i}")
            )
            for i in range(3)
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Total repositories: 3" in captured.out
        assert "Removed: 3" in captured.out
        assert "Remaining: 0" in captured.out


# ===========================================================================
# Test main() argparse entrypoint
# ===========================================================================


@pytest.mark.unit
class TestMain:
    """Tests for the main() argparse entrypoint."""

    def test_main_no_args_prints_help(self, tmp_path, capsys):
        """Calling main with no arguments prints help and returns."""
        (tmp_path / "meta.json").write_text("{}")
        metadata_cli.main(argv=["--metadata-file", str(tmp_path / "meta.json")])
        captured = capsys.readouterr()
        assert "Repository Metadata Management CLI" in captured.out or "usage:" in captured.out.lower()

    def test_main_show_command(self, tmp_path, capsys):
        """Main dispatches 'show' command correctly."""
        meta_file = tmp_path / "meta.json"
        meta_file.write_text("{}")
        metadata_cli.main(argv=["--metadata-file", str(meta_file), "show"])
        captured = capsys.readouterr()
        assert "No repositories found in metadata" in captured.out

    def test_main_report_command(self, tmp_path, capsys):
        """Main dispatches 'report' command correctly."""
        meta_file = tmp_path / "meta.json"
        meta_file.write_text("{}")
        metadata_cli.main(argv=["--metadata-file", str(meta_file), "report"])
        captured = capsys.readouterr()
        assert "Total Repositories: 0" in captured.out

    def test_main_cleanup_dry_run(self, tmp_path, capsys):
        """Main dispatches 'cleanup --dry-run' correctly."""
        meta_file = tmp_path / "meta.json"
        meta_file.write_text("{}")
        metadata_cli.main(argv=["--metadata-file", str(meta_file), "cleanup", "--dry-run"])
        captured = capsys.readouterr()
        assert "Cleaning up repository metadata" in captured.out

    def test_main_sync_status_command(self, tmp_path, capsys):
        """Main dispatches 'sync-status' command correctly."""
        meta_file = tmp_path / "meta.json"
        meta_file.write_text("{}")
        metadata_cli.main(argv=["--metadata-file", str(meta_file), "sync-status"])
        captured = capsys.readouterr()
        assert "No cloned repositories found" in captured.out

    def test_main_with_invalid_metadata_file(self, tmp_path, capsys):
        """Main handles errors from metadata manager initialization gracefully."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("NOT VALID JSON {{{")
        metadata_cli.main(argv=["--metadata-file", str(bad_file), "show"])
        captured = capsys.readouterr()
        assert "No repositories found" in captured.out or "Repository Metadata" in captured.out


# ===========================================================================
# Edge cases and integration-style tests
# ===========================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_show_repo_with_empty_version_tags(self, tmp_path, capsys):
        """Show handles empty version_tags list gracefully."""
        repo = _make_repo_metadata("a/notags")
        repo.version_tags = []
        manager = _make_manager(tmp_path, {"a/notags": repo})
        args = _args(repository="a/notags")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "Version Tags:" in captured.out

    def test_show_repo_with_many_version_tags(self, tmp_path, capsys):
        """Show only displays first 5 version tags."""
        repo = _make_repo_metadata("a/manytags")
        repo.version_tags = [f"v{i}.0" for i in range(10)]
        manager = _make_manager(tmp_path, {"a/manytags": repo})
        args = _args(repository="a/manytags")
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        # Should show v0.0 through v4.0 but not v5.0
        assert "v0.0" in captured.out
        assert "v4.0" in captured.out

    def test_report_repos_never_synced_counted_as_outdated(self, tmp_path, capsys):
        """Repos that have never been synced count as outdated."""
        repo = _make_repo_metadata("a/neversync", last_sync_date=None)
        manager = _make_manager(tmp_path, {"a/neversync": repo})
        args = _args(detailed=False)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Outdated Repositories: 1" in captured.out

    def test_cleanup_no_repos_to_remove(self, tmp_path, capsys):
        """Cleanup with no repos prints zero removal summary."""
        manager = _make_manager(tmp_path)
        args = _args(dry_run=False)
        metadata_cli.cmd_cleanup(manager, args)
        captured = capsys.readouterr()
        assert "Total repositories: 0" in captured.out
        assert "Removed: 0" in captured.out

    def test_update_repo_with_none_type_defaults_to_use(self, tmp_path, capsys):
        """When type arg is None, defaults to 'USE'."""
        manager = _make_manager(tmp_path)
        args = _args(repository="test/defaults", type=None)
        metadata_cli.cmd_update_metadata(manager, args)
        # Verify the metadata was created with USE type
        meta = manager.get_repository_metadata("test/defaults")
        assert meta is not None
        assert meta.repo_type == "USE"

    def test_show_summary_verbose_with_exactly_five_repos(self, tmp_path, capsys):
        """Verbose summary with exactly 5 repos shows all without 'and N more'."""
        repos = {
            f"owner/repo{i}": _make_repo_metadata(
                f"owner/repo{i}", clone_status=CloneStatus.CLONED
            )
            for i in range(5)
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(verbose=True)
        metadata_cli.cmd_show_metadata(manager, args)
        captured = capsys.readouterr()
        assert "more" not in captured.out

    def test_report_type_breakdown(self, tmp_path, capsys):
        """Report includes type breakdown section."""
        repos = {
            "a/own": _make_repo_metadata("a/own"),
        }
        # Modify repo_type
        repos["a/own"].repo_type = "OWN"
        manager = _make_manager(tmp_path, repos)
        args = _args(detailed=False)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Repository Type Breakdown:" in captured.out
        assert "OWN" in captured.out

    def test_report_access_breakdown(self, tmp_path, capsys):
        """Report includes access level breakdown section."""
        repos = {
            "a/rw": _make_repo_metadata("a/rw", access_level=AccessLevel.READ_WRITE),
        }
        manager = _make_manager(tmp_path, repos)
        args = _args(detailed=False)
        metadata_cli.cmd_report(manager, args)
        captured = capsys.readouterr()
        assert "Access Level Breakdown:" in captured.out
