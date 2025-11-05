"""
Unit tests for Git operations visualization integration.

Tests integration functions between git_operations and data_visualization.
"""

import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from codomyrmex.git_operations.visualization_integration import (
    create_git_analysis_report,
    visualize_commit_activity,
    visualize_git_branches,
)
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)
from codomyrmex.git_operations.visualization_integration import (
    _analyze_directory_structure,
    _get_created_files,
    _get_structure_stats,
    analyze_repository_structure,
    create_git_workflow_diagram,
    get_repository_metadata,
)


class TestGitAnalysisReport:
    """Test Git analysis report creation."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        False,
    )
    def test_create_git_analysis_report_no_visualization_module(self):
        """Test report creation when visualization module is not available."""
        result = create_git_analysis_report(self.test_dir)

        assert "error" in result
        assert "Visualization module not available" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.check_git_availability")
    def test_create_git_analysis_report_no_git(self, mock_git_available):
        """Test report creation when Git is not available."""
        mock_git_available.return_value = False

        result = create_git_analysis_report(self.test_dir)

        assert "error" in result
        assert "Git not available" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.check_git_availability")
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    def test_create_git_analysis_report_not_git_repo(
        self, mock_is_repo, mock_git_available
    ):
        """Test report creation for non-Git repository."""
        mock_git_available.return_value = True
        mock_is_repo.return_value = False

        result = create_git_analysis_report(self.test_dir)

        assert "error" in result
        assert "Not a Git repository" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.check_git_availability")
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch("codomyrmex.git_operations.visualization_integration.GitVisualizer")
    def test_create_git_analysis_report_success(
        self, mock_visualizer_class, mock_is_repo, mock_git_available
    ):
        """Test successful Git analysis report creation."""
        mock_git_available.return_value = True
        mock_is_repo.return_value = True

        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.create_comprehensive_git_report.return_value = {
            "git_tree_png": True,
            "git_tree_mermaid": True,
            "commit_activity": True,
        }

        result = create_git_analysis_report(
            repository_path=self.test_dir,
            output_dir=os.path.join(self.test_dir, "output"),
            report_name="test_report",
        )

        assert result["success"] is True
        assert result["repository_path"] == self.test_dir
        assert result["report_name"] == "test_report"
        assert "results" in result
        assert "files_created" in result

        mock_visualizer.create_comprehensive_git_report.assert_called_once()

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.check_git_availability")
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch("codomyrmex.git_operations.visualization_integration.GitVisualizer")
    def test_create_git_analysis_report_with_filters(
        self, mock_visualizer_class, mock_is_repo, mock_git_available
    ):
        """Test Git analysis report creation with PNG/Mermaid filters."""
        mock_git_available.return_value = True
        mock_is_repo.return_value = True

        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.create_comprehensive_git_report.return_value = {
            "git_tree_png": True,
            "git_tree_mermaid": True,
            "commit_activity": True,
        }

        # Test with PNG disabled
        result = create_git_analysis_report(
            repository_path=self.test_dir, include_png=False
        )

        assert result["success"] is True
        # PNG results should be filtered out
        png_results = [k for k in result["results"].keys() if "png" in k]
        assert len(png_results) == 0

        # Test with Mermaid disabled
        result = create_git_analysis_report(
            repository_path=self.test_dir, include_mermaid=False
        )

        assert result["success"] is True
        # Mermaid results should be filtered out
        mermaid_results = [k for k in result["results"].keys() if "mermaid" in k]
        assert len(mermaid_results) == 0


class TestBranchVisualization:
    """Test Git branch visualization functions."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        False,
    )
    def test_visualize_git_branches_no_visualization_module(self):
        """Test branch visualization when visualization module is not available."""
        result = visualize_git_branches(self.test_dir)

        assert "error" in result
        assert "Visualization module not available" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    def test_visualize_git_branches_not_git_repo(self, mock_is_repo):
        """Test branch visualization for non-Git repository."""
        mock_is_repo.return_value = False

        result = visualize_git_branches(self.test_dir)

        assert "error" in result
        assert "Not a Git repository" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch("codomyrmex.git_operations.visualization_integration.GitVisualizer")
    def test_visualize_git_branches_png_success(
        self, mock_visualizer_class, mock_is_repo
    ):
        """Test successful PNG branch visualization."""
        mock_is_repo.return_value = True

        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.visualize_git_tree_png.return_value = True

        result = visualize_git_branches(
            repository_path=self.test_dir, output_path="test.png", format_type="png"
        )

        assert result["success"] is True
        assert result["format"] == "png"
        assert "output_path" in result

        mock_visualizer.visualize_git_tree_png.assert_called_once()

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch("codomyrmex.git_operations.visualization_integration.GitVisualizer")
    def test_visualize_git_branches_mermaid_success(
        self, mock_visualizer_class, mock_is_repo
    ):
        """Test successful Mermaid branch visualization."""
        mock_is_repo.return_value = True

        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.visualize_git_tree_mermaid.return_value = "gitGraph content"

        result = visualize_git_branches(
            repository_path=self.test_dir, format_type="mermaid"
        )

        assert result["success"] is True
        assert result["format"] == "mermaid"
        assert result["content"] == "gitGraph content"

        mock_visualizer.visualize_git_tree_mermaid.assert_called_once()

    def test_visualize_git_branches_unsupported_format(self):
        """Test branch visualization with unsupported format."""
        with patch(
            "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
            True,
        ):
            with patch(
                "codomyrmex.git_operations.visualization_integration.is_git_repository"
            ) as mock_is_repo:
                mock_is_repo.return_value = True

                result = visualize_git_branches(
                    repository_path=self.test_dir, format_type="unsupported"
                )

                assert "error" in result
                assert "Unsupported format" in result["error"]


