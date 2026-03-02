"""Tests for git_operations.api.visualization — git visualization integration.

Uses pytest.importorskip to gracefully skip if data_visualization deps are missing.
Functions that only need git (not visualization) are tested even without the optional dep.
"""

import shutil
import subprocess

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
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, check=True, capture_output=True)

    readme = path / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, check=True, capture_output=True)

    # Add a second commit for richer history
    (path / "src").mkdir(exist_ok=True)
    (path / "src" / "main.py").write_text("print('hello')\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add source"], cwd=path, check=True, capture_output=True)


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
        expected_keys = {"path", "name", "is_git_repo", "current_branch", "status",
                         "recent_commits", "stashes", "structure_stats"}
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
# Functions that require VISUALIZATION_AVAILABLE
# These return an error dict when the dep is missing, which is valid behaviour.
# ---------------------------------------------------------------------------

class TestCreateGitAnalysisReport:
    """Tests for create_git_analysis_report — graceful degradation."""

    def test_returns_dict(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.create_git_analysis_report(str(tmp_path))
        assert isinstance(result, dict)

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.create_git_analysis_report(str(tmp_path))
        assert "error" in result

    def test_returns_error_when_visualization_unavailable(self, tmp_path):
        """If data_visualization is not installed, function returns error dict."""
        _make_git_repo(tmp_path)
        if not viz_mod.VISUALIZATION_AVAILABLE:
            result = viz_mod.create_git_analysis_report(str(tmp_path))
            assert "error" in result
            assert "not available" in result["error"].lower()
        else:
            # If visualization IS available, it should succeed on a valid repo
            result = viz_mod.create_git_analysis_report(
                str(tmp_path), output_dir=str(tmp_path / "out")
            )
            assert isinstance(result, dict)


class TestVisualizeGitBranches:

    def test_returns_dict(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.visualize_git_branches(str(tmp_path))
        assert isinstance(result, dict)

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.visualize_git_branches(str(tmp_path))
        assert "error" in result


class TestVisualizeCommitActivity:

    def test_returns_dict(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.visualize_commit_activity(str(tmp_path))
        assert isinstance(result, dict)

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.visualize_commit_activity(str(tmp_path))
        assert "error" in result


class TestCreateGitWorkflowDiagram:

    def test_returns_dict(self):
        result = viz_mod.create_git_workflow_diagram()
        assert isinstance(result, dict)

    def test_returns_error_when_viz_unavailable(self):
        if not viz_mod.VISUALIZATION_AVAILABLE:
            result = viz_mod.create_git_workflow_diagram()
            assert "error" in result


class TestAnalyzeRepositoryStructure:

    def test_returns_dict(self, tmp_path):
        _make_git_repo(tmp_path)
        result = viz_mod.analyze_repository_structure(str(tmp_path))
        assert isinstance(result, dict)

    def test_non_repo_returns_error(self, tmp_path):
        result = viz_mod.analyze_repository_structure(str(tmp_path))
        assert "error" in result
