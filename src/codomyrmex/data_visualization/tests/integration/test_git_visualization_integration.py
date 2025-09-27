"""
Integration tests for Git visualization functionality.

Tests the complete integration between git_operations and data_visualization modules
for comprehensive Git repository analysis and visualization.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Test both modules' integration
from codomyrmex.data_visualization import (
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

    GitVisualizer,
    create_git_tree_png,
    create_git_tree_mermaid,
    create_git_branch_diagram,
    create_git_workflow_diagram,
    visualize_git_repository,
)

try:
    from codomyrmex.git_operations import (
        initialize_git_repository,
        add_files,
        commit_changes,
        create_branch,
        switch_branch,
        get_status,
        get_commit_history,
    )
    from codomyrmex.git_operations.visualization_integration import (
        create_git_analysis_report,
        visualize_git_branches,
        visualize_commit_activity,
        get_repository_metadata,
    )

    GIT_OPS_AVAILABLE = True
except ImportError:
    GIT_OPS_AVAILABLE = False


@pytest.mark.skipif(not GIT_OPS_AVAILABLE, reason="git_operations module not available")
class TestGitVisualizationIntegration:
    """Integration tests for Git visualization with real Git operations."""

    def setup_method(self):
        """Set up test environment with a real Git repository."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_dir = os.path.join(self.test_dir, "test_repo")
        self.output_dir = os.path.join(self.test_dir, "output")

        os.makedirs(self.repo_dir)
        os.makedirs(self.output_dir)

        # Initialize Git repository for testing
        self._setup_test_repository()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _setup_test_repository(self):
        """Set up a test Git repository with sample content."""
        # Initialize repository
        success = initialize_git_repository(self.repo_dir, initial_commit=False)
        assert success, "Failed to initialize test repository"

        # Create initial file and commit
        readme_path = os.path.join(self.repo_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(
                "# Test Repository\n\nThis is a test repository for visualization integration testing."
            )

        add_files(["README.md"], self.repo_dir)
        commit_changes("Initial commit: Add README", self.repo_dir)

        # Create source directory structure
        src_dir = os.path.join(self.repo_dir, "src")
        os.makedirs(src_dir)

        main_py_path = os.path.join(src_dir, "main.py")
        with open(main_py_path, "w") as f:
            f.write(
                """#!/usr/bin/env python3
\"\"\"
Main application module.
\"\"\"

def main():
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    main()
"""
            )

        add_files(["src/main.py"], self.repo_dir)
        commit_changes("Add main application module", self.repo_dir)

        # Create and switch to feature branch
        create_branch("feature/authentication", self.repo_dir)

        auth_py_path = os.path.join(src_dir, "auth.py")
        with open(auth_py_path, "w") as f:
            f.write(
                """\"\"\"
Authentication module.
\"\"\"

class AuthManager:
    def __init__(self):
        self.users = {}
    
    def login(self, username, password):
        # Simple authentication logic
        return username in self.users and self.users[username] == password
    
    def register(self, username, password):
        self.users[username] = password
        return True
"""
            )

        add_files(["src/auth.py"], self.repo_dir)
        commit_changes("Add authentication module", self.repo_dir)

        # Add tests
        tests_dir = os.path.join(self.repo_dir, "tests")
        os.makedirs(tests_dir)

        test_auth_path = os.path.join(tests_dir, "test_auth.py")
        with open(test_auth_path, "w") as f:
            f.write(
                """\"\"\"
Tests for authentication module.
\"\"\"
import unittest
from src.auth import AuthManager

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        self.auth = AuthManager()
    
    def test_register_and_login(self):
        self.assertTrue(self.auth.register("testuser", "password123"))
        self.assertTrue(self.auth.login("testuser", "password123"))
        self.assertFalse(self.auth.login("testuser", "wrongpassword"))

if __name__ == "__main__":
    unittest.main()
"""
            )

        add_files(["tests/test_auth.py"], self.repo_dir)
        commit_changes("Add authentication tests", self.repo_dir)

        # Switch back to main and merge
        switch_branch("main", self.repo_dir)
        # Note: For testing, we'll skip the merge to keep branches separate

        # Create one more commit on main
        config_path = os.path.join(self.repo_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump({"app_name": "test_app", "version": "1.0.0"}, f, indent=2)

        add_files(["config.json"], self.repo_dir)
        commit_changes("Add application configuration", self.repo_dir)

    def test_comprehensive_git_visualization_report(self):
        """Test creating a comprehensive Git visualization report."""
        visualizer = GitVisualizer()

        # Create comprehensive report
        results = visualizer.create_comprehensive_git_report(
            repository_path=self.repo_dir,
            output_dir=self.output_dir,
            report_name="integration_test_report",
        )

        # Verify results
        assert isinstance(results, dict)
        assert len(results) > 0

        # Check that at least some visualizations were successful
        success_count = sum(1 for success in results.values() if success)
        assert (
            success_count >= 3
        ), f"Expected at least 3 successful visualizations, got {success_count}"

        # Verify output files were created
        expected_files = [
            "integration_test_report_git_tree.png",
            "integration_test_report_git_tree.mmd",
            "integration_test_report_commit_activity.png",
            "integration_test_report_summary_dashboard.png",
            "integration_test_report_workflow.mmd",
            "integration_test_report_structure.mmd",
            "integration_test_report_README.md",
        ]

        created_files = []
        for filename in expected_files:
            file_path = os.path.join(self.output_dir, filename)
            if os.path.exists(file_path):
                created_files.append(filename)
                # Verify file is not empty
                assert os.path.getsize(file_path) > 0, f"File {filename} is empty"

        assert (
            len(created_files) >= 4
        ), f"Expected at least 4 files to be created, got {created_files}"

        # Verify README was created and contains expected content
        readme_path = os.path.join(self.output_dir, "integration_test_report_README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                readme_content = f.read()
                assert "Git Analysis Report" in readme_content
                assert self.repo_dir in readme_content
                assert "integration_test_report" in readme_content

    def test_git_operations_integration_report(self):
        """Test Git analysis report through the integration module."""
        result = create_git_analysis_report(
            repository_path=self.repo_dir,
            output_dir=self.output_dir,
            report_name="git_ops_integration_test",
            include_png=True,
            include_mermaid=True,
        )

        # Verify successful report creation
        assert result["success"] is True
        assert result["repository_path"] == self.repo_dir
        assert result["report_name"] == "git_ops_integration_test"
        assert "results" in result
        assert "files_created" in result

        # Verify some files were created
        assert len(result["files_created"]) >= 3

        # Check that files actually exist
        for file_path in result["files_created"]:
            assert os.path.exists(file_path), f"File {file_path} does not exist"
            assert os.path.getsize(file_path) > 0, f"File {file_path} is empty"

    def test_individual_visualization_functions(self):
        """Test individual visualization functions with real Git data."""
        # Test PNG Git tree visualization
        png_result = visualize_git_branches(
            repository_path=self.repo_dir,
            output_path=os.path.join(self.output_dir, "branches.png"),
            format_type="png",
        )

        assert png_result["success"] is True
        assert png_result["format"] == "png"
        assert os.path.exists(png_result["output_path"])

        # Test Mermaid Git tree visualization
        mermaid_result = visualize_git_branches(
            repository_path=self.repo_dir,
            output_path=os.path.join(self.output_dir, "branches.mmd"),
            format_type="mermaid",
        )

        assert mermaid_result["success"] is True
        assert mermaid_result["format"] == "mermaid"
        assert isinstance(mermaid_result["content"], str)
        assert len(mermaid_result["content"]) > 0
        assert os.path.exists(mermaid_result["output_path"])

        # Test commit activity visualization
        activity_result = visualize_commit_activity(
            repository_path=self.repo_dir,
            output_path=os.path.join(self.output_dir, "activity.png"),
            days_back=30,
        )

        assert activity_result["success"] is True
        assert os.path.exists(activity_result["output_path"])

    def test_repository_metadata_extraction(self):
        """Test extracting comprehensive repository metadata."""
        metadata = get_repository_metadata(self.repo_dir)

        assert "error" not in metadata
        assert metadata["is_git_repo"] is True
        assert metadata["name"] == "test_repo"
        assert metadata["current_branch"] in [
            "main",
            "master",
        ]  # Could be either depending on Git config

        # Verify commit statistics
        assert "commit_stats" in metadata
        commit_stats = metadata["commit_stats"]
        assert commit_stats["total_recent_commits"] >= 3  # We made at least 3 commits
        assert commit_stats["unique_authors"] >= 1

        # Verify structure statistics
        assert "structure_stats" in metadata
        structure_stats = metadata["structure_stats"]
        assert structure_stats["directories"] >= 2  # src, tests
        assert (
            structure_stats["files"] >= 3
        )  # README.md, main.py, auth.py, test_auth.py, config.json

    def test_convenience_functions_with_real_data(self):
        """Test convenience functions with real Git repository data."""
        # Test comprehensive visualization function
        results = visualize_git_repository(
            repository_path=self.repo_dir,
            output_dir=self.output_dir,
            report_name="convenience_test",
        )

        assert isinstance(results, dict)
        success_count = sum(1 for success in results.values() if success)
        assert success_count >= 2, "Expected at least 2 successful visualizations"

        # Test individual PNG creation
        png_success = create_git_tree_png(
            repository_path=self.repo_dir,
            output_path=os.path.join(self.output_dir, "convenience_tree.png"),
            title="Convenience Function Test Tree",
        )

        assert png_success is True
        assert os.path.exists(os.path.join(self.output_dir, "convenience_tree.png"))

        # Test individual Mermaid creation
        mermaid_content = create_git_tree_mermaid(
            repository_path=self.repo_dir,
            output_path=os.path.join(self.output_dir, "convenience_tree.mmd"),
            title="Convenience Function Test Diagram",
        )

        assert isinstance(mermaid_content, str)
        assert len(mermaid_content) > 0
        assert "gitGraph" in mermaid_content
        assert os.path.exists(os.path.join(self.output_dir, "convenience_tree.mmd"))

    def test_workflow_diagram_generation(self):
        """Test Git workflow diagram generation."""
        # Test different workflow types
        workflow_types = ["feature_branch", "gitflow", "github_flow"]

        for workflow_type in workflow_types:
            from codomyrmex.git_operations.visualization_integration import (
                create_git_workflow_diagram,
            )

            result = create_git_workflow_diagram(
                workflow_type=workflow_type,
                output_path=os.path.join(
                    self.output_dir, f"workflow_{workflow_type}.mmd"
                ),
                title=f"{workflow_type.replace('_', ' ').title()} Workflow",
            )

            assert (
                result["success"] is True
            ), f"Failed to create {workflow_type} workflow"
            assert result["workflow_type"] == workflow_type
            assert isinstance(result["content"], str)
            assert len(result["content"]) > 0
            assert os.path.exists(result["output_path"])

            # Verify content contains expected elements
            content = result["content"]
            assert "flowchart TD" in content or "flowchart" in content

    def test_mermaid_content_validation(self):
        """Test that generated Mermaid content is valid."""
        # Generate various Mermaid diagrams and validate their structure
        visualizer = GitVisualizer()

        # Test Git branch diagram
        branch_content = visualizer.visualize_git_tree_mermaid(
            repository_path=self.repo_dir, title="Validation Test Branch Diagram"
        )

        assert "gitGraph" in branch_content
        assert "commit" in branch_content

        # Test workflow diagram
        workflow_content = create_git_workflow_diagram(
            workflow_type="feature_branch", title="Validation Test Workflow"
        )

        assert workflow_content["success"] is True
        content = workflow_content["content"]
        assert "flowchart TD" in content
        assert "-->" in content or "--->" in content  # Mermaid connection syntax

        # Test structure diagram
        structure_content = create_git_branch_diagram(title="Validation Test Structure")

        assert isinstance(structure_content, str)
        assert len(structure_content) > 0

    def test_error_handling_with_real_repository(self):
        """Test error handling with edge cases in real repository."""
        visualizer = GitVisualizer()

        # Test with non-existent repository
        results = visualizer.create_comprehensive_git_report(
            repository_path="/non/existent/path",
            output_dir=self.output_dir,
            report_name="error_test",
        )

        assert results == {}  # Should return empty dict for invalid repo

        # Test with valid repo but invalid output directory
        with patch("os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = PermissionError("Permission denied")

            # This should handle the error gracefully
            try:
                results = visualizer.create_comprehensive_git_report(
                    repository_path=self.repo_dir,
                    output_dir="/invalid/path/that/requires/permissions",
                    report_name="permission_test",
                )
                # If it doesn't raise an exception, it should return limited results
                assert isinstance(results, dict)
            except PermissionError:
                # This is acceptable behavior too
                pass


class TestGitVisualizationWithSampleData:
    """Test Git visualization with sample data (no real Git repository required)."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir)

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_visualization_with_sample_data(self):
        """Test visualization functions with sample data."""
        visualizer = GitVisualizer()

        # Test PNG visualization with sample data
        success = visualizer.visualize_git_tree_png(
            title="Sample Data Git Tree",
            output_path=os.path.join(self.output_dir, "sample_tree.png"),
        )

        assert success is True
        assert os.path.exists(os.path.join(self.output_dir, "sample_tree.png"))

        # Test Mermaid visualization with sample data
        content = visualizer.visualize_git_tree_mermaid(
            title="Sample Data Git Diagram",
            output_path=os.path.join(self.output_dir, "sample_tree.mmd"),
        )

        assert isinstance(content, str)
        assert len(content) > 0
        assert os.path.exists(os.path.join(self.output_dir, "sample_tree.mmd"))

        # Test commit activity with sample data
        success = visualizer.visualize_commit_activity_png(
            title="Sample Commit Activity",
            output_path=os.path.join(self.output_dir, "sample_activity.png"),
        )

        assert success is True
        assert os.path.exists(os.path.join(self.output_dir, "sample_activity.png"))

    def test_custom_data_visualization(self):
        """Test visualization with custom provided data."""
        visualizer = GitVisualizer()

        # Custom branch data
        branches = [
            {"name": "main", "commits": 10},
            {"name": "develop", "commits": 8},
            {"name": "feature/user-auth", "commits": 5},
            {"name": "hotfix/security-fix", "commits": 2},
        ]

        # Custom commit data
        commits = [
            {
                "hash": "a1b2c3d",
                "message": "Initial commit",
                "author": "Alice",
                "branch": "main",
                "date": "2024-01-01T10:00:00Z",
            },
            {
                "hash": "e4f5g6h",
                "message": "Add user authentication",
                "author": "Bob",
                "branch": "feature/user-auth",
                "date": "2024-01-05T14:30:00Z",
            },
            {
                "hash": "i7j8k9l",
                "message": "Fix security vulnerability",
                "author": "Charlie",
                "branch": "hotfix/security-fix",
                "date": "2024-01-10T09:15:00Z",
            },
            {
                "hash": "m1n2o3p",
                "message": "Update documentation",
                "author": "Alice",
                "branch": "develop",
                "date": "2024-01-12T16:45:00Z",
            },
            {
                "hash": "q4r5s6t",
                "message": "Refactor authentication module",
                "author": "Bob",
                "branch": "feature/user-auth",
                "date": "2024-01-15T11:20:00Z",
            },
        ]

        # Test PNG with custom data
        success = visualizer.visualize_git_tree_png(
            branches=branches,
            commits=commits,
            title="Custom Data Git Tree",
            output_path=os.path.join(self.output_dir, "custom_tree.png"),
        )

        assert success is True
        assert os.path.exists(os.path.join(self.output_dir, "custom_tree.png"))

        # Test Mermaid with custom data
        content = visualizer.visualize_git_tree_mermaid(
            branches=[
                {"name": b["name"], "created_at": "2024-01-01", "merged": True}
                for b in branches[:2]
            ],
            commits=commits,
            title="Custom Data Git Diagram",
            output_path=os.path.join(self.output_dir, "custom_tree.mmd"),
        )

        assert isinstance(content, str)
        assert len(content) > 0
        assert "feature/user-auth" in content or "main" in content
        assert os.path.exists(os.path.join(self.output_dir, "custom_tree.mmd"))

        # Test commit activity with custom commits
        success = visualizer.visualize_commit_activity_png(
            commits=commits,
            title="Custom Commit Activity",
            output_path=os.path.join(self.output_dir, "custom_activity.png"),
            days_back=15,
        )

        assert success is True
        assert os.path.exists(os.path.join(self.output_dir, "custom_activity.png"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