class TestCommitActivityVisualization:
    """Test commit activity visualization functions."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        False,
    )
    def test_visualize_commit_activity_no_visualization_module(self):
        """Test commit activity visualization when visualization module is not available."""
        result = visualize_commit_activity(self.test_dir)

        assert "error" in result
        assert "Visualization module not available" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    def test_visualize_commit_activity_not_git_repo(self, mock_is_repo):
        """Test commit activity visualization for non-Git repository."""
        mock_is_repo.return_value = False

        result = visualize_commit_activity(self.test_dir)

        assert "error" in result
        assert "Not a Git repository" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch("codomyrmex.git_operations.visualization_integration.GitVisualizer")
    def test_visualize_commit_activity_success(
        self, mock_visualizer_class, mock_is_repo
    ):
        """Test successful commit activity visualization."""
        mock_is_repo.return_value = True

        mock_visualizer = MagicMock()
        mock_visualizer_class.return_value = mock_visualizer
        mock_visualizer.visualize_commit_activity_png.return_value = True

        result = visualize_commit_activity(repository_path=self.test_dir, days_back=14)

        assert result["success"] is True
        assert result["days_analyzed"] == 14

        mock_visualizer.visualize_commit_activity_png.assert_called_once()


class TestWorkflowDiagram:
    """Test Git workflow diagram creation."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        False,
    )
    def test_create_git_workflow_diagram_no_visualization_module(self):
        """Test workflow diagram creation when visualization module is not available."""
        result = create_git_workflow_diagram()

        assert "error" in result
        assert "Visualization module not available" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch(
        "codomyrmex.git_operations.visualization_integration.create_git_workflow_diagram"
    )
    def test_create_git_workflow_diagram_feature_branch(self, mock_create_workflow):
        """Test feature branch workflow diagram creation."""
        mock_create_workflow.return_value = "flowchart TD"

        result = create_git_workflow_diagram(
            workflow_type="feature_branch", title="Feature Branch Workflow"
        )

        assert result["success"] is True
        assert result["workflow_type"] == "feature_branch"
        assert result["content"] == "flowchart TD"

        mock_create_workflow.assert_called_once()

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch(
        "codomyrmex.git_operations.visualization_integration.create_git_workflow_diagram"
    )
    def test_create_git_workflow_diagram_gitflow(self, mock_create_workflow):
        """Test GitFlow workflow diagram creation."""
        mock_create_workflow.return_value = "flowchart TD"

        result = create_git_workflow_diagram(
            workflow_type="gitflow", title="GitFlow Workflow"
        )

        assert result["success"] is True
        assert result["workflow_type"] == "gitflow"

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch(
        "codomyrmex.git_operations.visualization_integration.create_git_workflow_diagram"
    )
    def test_create_git_workflow_diagram_github_flow(self, mock_create_workflow):
        """Test GitHub Flow workflow diagram creation."""
        mock_create_workflow.return_value = "flowchart TD"

        result = create_git_workflow_diagram(
            workflow_type="github_flow", title="GitHub Flow Workflow"
        )

        assert result["success"] is True
        assert result["workflow_type"] == "github_flow"


