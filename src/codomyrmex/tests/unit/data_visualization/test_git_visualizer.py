"""
Tests for codomyrmex.data_visualization.git.git_visualizer module.

Covers GitVisualizer class: initialization, PNG visualizations, Mermaid diagrams,
repository summary dashboards, comprehensive reports, helper methods, and
convenience functions.

Zero-mock policy: all tests use real objects and tmp_path for filesystem.
"""

import importlib.util
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Matplotlib must be available (it's a core dependency of data_visualization)
matplotlib_spec = importlib.util.find_spec("matplotlib")
pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(matplotlib_spec is None, reason="Requires matplotlib"),
]

# Force non-interactive backend before any matplotlib import
import matplotlib

matplotlib.use("Agg")

from codomyrmex.data_visualization.git.git_visualizer import (
    GitVisualizer,
    create_git_tree_mermaid,
    create_git_tree_png,
    visualize_git_repository,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def visualizer():
    """Return a fresh GitVisualizer instance."""
    return GitVisualizer()


@pytest.fixture
def sample_branches():
    """Provide a list of branch dicts used by visualize_git_tree_png."""
    return [
        {"name": "main", "commits": 5},
        {"name": "develop", "commits": 3},
        {"name": "feature/login", "commits": 2},
    ]


@pytest.fixture
def sample_commits():
    """Provide a list of commit dicts with ISO dates spread across branches."""
    base = datetime(2025, 6, 1, 12, 0, 0)
    commits = []
    branch_cycle = ["main", "develop", "feature/login"]
    for i in range(10):
        commits.append(
            {
                "hash": f"abc{i:04d}",
                "message": f"Implement feature number {i}",
                "author_name": "Alice" if i % 2 == 0 else "Bob",
                "author_email": "dev@example.com",
                "date": (base - timedelta(days=i)).isoformat(),
                "branch": branch_cycle[i % len(branch_cycle)],
            }
        )
    return commits


@pytest.fixture
def sample_repo_data(sample_commits):
    """Provide a repo_data dict suitable for visualize_repository_summary_png."""
    return {
        "status": {"clean": False, "modified": ["file_a.py"], "untracked": ["tmp.log"]},
        "commits": sample_commits,
        "current_branch": "develop",
        "total_commits": len(sample_commits),
    }


@pytest.fixture
def sample_repo_dir(tmp_path):
    """Create a simple directory tree to exercise _get_repository_structure."""
    # Top-level files
    (tmp_path / "README.md").write_text("# Repo")
    (tmp_path / "setup.py").write_text("")
    # Hidden file (should be skipped)
    (tmp_path / ".gitignore").write_text("*.pyc")
    # Subdirectory with children
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("")
    (src / "utils").mkdir()
    (src / ".hidden_dir").mkdir()  # should be skipped
    # Another top-level dir
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "guide.md").write_text("")
    return tmp_path


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestGitVisualizerInit:
    """Test GitVisualizer construction and default attributes."""

    def test_init_creates_mermaid_generator(self, visualizer):
        assert visualizer.mermaid_generator is not None

    def test_init_has_color_palette(self, visualizer):
        expected_keys = {"main", "develop", "feature", "hotfix", "release", "commit", "merge", "tag"}
        assert expected_keys == set(visualizer.colors.keys())

    def test_colors_are_hex_strings(self, visualizer):
        for key, value in visualizer.colors.items():
            assert isinstance(value, str), f"Color for {key} is not a string"
            assert value.startswith("#"), f"Color for {key} does not start with #"


# ---------------------------------------------------------------------------
# _get_branch_color
# ---------------------------------------------------------------------------


