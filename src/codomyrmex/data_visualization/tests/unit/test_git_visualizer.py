"""
Unit tests for the Git visualizer.

Tests Git-specific visualization functions with various inputs.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

from codomyrmex.data_visualization.git_visualizer import (
    GitVisualizer,
    visualize_git_repository,
    create_git_tree_png,
    create_git_tree_mermaid,
)
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class TestGitVisualizer:
    """Test the GitVisualizer class."""

    def setup_method(self):
        """Set up test environment."""
        self.visualizer = GitVisualizer()
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_visualizer_initialization(self):
        """Test visualizer initializes with correct colors and components."""
        assert self.visualizer is not None
        assert "main" in self.visualizer.colors
        assert "develop" in self.visualizer.colors
        assert "feature" in self.visualizer.colors
        assert self.visualizer.mermaid_generator is not None

    def test_get_branch_color(self):
        """Test branch color determination."""
        assert (
            self.visualizer._get_branch_color("main") == self.visualizer.colors["main"]
        )
        assert (
            self.visualizer._get_branch_color("master")
            == self.visualizer.colors["main"]
        )
        assert (
            self.visualizer._get_branch_color("develop")
            == self.visualizer.colors["develop"]
        )
        assert (
            self.visualizer._get_branch_color("feature/test")
            == self.visualizer.colors["feature"]
        )
        assert (
            self.visualizer._get_branch_color("hotfix/bug")
            == self.visualizer.colors["hotfix"]
        )
        assert (
            self.visualizer._get_branch_color("release/v1.0")
            == self.visualizer.colors["release"]
        )
        assert (
            self.visualizer._get_branch_color("unknown-branch")
            == self.visualizer.colors["commit"]
        )

    def test_generate_sample_commits(self):
        """Test sample commit generation."""
        commits = self.visualizer._generate_sample_commits(5)

        assert len(commits) == 5
        assert all("hash" in commit for commit in commits)
        assert all("message" in commit for commit in commits)
        assert all("author_name" in commit for commit in commits)
        assert all("date" in commit for commit in commits)
        assert all("branch" in commit for commit in commits)

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_git_tree_png_with_sample_data(self, mock_plt):
        """Test PNG Git tree visualization with sample data."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        output_path = os.path.join(self.test_dir, "test_git_tree.png")

        result = self.visualizer.visualize_git_tree_png(
            title="Test Git Tree", output_path=output_path
        )

        assert result is True
        mock_plt.subplots.assert_called()
        mock_ax.scatter.assert_called()
        mock_ax.axhline.assert_called()

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_git_tree_png_with_custom_data(self, mock_plt):
        """Test PNG Git tree visualization with custom data."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        branches = [
            {"name": "main", "commits": 5},
            {"name": "feature/test", "commits": 3},
        ]
        commits = [
            {"hash": "abc123", "message": "Initial commit", "branch": "main"},
            {"hash": "def456", "message": "Add feature", "branch": "feature/test"},
            {"hash": "ghi789", "message": "Fix bug", "branch": "main"},
        ]

        result = self.visualizer.visualize_git_tree_png(
            branches=branches, commits=commits, title="Custom Git Tree"
        )

        assert result is True
        mock_plt.subplots.assert_called()
        mock_ax.scatter.assert_called()

    @patch(
        "codomyrmex.data_visualization.git_visualizer.GIT_OPERATIONS_AVAILABLE", True
    )
    @patch("codomyrmex.data_visualization.git_visualizer.is_git_repository")
    @patch("codomyrmex.data_visualization.git_visualizer.get_commit_history")
    @patch("codomyrmex.data_visualization.git_visualizer.get_current_branch")
    def test_visualize_git_tree_mermaid_with_repo_path(
        self, mock_current_branch, mock_commit_history, mock_is_repo
    ):
        """Test Mermaid Git tree visualization with repository path."""
        mock_is_repo.return_value = True
        mock_current_branch.return_value = "main"
        mock_commit_history.return_value = [
            {"hash": "abc123", "message": "Test commit", "date": "2024-01-01"}
        ]

        output_path = os.path.join(self.test_dir, "test_git_tree.mmd")

        result = self.visualizer.visualize_git_tree_mermaid(
            repository_path=self.test_dir,
            title="Test Git Tree",
            output_path=output_path,
        )

        assert isinstance(result, str)
        assert "gitGraph" in result
        mock_is_repo.assert_called_once_with(self.test_dir)
        mock_commit_history.assert_called_once()

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_commit_activity_png_with_sample_data(self, mock_plt):
        """Test commit activity PNG visualization with sample data."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        output_path = os.path.join(self.test_dir, "test_activity.png")

        result = self.visualizer.visualize_commit_activity_png(
            title="Test Activity", output_path=output_path, days_back=7
        )

        assert result is True
        mock_plt.subplots.assert_called()
        mock_ax.bar.assert_called()

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_commit_activity_png_with_custom_commits(self, mock_plt):
        """Test commit activity PNG visualization with custom commit data."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        commits = [
            {"date": "2024-01-01 10:00:00"},
            {"date": "2024-01-01 14:00:00"},
            {"date": "2024-01-02 09:00:00"},
        ]

        result = self.visualizer.visualize_commit_activity_png(
            commits=commits, title="Custom Activity", days_back=5
        )

        assert result is True
        mock_plt.subplots.assert_called()
        mock_ax.bar.assert_called()

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_repository_summary_png_with_sample_data(self, mock_plt):
        """Test repository summary PNG visualization with sample data."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_gs = MagicMock()
        mock_fig.add_gridspec.return_value = mock_gs
        mock_fig.add_subplot.return_value = MagicMock()
        mock_plt.figure.return_value = mock_fig

        output_path = os.path.join(self.test_dir, "test_summary.png")

        result = self.visualizer.visualize_repository_summary_png(
            title="Test Summary", output_path=output_path
        )

        assert result is True
        mock_plt.figure.assert_called()

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_repository_summary_png_with_custom_data(self, mock_plt):
        """Test repository summary PNG visualization with custom repository data."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_gs = MagicMock()
        mock_fig.add_gridspec.return_value = mock_gs
        mock_ax = MagicMock()
        mock_fig.add_subplot.return_value = mock_ax
        mock_plt.figure.return_value = mock_fig

        repo_data = {
            "status": {
                "clean": False,
                "modified": ["file1.py"],
                "untracked": ["file2.py"],
            },
            "commits": [
                {
                    "date": "2024-01-01T10:00:00Z",
                    "author_name": "Alice",
                    "message": "Initial commit",
                },
                {
                    "date": "2024-01-02T11:00:00Z",
                    "author_name": "Bob",
                    "message": "Add feature",
                },
            ],
            "current_branch": "main",
            "total_commits": 10,
        }

        result = self.visualizer.visualize_repository_summary_png(
            repo_data=repo_data, title="Custom Summary"
        )

        assert result is True
        mock_plt.figure.assert_called()

    @patch(
        "codomyrmex.data_visualization.git_visualizer.GIT_OPERATIONS_AVAILABLE", True
    )
    @patch("codomyrmex.data_visualization.git_visualizer.check_git_availability")
    @patch("codomyrmex.data_visualization.git_visualizer.is_git_repository")
    @patch.object(GitVisualizer, "visualize_git_tree_png")
    @patch.object(GitVisualizer, "visualize_git_tree_mermaid")
    @patch.object(GitVisualizer, "visualize_commit_activity_png")
    @patch.object(GitVisualizer, "visualize_repository_summary_png")
    def test_create_comprehensive_git_report(
        self,
        mock_summary,
        mock_activity,
        mock_tree_mermaid,
        mock_tree_png,
        mock_is_repo,
        mock_git_available,
    ):
        """Test comprehensive Git report creation."""
        # Mock all the prerequisites
        mock_git_available.return_value = True
        mock_is_repo.return_value = True
        mock_tree_png.return_value = True
        mock_tree_mermaid.return_value = "gitGraph content"
        mock_activity.return_value = True
        mock_summary.return_value = True

        with patch.object(
            self.visualizer.mermaid_generator, "create_git_workflow_diagram"
        ) as mock_workflow:
            mock_workflow.return_value = "workflow content"

            with patch.object(
                self.visualizer, "_get_repository_structure"
            ) as mock_structure:
                mock_structure.return_value = {"src": {"main.py": "file"}}

                with patch.object(
                    self.visualizer.mermaid_generator,
                    "create_repository_structure_diagram",
                ) as mock_struct_diag:
                    mock_struct_diag.return_value = "structure content"

                    results = self.visualizer.create_comprehensive_git_report(
                        repository_path=self.test_dir,
                        output_dir=os.path.join(self.test_dir, "report"),
                        report_name="test_report",
                    )

        assert isinstance(results, dict)
        assert "git_tree_png" in results
        assert "git_tree_mermaid" in results
        assert "commit_activity" in results
        assert "repo_summary" in results
        assert "workflow_mermaid" in results
        assert "structure_mermaid" in results

        # Check that visualization methods were called
        mock_tree_png.assert_called_once()
        mock_tree_mermaid.assert_called_once()
        mock_activity.assert_called_once()
        mock_summary.assert_called_once()

    def test_get_repository_structure(self):
        """Test repository structure analysis."""
        # Create test directory structure
        test_repo = os.path.join(self.test_dir, "test_repo")
        os.makedirs(os.path.join(test_repo, "src"))
        os.makedirs(os.path.join(test_repo, "tests"))

        with open(os.path.join(test_repo, "README.md"), "w") as f:
            f.write("# Test repo")
        with open(os.path.join(test_repo, "src", "main.py"), "w") as f:
            f.write("print('hello')")

        structure = self.visualizer._get_repository_structure(test_repo)

        assert isinstance(structure, dict)
        assert "src" in structure
        assert "tests" in structure
        assert "README.md" in structure
        assert structure["README.md"] == "file"
        assert isinstance(structure["src"], dict)
        assert "main.py" in structure["src"]


class TestGitVisualizationConvenienceFunctions:
    """Test the convenience functions for Git visualization."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("codomyrmex.data_visualization.git_visualizer.GitVisualizer")
    def test_visualize_git_repository_function(self, mock_visualizer_class):
        """Test the convenience function for comprehensive Git repository visualization."""
        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.create_comprehensive_git_report.return_value = {"success": True}

        result = visualize_git_repository(
            repository_path=self.test_dir, output_dir="./output", report_name="test"
        )

        assert result == {"success": True}
        mock_visualizer.create_comprehensive_git_report.assert_called_once_with(
            self.test_dir, "./output", "test"
        )

    @patch("codomyrmex.data_visualization.git_visualizer.GitVisualizer")
    def test_create_git_tree_png_function(self, mock_visualizer_class):
        """Test the convenience function for PNG Git tree visualization."""
        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.visualize_git_tree_png.return_value = True

        result = create_git_tree_png(
            repository_path=self.test_dir, output_path="test.png"
        )

        assert result is True
        mock_visualizer.visualize_git_tree_png.assert_called_once()

    @patch("codomyrmex.data_visualization.git_visualizer.GitVisualizer")
    def test_create_git_tree_mermaid_function(self, mock_visualizer_class):
        """Test the convenience function for Mermaid Git tree visualization."""
        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.visualize_git_tree_mermaid.return_value = "gitGraph content"

        result = create_git_tree_mermaid(
            repository_path=self.test_dir, output_path="test.mmd"
        )

        assert result == "gitGraph content"
        mock_visualizer.visualize_git_tree_mermaid.assert_called_once()