class TestRepositoryStructureAnalysis:
    """Test repository structure analysis functions."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        False,
    )
    def test_analyze_repository_structure_no_visualization_module(self):
        """Test structure analysis when visualization module is not available."""
        result = analyze_repository_structure(self.test_dir)

        assert "error" in result
        assert "Visualization module not available" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    def test_analyze_repository_structure_not_git_repo(self, mock_is_repo):
        """Test structure analysis for non-Git repository."""
        mock_is_repo.return_value = False

        result = analyze_repository_structure(self.test_dir)

        assert "error" in result
        assert "Not a Git repository" in result["error"]

    @patch(
        "codomyrmex.git_operations.visualization_integration.VISUALIZATION_AVAILABLE",
        True,
    )
    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch(
        "codomyrmex.git_operations.visualization_integration.create_repository_structure_diagram"
    )
    def test_analyze_repository_structure_success(
        self, mock_create_structure, mock_is_repo
    ):
        """Test successful repository structure analysis."""
        mock_is_repo.return_value = True
        mock_create_structure.return_value = "graph TD"

        # Create test directory structure
        os.makedirs(os.path.join(self.test_dir, "src"))
        with open(os.path.join(self.test_dir, "README.md"), "w") as f:
            f.write("# Test")

        result = analyze_repository_structure(self.test_dir)

        assert result["success"] is True
        assert result["content"] == "graph TD"
        assert "structure" in result
        assert "stats" in result

        mock_create_structure.assert_called_once()


class TestRepositoryMetadata:
    """Test repository metadata functions."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    def test_get_repository_metadata_not_git_repo(self, mock_is_repo):
        """Test metadata retrieval for non-Git repository."""
        mock_is_repo.return_value = False

        result = get_repository_metadata(self.test_dir)

        assert "error" in result
        assert "Not a Git repository" in result["error"]

    @patch("codomyrmex.git_operations.visualization_integration.is_git_repository")
    @patch("codomyrmex.git_operations.visualization_integration.get_current_branch")
    @patch("codomyrmex.git_operations.visualization_integration.get_status")
    @patch("codomyrmex.git_operations.visualization_integration.get_commit_history")
    @patch("codomyrmex.git_operations.visualization_integration.list_stashes")
    def test_get_repository_metadata_success(
        self, mock_stashes, mock_commits, mock_status, mock_branch, mock_is_repo
    ):
        """Test successful repository metadata retrieval."""
        mock_is_repo.return_value = True
        mock_branch.return_value = "main"
        mock_status.return_value = {"clean": True}
        mock_commits.return_value = [
            {"author_name": "Alice", "message": "Commit 1"},
            {"author_name": "Bob", "message": "Commit 2"},
            {"author_name": "Alice", "message": "Commit 3"},
        ]
        mock_stashes.return_value = []

        result = get_repository_metadata(self.test_dir)

        assert result["is_git_repo"] is True
        assert result["current_branch"] == "main"
        assert result["status"]["clean"] is True
        assert "recent_commits" in result
        assert "commit_stats" in result
        assert result["commit_stats"]["total_recent_commits"] == 3
        assert result["commit_stats"]["unique_authors"] == 2
        assert len(result["commit_stats"]["top_authors"]) == 2
        assert result["commit_stats"]["top_authors"][0] == (
            "Alice",
            2,
        )  # Alice has 2 commits