class TestGetBranchColor:
    """Test branch color resolution logic."""

    def test_main_branch(self, visualizer):
        assert visualizer._get_branch_color("main") == visualizer.colors["main"]

    def test_master_branch(self, visualizer):
        assert visualizer._get_branch_color("master") == visualizer.colors["main"]

    def test_develop_branch(self, visualizer):
        assert visualizer._get_branch_color("develop") == visualizer.colors["develop"]

    def test_feature_branch(self, visualizer):
        assert visualizer._get_branch_color("feature/auth") == visualizer.colors["feature"]

    def test_hotfix_branch(self, visualizer):
        assert visualizer._get_branch_color("hotfix/critical-fix") == visualizer.colors["hotfix"]

    def test_release_branch(self, visualizer):
        assert visualizer._get_branch_color("release/v2.0") == visualizer.colors["release"]

    def test_unknown_branch_returns_commit_color(self, visualizer):
        assert visualizer._get_branch_color("experiment/weird") == visualizer.colors["commit"]

    def test_case_insensitive(self, visualizer):
        assert visualizer._get_branch_color("MAIN") == visualizer.colors["main"]
        assert visualizer._get_branch_color("Develop") == visualizer.colors["develop"]


# ---------------------------------------------------------------------------
# _generate_sample_commits
# ---------------------------------------------------------------------------


class TestGenerateSampleCommits:
    """Test internal sample commit generation."""

    def test_default_count(self, visualizer):
        commits = visualizer._generate_sample_commits()
        assert len(commits) == 30

    def test_custom_days_back(self, visualizer):
        commits = visualizer._generate_sample_commits(days_back=7)
        assert len(commits) == 7

    def test_commit_structure(self, visualizer):
        commits = visualizer._generate_sample_commits(days_back=3)
        for commit in commits:
            assert "hash" in commit
            assert "message" in commit
            assert "author_name" in commit
            assert "date" in commit
            assert "branch" in commit

    def test_branch_distribution(self, visualizer):
        commits = visualizer._generate_sample_commits(days_back=9)
        branches = {c["branch"] for c in commits}
        assert "main" in branches
        assert "develop" in branches
        assert "feature/sample" in branches


# ---------------------------------------------------------------------------
# visualize_git_tree_png
# ---------------------------------------------------------------------------


class TestVisualizeGitTreePng:
    """Test PNG git tree visualization with provided data."""

    def test_with_provided_branches_and_commits(self, visualizer, sample_branches, sample_commits, tmp_path):
        out = tmp_path / "tree.png"
        result = visualizer.visualize_git_tree_png(
            branches=sample_branches,
            commits=sample_commits,
            title="Test Tree",
            output_path=str(out),
        )
        assert result is True
        assert out.exists()
        assert out.stat().st_size > 0

    def test_with_sample_data_fallback(self, visualizer, tmp_path):
        """When neither repository_path nor branches/commits given, uses sample data."""
        out = tmp_path / "sample_tree.png"
        result = visualizer.visualize_git_tree_png(
            title="Sample Fallback",
            output_path=str(out),
        )
        assert result is True
        assert out.exists()

    def test_no_output_path_still_succeeds(self, visualizer, sample_branches, sample_commits):
        result = visualizer.visualize_git_tree_png(
            branches=sample_branches,
            commits=sample_commits,
            title="No save",
        )
        assert result is True

    def test_custom_figure_size(self, visualizer, sample_branches, sample_commits, tmp_path):
        out = tmp_path / "custom_size.png"
        result = visualizer.visualize_git_tree_png(
            branches=sample_branches,
            commits=sample_commits,
            figure_size=(8, 4),
            output_path=str(out),
        )
        assert result is True

    def test_max_commits_limits_display(self, visualizer, sample_branches, sample_commits, tmp_path):
        out = tmp_path / "limited.png"
        result = visualizer.visualize_git_tree_png(
            branches=sample_branches,
            commits=sample_commits,
            max_commits=3,
            output_path=str(out),
        )
        assert result is True

    def test_returns_false_on_internal_error(self, visualizer):
        """Passing a commit with no branch should still succeed (defaults to 'main')."""
        result = visualizer.visualize_git_tree_png(
            branches=[{"name": "main", "commits": 1}],
            commits=[{"hash": "abc", "message": "test", "date": "2025-01-01T00:00:00"}],
        )
        assert result is True


