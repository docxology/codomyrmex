"""Tests for git_operations.api.visualization — git visualization integration.

Uses pytest.importorskip to gracefully skip if data_visualization deps are missing.
Functions that only need git (not visualization) are tested even without the optional dep.
"""

import shutil
import subprocess

from pathlib import Path

import pytest

_GIT_AVAILABLE = shutil.which("git") is not None

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not available"),
]

# Import the module — always available (it handles missing deps internally)
from codomyrmex.git_operations.api import visualization as viz_mod

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_git_repo(path):
    """Create a minimal git repo with a few commits at *path*."""
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

    readme = path / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True
    )

    # Add a second commit for richer history
    (path / "src").mkdir(exist_ok=True)
    (path / "src" / "main.py").write_text("print('hello')\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "add source"], cwd=path, check=True, capture_output=True
    )


# ---------------------------------------------------------------------------
# get_repository_metadata — does NOT require visualization dep
# ---------------------------------------------------------------------------


class TestGetRepositoryMetadata:
    """get_repository_metadata only needs git, not data_visualization."""

    def test_returns_dict_for_valid_repo(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.get_repository_metadata(str(tmp_path))
        assert isinstance(result, dict)
        assert "error" not in result

    def test_contains_expected_keys(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.get_repository_metadata(str(tmp_path))
        expected_keys = {
            "path",
            "name",
            "is_git_repo",
            "current_branch",
            "status",
            "recent_commits",
            "stashes",
            "structure_stats",
        }
        assert expected_keys.issubset(result.keys())

    def test_current_branch_is_main(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.get_repository_metadata(str(tmp_path))
        assert result["current_branch"] == "main"

    def test_recent_commits_not_empty(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.get_repository_metadata(str(tmp_path))
        assert len(result["recent_commits"]) >= 1

    def test_returns_error_for_non_repo(self, tmp_path):
        result = viz_mod.get_repository_metadata(str(tmp_path))
        assert "error" in result

    def test_commit_stats_present_when_commits_exist(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.get_repository_metadata(str(tmp_path))
        assert "commit_stats" in result
        assert result["commit_stats"]["total_recent_commits"] >= 2

    def test_structure_stats_has_files_and_directories(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.get_repository_metadata(str(tmp_path))
        stats = result["structure_stats"]
        assert "files" in stats
        assert "directories" in stats


# ---------------------------------------------------------------------------
# Internal helpers — _analyze_directory_structure, _get_structure_stats
# ---------------------------------------------------------------------------


class TestAnalyzeDirectoryStructure:
    def test_returns_dict_with_children(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "b.txt").write_text("b")
        result = viz_mod._analyze_directory_structure(str(tmp_path), max_depth=2)
        assert result["type"] == "directory"
        assert len(result["children"]) >= 2

    def test_respects_max_depth_zero(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        result = viz_mod._analyze_directory_structure(str(tmp_path), max_depth=0)
        assert result["children"] == []

    def test_skips_dot_directories(self, tmp_path):
        _make_git_repo(tmp_path)  # creates .git
        result = viz_mod._analyze_directory_structure(str(tmp_path), max_depth=1)
        child_names = [c["name"] for c in result["children"]]
        assert ".git" not in child_names


class TestGetStructureStats:
    def test_counts_files_and_dirs(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "b.txt").write_text("b")
        structure = viz_mod._analyze_directory_structure(str(tmp_path), max_depth=2)
        stats = viz_mod._get_structure_stats(structure)
        assert stats["files"] >= 2
        assert stats["directories"] >= 1

    def test_empty_directory(self, tmp_path):
        structure = viz_mod._analyze_directory_structure(str(tmp_path), max_depth=1)
        stats = viz_mod._get_structure_stats(structure)
        assert stats["files"] == 0
        assert stats["directories"] == 0


# ---------------------------------------------------------------------------
# Rendering functions (outputs always go under tmp_path)
# ---------------------------------------------------------------------------


class TestCreateGitAnalysisReport:
    def test_creates_report(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _make_git_repo(repo)
        result = viz_mod.create_git_analysis_report(
            str(repo), output_dir=str(tmp_path / "out")
        )
        assert result["success"] is True
        assert result["files_created"]
        assert all(Path(f).exists() for f in result["files_created"])

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.create_git_analysis_report(
            str(tmp_path), output_dir=str(tmp_path / "out")
        )
        assert "error" in result


class TestVisualizeGitBranches:
    def test_writes_png(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _make_git_repo(repo)
        out = tmp_path / "branches.png"
        result = viz_mod.visualize_git_branches(str(repo), output_path=str(out))
        assert result["success"] is True
        assert out.exists()

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.visualize_git_branches(str(tmp_path))
        assert "error" in result


class TestVisualizeCommitActivity:
    def test_writes_png(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _make_git_repo(repo)
        out = tmp_path / "activity.png"
        result = viz_mod.visualize_commit_activity(str(repo), output_path=str(out))
        assert result["success"] is True
        assert out.exists()

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.visualize_commit_activity(str(tmp_path))
        assert "error" in result


class TestCreateGitWorkflowDiagram:
    def test_writes_mermaid(self, tmp_path):
        out = tmp_path / "workflow.mmd"
        result = viz_mod.create_git_workflow_diagram(output_path=str(out))
        assert result["success"] is True
        assert out.read_text().strip()


class TestAnalyzeRepositoryStructure:
    def test_writes_structure(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        _make_git_repo(repo)
        out = tmp_path / "structure.mmd"
        result = viz_mod.analyze_repository_structure(str(repo), output_path=str(out))
        assert result["success"] is True
        assert out.exists()

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.analyze_repository_structure(str(tmp_path))
        assert "error" in result