class TestUtilityFunctions:
    """Test utility functions."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_analyze_directory_structure(self):
        """Test directory structure analysis."""
        # Create test structure
        os.makedirs(os.path.join(self.test_dir, "src", "utils"))
        os.makedirs(os.path.join(self.test_dir, "tests"))

        with open(os.path.join(self.test_dir, "README.md"), "w") as f:
            f.write("# Test")
        with open(os.path.join(self.test_dir, "src", "main.py"), "w") as f:
            f.write("print('hello')")
        with open(os.path.join(self.test_dir, "src", "utils", "helper.py"), "w") as f:
            f.write("def help(): pass")

        structure = _analyze_directory_structure(self.test_dir, max_depth=3)

        assert "src" in structure
        assert "tests" in structure
        assert "README.md" in structure
        assert structure["README.md"] == "file"
        assert "main.py" in structure["src"]
        assert structure["src"]["main.py"] == "file"
        assert "utils" in structure["src"]
        assert "helper.py" in structure["src"]["utils"]

    def test_analyze_directory_structure_max_depth(self):
        """Test directory structure analysis respects max depth."""
        # Create deep structure
        os.makedirs(os.path.join(self.test_dir, "level1", "level2", "level3"))
        with open(
            os.path.join(self.test_dir, "level1", "level2", "level3", "deep.txt"), "w"
        ) as f:
            f.write("deep file")

        structure = _analyze_directory_structure(self.test_dir, max_depth=2)

        assert "level1" in structure
        assert "level2" in structure["level1"]
        # level3 should not be included due to max_depth=2
        assert not structure["level1"]["level2"]  # Should be empty dict

    def test_get_structure_stats(self):
        """Test structure statistics calculation."""
        structure = {
            "src": {"main.py": "file", "utils": {"helper.py": "file"}},
            "tests": {},
            "README.md": "file",
        }

        stats = _get_structure_stats(structure)

        assert stats["directories"] == 3  # src, utils, tests
        assert stats["files"] == 3  # main.py, helper.py, README.md

    def test_get_created_files(self):
        """Test created files list generation."""
        # Create test output directory and files
        output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(output_dir)

        # Create some test files
        test_files = [
            "test_report_git_tree.png",
            "test_report_git_tree.mmd",
            "test_report_commit_activity.png",
            "test_report_README.md",
        ]

        for filename in test_files:
            with open(os.path.join(output_dir, filename), "w") as f:
                f.write("test content")

        results = {
            "git_tree_png": True,
            "git_tree_mermaid": True,
            "commit_activity": True,
            "repo_summary": False,  # This file shouldn't be included
        }

        files = _get_created_files(output_dir, "test_report", results)

        expected_files = [
            os.path.join(output_dir, "test_report_git_tree.png"),
            os.path.join(output_dir, "test_report_git_tree.mmd"),
            os.path.join(output_dir, "test_report_commit_activity.png"),
            os.path.join(output_dir, "test_report_README.md"),
        ]

        for expected_file in expected_files[:3]:  # First 3 should be included
            assert expected_file in files

        assert (
            expected_files[3] in files
        )  # README should always be included if it exists

        # repo_summary file should not be included since results[repo_summary] = False
        repo_summary_file = os.path.join(
            output_dir, "test_report_summary_dashboard.png"
        )
        assert repo_summary_file not in files


if __name__ == "__main__":
    pytest.main([__file__])