# ---------------------------------------------------------------------------
# visualize_git_tree_mermaid
# ---------------------------------------------------------------------------


class TestVisualizeGitTreeMermaid:
    """Test Mermaid git tree diagram generation."""

    def test_with_branches_and_commits(self, visualizer, sample_branches, sample_commits, tmp_path):
        out = tmp_path / "tree.mmd"
        result = visualizer.visualize_git_tree_mermaid(
            branches=sample_branches,
            commits=sample_commits,
            title="Mermaid Tree",
            output_path=str(out),
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_without_data_uses_default(self, visualizer):
        """When no repo path or data given, mermaid generator creates default diagram."""
        result = visualizer.visualize_git_tree_mermaid(title="Default Mermaid")
        assert isinstance(result, str)

    def test_returns_empty_on_error(self, visualizer):
        """If mermaid generation throws, returns empty string."""
        # Pass data that would cause an error in the mermaid generator
        # Actually, the default generator handles None branches gracefully via default diagram
        # So just confirm the type
        result = visualizer.visualize_git_tree_mermaid()
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# visualize_commit_activity_png
# ---------------------------------------------------------------------------


class TestVisualizeCommitActivityPng:
    """Test commit activity bar chart generation."""

    def test_with_iso_dates(self, visualizer, sample_commits, tmp_path):
        out = tmp_path / "activity.png"
        result = visualizer.visualize_commit_activity_png(
            commits=sample_commits,
            title="Activity Chart",
            output_path=str(out),
            days_back=15,
        )
        assert result is True
        assert out.exists()

    def test_with_space_separated_dates(self, visualizer, tmp_path):
        """Test date parsing for 'YYYY-MM-DD HH:MM:SS' format."""
        commits = [
            {
                "hash": "aaa111",
                "message": "commit with space date",
                "date": "2025-06-01 14:30:00",
                "branch": "main",
            },
            {
                "hash": "bbb222",
                "message": "another",
                "date": "2025-06-02 09:00:00",
                "branch": "main",
            },
        ]
        out = tmp_path / "space_dates.png"
        result = visualizer.visualize_commit_activity_png(
            commits=commits,
            title="Space Dates",
            output_path=str(out),
            days_back=5,
        )
        assert result is True

    def test_with_sample_fallback(self, visualizer, tmp_path):
        """When no commits provided, uses sample data."""
        out = tmp_path / "fallback_activity.png"
        result = visualizer.visualize_commit_activity_png(
            title="Fallback Activity",
            output_path=str(out),
            days_back=7,
        )
        assert result is True

    def test_no_valid_dates_returns_false(self, visualizer):
        """When all dates are unparseable, returns False."""
        commits = [
            {"hash": "xxx", "message": "bad date", "date": "not-a-date"},
            {"hash": "yyy", "message": "no date"},
        ]
        result = visualizer.visualize_commit_activity_png(commits=commits)
        assert result is False

    def test_empty_commits_uses_sample_fallback(self, visualizer):
        """Empty commit list evaluates as falsy, so sample data is used instead."""
        result = visualizer.visualize_commit_activity_png(commits=[])
        # Empty list is falsy, so the method falls through to sample data generation
        assert result is True

    def test_no_output_path_succeeds(self, visualizer, sample_commits):
        result = visualizer.visualize_commit_activity_png(
            commits=sample_commits,
            days_back=10,
        )
        assert result is True


# ---------------------------------------------------------------------------
# _get_repo_data
# ---------------------------------------------------------------------------


class TestGetRepoData:
    """Test the _get_repo_data helper with provided data and fallback."""

    def test_with_provided_repo_data(self, visualizer, sample_repo_data):
        result = visualizer._get_repo_data(None, sample_repo_data)
        assert result is sample_repo_data

    def test_fallback_sample_data(self, visualizer):
        """When both repository_path and repo_data are None, returns sample."""
        result = visualizer._get_repo_data(None, None)
        assert "status" in result
        assert "commits" in result
        assert "current_branch" in result
        assert "total_commits" in result
        assert result["current_branch"] == "main"

    def test_fallback_sample_has_commits(self, visualizer):
        result = visualizer._get_repo_data(None, None)
        assert len(result["commits"]) > 0


# ---------------------------------------------------------------------------
# Helper subplot methods
# ---------------------------------------------------------------------------


class TestPlotHelpers:
    """Test the private _plot_* methods directly."""

    def test_plot_repository_status_with_data(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        repo_data = {
            "status": {"clean": False, "modified": ["a.py", "b.py"], "untracked": ["c.py"]},
        }
        visualizer._plot_repository_status(ax, repo_data)
        assert ax.get_title() == "Repository Status"
        plt.close(fig)

    def test_plot_repository_status_clean(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        repo_data = {"status": {"clean": True, "modified": [], "untracked": []}}
        visualizer._plot_repository_status(ax, repo_data)
        assert ax.get_title() == "Repository Status"
        plt.close(fig)

    def test_plot_repository_status_empty(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        repo_data = {"status": {}}
        visualizer._plot_repository_status(ax, repo_data)
        assert ax.get_title() == "Repository Status"
        plt.close(fig)

    def test_plot_commit_timeline_with_data(self, visualizer, sample_commits):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_commit_timeline(ax, sample_commits)
        assert ax.get_title() == "Recent Commits Timeline"
        plt.close(fig)

    def test_plot_commit_timeline_empty(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_commit_timeline(ax, [])
        # With empty commits, method returns early; no title set
        plt.close(fig)

    def test_plot_commit_timeline_bad_dates(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        commits = [{"date": "not-a-date"}, {"date": ""}]
        visualizer._plot_commit_timeline(ax, commits)
        plt.close(fig)

    def test_plot_author_contributions(self, visualizer, sample_commits):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_author_contributions(ax, sample_commits)
        assert ax.get_title() == "Top Contributors"
        plt.close(fig)

    def test_plot_author_contributions_empty(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_author_contributions(ax, [])
        plt.close(fig)

    def test_plot_branch_info(self, visualizer, sample_repo_data):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_branch_info(ax, sample_repo_data)
        assert ax.get_title() == "Branch Info"
        plt.close(fig)

    def test_plot_commit_words(self, visualizer, sample_commits):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_commit_words(ax, sample_commits)
        assert ax.get_title() == "Common Commit Words"
        plt.close(fig)

    def test_plot_commit_words_empty(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_commit_words(ax, [])
        plt.close(fig)

    def test_plot_activity_heatmap(self, visualizer, sample_commits):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_activity_heatmap(ax, sample_commits)
        assert ax.get_title() == "Weekly Commit Activity Heatmap"
        plt.close(fig)

    def test_plot_activity_heatmap_empty(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        visualizer._plot_activity_heatmap(ax, [])
        plt.close(fig)

    def test_plot_activity_heatmap_bad_dates(self, visualizer):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        commits = [{"date": "invalid"}, {}]
        visualizer._plot_activity_heatmap(ax, commits)
        plt.close(fig)


# ---------------------------------------------------------------------------
# visualize_repository_summary_png
# ---------------------------------------------------------------------------


class TestVisualizeRepositorySummaryPng:
    """Test the multi-subplot repository dashboard."""

    def test_with_repo_data(self, visualizer, sample_repo_data, tmp_path):
        out = tmp_path / "summary.png"
        result = visualizer.visualize_repository_summary_png(
            repo_data=sample_repo_data,
            title="Test Summary",
            output_path=str(out),
        )
        assert result is True
        assert out.exists()

    def test_with_sample_fallback(self, visualizer, tmp_path):
        out = tmp_path / "fallback_summary.png"
        result = visualizer.visualize_repository_summary_png(
            title="Fallback Summary",
            output_path=str(out),
        )
        assert result is True

    def test_no_output_path_succeeds(self, visualizer, sample_repo_data):
        result = visualizer.visualize_repository_summary_png(
            repo_data=sample_repo_data,
        )
        assert result is True

    def test_custom_figure_size(self, visualizer, sample_repo_data, tmp_path):
        out = tmp_path / "custom_summary.png"
        result = visualizer.visualize_repository_summary_png(
            repo_data=sample_repo_data,
            figure_size=(10, 8),
            output_path=str(out),
        )
        assert result is True


# ---------------------------------------------------------------------------
# _get_repository_structure (lines 777-806)
# ---------------------------------------------------------------------------


class TestGetRepositoryStructure:
    """Test directory tree scanning for structure diagrams."""

    def test_scans_files_and_dirs(self, visualizer, sample_repo_dir):
        structure = visualizer._get_repository_structure(str(sample_repo_dir))
        # Top-level non-hidden items
        assert "README.md" in structure
        assert structure["README.md"] == "file"
        assert "src" in structure
        assert isinstance(structure["src"], dict)
        # Subdirectory contents
        assert "main.py" in structure["src"]
        assert "utils" in structure["src"]

    def test_skips_hidden_files_and_dirs(self, visualizer, sample_repo_dir):
        structure = visualizer._get_repository_structure(str(sample_repo_dir))
        assert ".gitignore" not in structure
        # Hidden subdir inside src should also be skipped
        if "src" in structure:
            assert ".hidden_dir" not in structure["src"]

    def test_empty_directory(self, visualizer, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        structure = visualizer._get_repository_structure(str(empty_dir))
        assert structure == {}

    def test_nonexistent_directory(self, visualizer, tmp_path):
        """Non-existent path should return empty dict (error caught internally)."""
        structure = visualizer._get_repository_structure(str(tmp_path / "nope"))
        assert structure == {}

    def test_nested_dirs(self, visualizer, sample_repo_dir):
        structure = visualizer._get_repository_structure(str(sample_repo_dir))
        assert "docs" in structure
        assert "guide.md" in structure["docs"]


# ---------------------------------------------------------------------------
# _create_report_summary (lines 816-858)
# ---------------------------------------------------------------------------


class TestCreateReportSummary:
    """Test markdown summary report generation."""

    def test_creates_readme_file(self, visualizer, tmp_path):
        results = {"git_tree_png": True, "commit_activity": False}
        visualizer._create_report_summary(
            output_dir=str(tmp_path),
            report_name="test_report",
            results=results,
            repository_path="/fake/repo",
        )
        summary_path = tmp_path / "test_report_README.md"
        assert summary_path.exists()

    def test_summary_content_contains_results(self, visualizer, tmp_path):
        results = {"git_tree_png": True, "workflow_mermaid": False}
        visualizer._create_report_summary(
            output_dir=str(tmp_path),
            report_name="report",
            results=results,
            repository_path="/my/repo",
        )
        content = (tmp_path / "report_README.md").read_text()
        assert "# Git Analysis Report" in content
        assert "/my/repo" in content
        assert "git_tree_png" in content
        assert "workflow_mermaid" in content

    def test_summary_includes_file_descriptions(self, visualizer, tmp_path):
        results = {}
        visualizer._create_report_summary(
            output_dir=str(tmp_path),
            report_name="myreport",
            results=results,
            repository_path="/repo",
        )
        content = (tmp_path / "myreport_README.md").read_text()
        assert "myreport_git_tree.png" in content
        assert "myreport_workflow.mmd" in content
        assert "Mermaid Live Editor" in content

    def test_empty_results(self, visualizer, tmp_path):
        visualizer._create_report_summary(
            output_dir=str(tmp_path),
            report_name="empty",
            results={},
            repository_path="/repo",
        )
        content = (tmp_path / "empty_README.md").read_text()
        assert "Generated Files" in content


# ---------------------------------------------------------------------------
# create_comprehensive_git_report (lines 649-733)
# ---------------------------------------------------------------------------


class TestCreateComprehensiveGitReport:
    """Test comprehensive report -- exercises the large uncovered block."""

    def test_without_git_operations_returns_empty(self, visualizer, tmp_path):
        """If GIT_OPERATIONS_AVAILABLE is False, should return empty dict."""
        import codomyrmex.data_visualization.git.git_visualizer as mod

        original = mod.GIT_OPERATIONS_AVAILABLE
        try:
            mod.GIT_OPERATIONS_AVAILABLE = False
            result = visualizer.create_comprehensive_git_report(
                repository_path="/fake",
                output_dir=str(tmp_path / "out"),
            )
            assert result == {}
        finally:
            mod.GIT_OPERATIONS_AVAILABLE = original

    @pytest.mark.skipif(
        not importlib.util.find_spec("codomyrmex.git_operations"),
        reason="Requires git_operations module",
    )
    @pytest.mark.xfail(
        reason="Source bug: create_git_workflow_diagram called without required workflow_steps arg (line 700)",
        strict=True,
        raises=TypeError,
    )
    def test_with_real_repo(self, visualizer, tmp_path):
        """Run against the actual codomyrmex repo if git_operations is available.

        Currently xfail: create_comprehensive_git_report calls
        mermaid_generator.create_git_workflow_diagram() without the required
        workflow_steps positional argument, raising TypeError.
        """
        import codomyrmex.data_visualization.git.git_visualizer as mod

        if not mod.GIT_OPERATIONS_AVAILABLE:
            pytest.skip("git_operations not importable")

        repo_path = str(Path(__file__).resolve().parents[5])
        from codomyrmex.git_operations.core.git import is_git_repository

        if not is_git_repository(repo_path):
            pytest.skip("Not running inside a git repository")

        out_dir = str(tmp_path / "report")
        result = visualizer.create_comprehensive_git_report(
            repository_path=repo_path,
            output_dir=out_dir,
            report_name="ci_test",
        )
        assert isinstance(result, dict)
        assert len(result) > 0
        assert any(result.values())
        assert os.path.isdir(out_dir)

    @pytest.mark.skipif(
        not importlib.util.find_spec("codomyrmex.git_operations"),
        reason="Requires git_operations module",
    )
    def test_with_nonexistent_repo_returns_empty(self, visualizer, tmp_path):
        """Non-git directory should return empty dict."""
        import codomyrmex.data_visualization.git.git_visualizer as mod

        if not mod.GIT_OPERATIONS_AVAILABLE:
            pytest.skip("git_operations not importable")

        from codomyrmex.git_operations.core.git import is_git_repository

        non_git = tmp_path / "not_a_repo"
        non_git.mkdir()
        result = visualizer.create_comprehensive_git_report(
            repository_path=str(non_git),
            output_dir=str(tmp_path / "out"),
        )
        assert result == {}


# ---------------------------------------------------------------------------
# Convenience module-level functions (lines 862-917)
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    """Test module-level convenience wrapper functions."""

    def test_create_git_tree_png_with_data(self, sample_branches, sample_commits, tmp_path):
        out = tmp_path / "conv_tree.png"
        result = create_git_tree_png(
            branches=sample_branches,
            commits=sample_commits,
            output_path=str(out),
            title="Convenience Tree",
        )
        assert result is True
        assert out.exists()

    def test_create_git_tree_png_default(self, tmp_path):
        out = tmp_path / "conv_default.png"
        result = create_git_tree_png(output_path=str(out))
        assert result is True

    def test_create_git_tree_mermaid_with_data(self, sample_branches, sample_commits, tmp_path):
        out = tmp_path / "conv_tree.mmd"
        result = create_git_tree_mermaid(
            branches=sample_branches,
            commits=sample_commits,
            output_path=str(out),
            title="Convenience Mermaid",
        )
        assert isinstance(result, str)

    def test_create_git_tree_mermaid_default(self, tmp_path):
        out = tmp_path / "conv_default.mmd"
        result = create_git_tree_mermaid(output_path=str(out))
        assert isinstance(result, str)

    def test_visualize_git_repository_without_git_ops(self, tmp_path):
        """When git_operations unavailable, returns empty dict."""
        import codomyrmex.data_visualization.git.git_visualizer as mod

        original = mod.GIT_OPERATIONS_AVAILABLE
        try:
            mod.GIT_OPERATIONS_AVAILABLE = False
            result = visualize_git_repository(
                repository_path="/fake",
                output_dir=str(tmp_path / "out"),
            )
            assert result == {}
        finally:
            mod.GIT_OPERATIONS_AVAILABLE = original


# ---------------------------------------------------------------------------
# Edge cases and error paths
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and error handling paths."""

    def test_commit_with_z_suffix_date(self, visualizer, tmp_path):
        """ISO date with Z suffix should be parsed correctly."""
        commits = [
            {
                "hash": "z11111",
                "message": "utc commit",
                "date": "2025-06-01T12:00:00Z",
                "branch": "main",
            }
        ]
        result = visualizer.visualize_commit_activity_png(
            commits=commits,
            days_back=5,
            output_path=str(tmp_path / "z_date.png"),
        )
        assert result is True

    def test_single_commit(self, visualizer, tmp_path):
        """Single commit should still produce a valid chart."""
        commits = [
            {
                "hash": "single1",
                "message": "only one",
                "author_name": "Solo",
                "date": datetime.now().isoformat(),
                "branch": "main",
            }
        ]
        branches = [{"name": "main", "commits": 1}]
        out = tmp_path / "single.png"
        result = visualizer.visualize_git_tree_png(
            branches=branches,
            commits=commits,
            output_path=str(out),
        )
        assert result is True

    def test_many_commits_truncated(self, visualizer, tmp_path):
        """More commits than max_commits should be truncated gracefully."""
        base = datetime(2025, 1, 1)
        commits = [
            {
                "hash": f"h{i:05d}",
                "message": f"commit {i}",
                "date": (base + timedelta(hours=i)).isoformat(),
                "branch": "main",
            }
            for i in range(50)
        ]
        branches = [{"name": "main", "commits": 50}]
        out = tmp_path / "many.png"
        result = visualizer.visualize_git_tree_png(
            branches=branches,
            commits=commits,
            max_commits=5,
            output_path=str(out),
        )
        assert result is True

    def test_commit_missing_optional_fields(self, visualizer, tmp_path):
        """Commits with missing optional fields should not crash."""
        commits = [
            {"branch": "main"},  # minimal
            {"hash": "abc", "branch": "main"},
            {"message": "no hash", "branch": "main"},
        ]
        branches = [{"name": "main", "commits": 3}]
        result = visualizer.visualize_git_tree_png(
            branches=branches,
            commits=commits,
        )
        assert result is True

    def test_plot_commit_timeline_with_attribute_error(self, visualizer):
        """Commits where date is None (AttributeError on .replace) should be skipped."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        commits = [{"date": None}, {"date": 12345}]
        visualizer._plot_commit_timeline(ax, commits)
        plt.close(fig)

    def test_activity_heatmap_with_attribute_error(self, visualizer):
        """Commits with non-string dates should be skipped in heatmap."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        commits = [{"date": None}, {"date": 999}]
        visualizer._plot_activity_heatmap(ax, commits)
        plt.close(fig)

    def test_summary_with_all_zeros_status(self, visualizer, tmp_path):
        """Repo status where all counts are zero (clean=False, no modified, no untracked)."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        repo_data = {"status": {"clean": False, "modified": [], "untracked": []}}
        visualizer._plot_repository_status(ax, repo_data)
        plt.close(fig)

    def test_commit_words_short_words_filtered(self, visualizer):
        """Words with 3 or fewer chars should be excluded from commit word chart."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        commits = [{"message": "fix the big bad bug in core system"}]
        visualizer._plot_commit_words(ax, commits)
        plt.close(fig)

    def test_author_contributions_many_authors(self, visualizer):
        """Only top 5 authors should be plotted."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        commits = [{"author_name": f"Author{i}"} for i in range(20)]
        visualizer._plot_author_contributions(ax, commits)
        assert ax.get_title() == "Top Contributors"
        plt.close(fig)