class TestGitVisualizationErrorHandling:
    """Test error handling in Git visualization functions."""

    def setup_method(self):
        """Set up test environment."""
        self.visualizer = GitVisualizer()
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_git_tree_png_handles_empty_data(self, mock_plt):
        """Test PNG visualization handles empty data gracefully."""
        # Mock matplotlib to raise exception
        mock_plt.subplots.side_effect = Exception("Matplotlib error")

        result = self.visualizer.visualize_git_tree_png(
            branches=[], commits=[], title="Empty Data Test"
        )

        assert result is False

    @patch(
        "codomyrmex.data_visualization.git_visualizer.GIT_OPERATIONS_AVAILABLE", True
    )
    @patch("codomyrmex.data_visualization.git_visualizer.is_git_repository")
    def test_visualize_git_tree_mermaid_invalid_repo(self, mock_is_repo):
        """Test Mermaid visualization handles invalid repository."""
        mock_is_repo.return_value = False

        result = self.visualizer.visualize_git_tree_mermaid(
            repository_path="/invalid/path", title="Invalid Repo Test"
        )

        assert result == ""

    @patch("codomyrmex.data_visualization.git_visualizer.plt")
    def test_visualize_commit_activity_png_no_valid_dates(self, mock_plt):
        """Test commit activity handles commits with no valid dates."""
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        commits = [
            {"date": "invalid-date"},
            {"date": None},
            {"author_name": "Test"},  # No date field
        ]

        result = self.visualizer.visualize_commit_activity_png(
            commits=commits, title="Invalid Dates Test"
        )

        assert result is False

    @patch(
        "codomyrmex.data_visualization.git_visualizer.GIT_OPERATIONS_AVAILABLE", False
    )
    def test_create_comprehensive_git_report_no_git_operations(self):
        """Test comprehensive report handles missing git operations module."""
        results = self.visualizer.create_comprehensive_git_report(
            repository_path=self.test_dir, output_dir="./output", report_name="test"
        )

        assert results == {}


if __name__ == "__main__":
    pytest.main([__file__])
