"""
Git-specific visualization functions that integrate git_operations with data_visualization.

This module provides comprehensive Git visualization capabilities including:
- Git tree/branch visualizations (PNG and Mermaid)
- Commit history timelines
- Repository analysis charts
- Git workflow diagrams
- Integration with git_operations module data

The ``GitVisualizer`` class is composed from focused mixin classes:

- ``GitChartsMixin`` — tree/branch visualizations, commit activity charts
- ``GitDashboardMixin`` — repository summary dashboard subplot helpers

Uses logging_monitoring for logging.
Integrates with both matplotlib (PNG) and Mermaid (text diagrams).
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from codomyrmex.data_visualization.mermaid.mermaid_generator import (
    MermaidDiagramGenerator,
)
from codomyrmex.data_visualization.utils import save_plot
from codomyrmex.logging_monitoring import get_logger

from ._charts import GitChartsMixin
from ._dashboard import GitDashboardMixin

# Import git_operations if available
try:
    from codomyrmex.git_operations.core.git import (
        check_git_availability,
        is_git_repository,
    )

    GIT_OPERATIONS_AVAILABLE = True
except ImportError:
    GIT_OPERATIONS_AVAILABLE = False

logger = get_logger(__name__)


class GitVisualizer(GitChartsMixin, GitDashboardMixin):
    """Comprehensive Git visualization class supporting both PNG and Mermaid outputs.

    Tree/branch visualizations and commit activity charts are provided by
    ``GitChartsMixin``. Dashboard subplot helpers are provided by
    ``GitDashboardMixin``.
    """

    def __init__(self):
        """Initialize the Git visualizer."""
        self.mermaid_generator = MermaidDiagramGenerator()
        self.colors = {
            "main": "#2E8B57",
            "develop": "#4169E1",
            "feature": "#FF6347",
            "hotfix": "#DC143C",
            "release": "#9932CC",
            "commit": "#696969",
            "merge": "#FFD700",
            "tag": "#FF1493",
        }

    # =========================================================================
    # Repository Summary Dashboard
    # =========================================================================

    def visualize_repository_summary_png(
        self,
        repository_path: str | None = None,
        repo_data: dict[str, Any] | None = None,
        title: str = "Repository Summary",
        output_path: str | None = None,
        show_plot: bool = False,
        figure_size: tuple[int, int] = (14, 10),
    ) -> bool:
        """Create a comprehensive PNG dashboard of repository statistics."""
        logger.debug("Creating repository summary PNG dashboard: %s", title)

        try:
            repo_data = self._get_repo_data(repository_path, repo_data)

            fig = plt.figure(figsize=figure_size)
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

            commits = repo_data.get("commits", [])

            self._plot_repository_status(fig.add_subplot(gs[0, 0]), repo_data)
            self._plot_commit_timeline(fig.add_subplot(gs[0, 1:]), commits)
            self._plot_author_contributions(fig.add_subplot(gs[1, 0]), commits)
            self._plot_branch_info(fig.add_subplot(gs[1, 1]), repo_data)
            self._plot_commit_words(fig.add_subplot(gs[1, 2]), commits)
            self._plot_activity_heatmap(fig.add_subplot(gs[2, :]), commits)

            plt.suptitle(title, fontsize=16, fontweight="bold")

            if output_path:
                save_plot(fig, output_path, dpi=150)
            if show_plot:
                plt.show()
            else:
                plt.close(fig)

            logger.info(
                "Repository summary PNG dashboard '%s' generated successfully", title
            )
            return True

        except Exception as e:
            logger.error(
                "Error creating repository summary PNG dashboard: %s", e, exc_info=True
            )
            return False

    # =========================================================================
    # Comprehensive Report
    # =========================================================================

    def create_comprehensive_git_report(
        self,
        repository_path: str,
        output_dir: str,
        report_name: str = "git_analysis_report",
    ) -> dict[str, bool]:
        """Create a comprehensive Git analysis report with both PNG and Mermaid outputs."""
        logger.info("Creating comprehensive Git report for %s", repository_path)

        if not GIT_OPERATIONS_AVAILABLE:
            logger.error("Git operations module not available")
            return {}

        if not check_git_availability():
            logger.error("Git is not available on this system")
            return {}

        if not is_git_repository(repository_path):
            logger.error("Path %s is not a Git repository", repository_path)
            return {}

        os.makedirs(output_dir, exist_ok=True)

        results = {}

        results["git_tree_png"] = self.visualize_git_tree_png(
            repository_path=repository_path,
            title=f"Git Tree - {os.path.basename(repository_path)}",
            output_path=os.path.join(output_dir, f"{report_name}_git_tree.png"),
        )

        results["git_tree_mermaid"] = bool(
            self.visualize_git_tree_mermaid(
                repository_path=repository_path,
                title=f"Git Branch Diagram - {os.path.basename(repository_path)}",
                output_path=os.path.join(output_dir, f"{report_name}_git_tree.mmd"),
            )
        )

        results["commit_activity"] = self.visualize_commit_activity_png(
            repository_path=repository_path,
            title=f"Commit Activity - {os.path.basename(repository_path)}",
            output_path=os.path.join(output_dir, f"{report_name}_commit_activity.png"),
        )

        results["repo_summary"] = self.visualize_repository_summary_png(
            repository_path=repository_path,
            title=f"Repository Summary - {os.path.basename(repository_path)}",
            output_path=os.path.join(
                output_dir, f"{report_name}_summary_dashboard.png"
            ),
        )

        workflow_content = self.mermaid_generator.create_git_workflow_diagram(
            title=f"Git Workflow - {os.path.basename(repository_path)}",
            output_path=os.path.join(output_dir, f"{report_name}_workflow.mmd"),
        )
        results["workflow_mermaid"] = bool(workflow_content)

        try:
            repo_structure = self._get_repository_structure(repository_path)
            structure_content = (
                self.mermaid_generator.create_repository_structure_diagram(
                    repo_structure=repo_structure,
                    title=f"Repository Structure - {os.path.basename(repository_path)}",
                    output_path=os.path.join(
                        output_dir, f"{report_name}_structure.mmd"
                    ),
                )
            )
            results["structure_mermaid"] = bool(structure_content)
        except Exception as e:
            logger.error("Error creating structure diagram: %s", e)
            results["structure_mermaid"] = False

        self._create_report_summary(output_dir, report_name, results, repository_path)

        success_count = sum(results.values())
        total_count = len(results)
        logger.info(
            "Git report creation completed: %s/%s visualizations successful",
            success_count,
            total_count,
        )

        return results

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def _get_branch_color(self, branch_name: str) -> str:
        """Get color for branch based on name."""
        branch_lower = branch_name.lower()
        if "main" in branch_lower or "master" in branch_lower:
            return self.colors["main"]
        if "develop" in branch_lower:
            return self.colors["develop"]
        if "feature" in branch_lower:
            return self.colors["feature"]
        if "hotfix" in branch_lower:
            return self.colors["hotfix"]
        if "release" in branch_lower:
            return self.colors["release"]
        return self.colors["commit"]

    def _generate_sample_commits(self, days_back: int = 30) -> list[dict[str, Any]]:
        """Generate sample commit data for testing."""
        commits = []
        base_date = datetime.now()

        for i in range(days_back):
            date = base_date - timedelta(days=i)
            commits.append(
                {
                    "hash": f"a{i:02d}b{i:02d}c{i:02d}",
                    "message": f"Sample commit {i + 1}",
                    "author_name": "Developer" if i % 2 == 0 else "Contributor",
                    "author_email": "dev@example.com",
                    "date": date.isoformat(),
                    "branch": (
                        "main"
                        if i % 3 == 0
                        else ("develop" if i % 3 == 1 else "feature/sample")
                    ),
                }
            )

        return commits

    def _get_repository_structure(self, repository_path: str) -> dict[str, Any]:
        """Get basic repository directory structure."""
        structure = {}
        path = Path(repository_path)

        try:
            for item in path.iterdir():
                if item.name.startswith("."):
                    continue

                if item.is_dir():
                    substructure = {}
                    try:
                        for subitem in item.iterdir():
                            if subitem.name.startswith("."):
                                continue
                            if subitem.is_dir():
                                substructure[subitem.name] = {}
                            else:
                                substructure[subitem.name] = "file"
                    except PermissionError as e:
                        logger.debug("Permission denied reading subdirectory: %s", e)
                    structure[item.name] = substructure
                else:
                    structure[item.name] = "file"

        except Exception as e:
            logger.error("Error getting repository structure: %s", e)

        return structure

    def _create_report_summary(
        self,
        output_dir: str,
        report_name: str,
        results: dict[str, bool],
        repository_path: str,
    ):
        """Create a summary report file."""
        summary_content = [
            "# Git Analysis Report",
            "",
            f"**Repository:** {repository_path}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Report Name:** {report_name}",
            "",
            "## Generated Files",
            "",
        ]

        for viz_type, success in results.items():
            status = "+" if success else "x"
            summary_content.append(f"- {viz_type}: {status}")

        summary_content.extend(
            [
                "",
                "## File Descriptions",
                "",
                f"- **{report_name}_git_tree.png**: Git branch tree visualization",
                f"- **{report_name}_git_tree.mmd**: Mermaid git branch diagram",
                f"- **{report_name}_commit_activity.png**: Daily commit activity chart",
                f"- **{report_name}_summary_dashboard.png**: Comprehensive repository dashboard",
                f"- **{report_name}_workflow.mmd**: Git workflow diagram",
                f"- **{report_name}_structure.mmd**: Repository structure diagram",
                "",
                "## Usage",
                "",
                "PNG files can be viewed directly or embedded in documents.",
                "Mermaid (.mmd) files can be rendered using:",
                "- Mermaid Live Editor (mermaid.live)",
                "- GitHub/GitLab markdown rendering",
                "- Mermaid CLI tools",
                "- VS Code Mermaid extensions",
            ]
        )

        summary_path = os.path.join(output_dir, f"{report_name}_README.md")
        with open(summary_path, "w") as f:
            f.write("\n".join(summary_content))

        logger.info("Report summary saved to %s", summary_path)


# =========================================================================
# Convenience functions for easy import
# =========================================================================


def visualize_git_repository(
    repository_path: str,
    output_dir: str = "./git_analysis",
    report_name: str = "git_report",
) -> dict[str, bool]:
    """Create comprehensive Git repository visualizations."""
    visualizer = GitVisualizer()
    return visualizer.create_comprehensive_git_report(
        repository_path, output_dir, report_name
    )


def create_git_tree_png(
    repository_path: str | None = None,
    branches: list[dict[str, Any]] | None = None,
    commits: list[dict[str, Any]] | None = None,
    output_path: str = "git_tree.png",
    title: str = "Git Tree Visualization",
) -> bool:
    """Create a PNG Git tree visualization."""
    visualizer = GitVisualizer()
    return visualizer.visualize_git_tree_png(
        repository_path=repository_path,
        branches=branches,
        commits=commits,
        title=title,
        output_path=output_path,
    )


def create_git_tree_mermaid(
    repository_path: str | None = None,
    branches: list[dict[str, Any]] | None = None,
    commits: list[dict[str, Any]] | None = None,
    output_path: str = "git_tree.mmd",
    title: str = "Git Tree Diagram",
) -> str:
    """Create a Mermaid Git tree diagram."""
    visualizer = GitVisualizer()
    return visualizer.visualize_git_tree_mermaid(
        repository_path=repository_path,
        branches=branches,
        commits=commits,
        title=title,
        output_path=output_path,
    )


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "output" / "git_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Testing Git Visualization ---")

    visualizer = GitVisualizer()

    repo_path = sys.argv[1] if len(sys.argv) > 1 else None

    if repo_path and os.path.exists(repo_path):
        logger.info("Creating comprehensive Git report for: %s", repo_path)
        results = visualizer.create_comprehensive_git_report(
            repository_path=repo_path,
            output_dir=str(output_dir),
            report_name="test_git_report",
        )
        logger.info("Results: %s", results)
    else:
        logger.info("Testing with sample data")

        success = visualizer.visualize_git_tree_png(
            title="Sample Git Tree", output_path=str(output_dir / "sample_git_tree.png")
        )
        logger.info("Sample Git tree PNG: %s", "Success" if success else "Failed")

        mermaid_content = visualizer.visualize_git_tree_mermaid(
            title="Sample Git Diagram",
            output_path=str(output_dir / "sample_git_tree.mmd"),
        )
        logger.info(
            "Sample Git tree Mermaid: %s", "Success" if mermaid_content else "Failed"
        )

        success = visualizer.visualize_commit_activity_png(
            title="Sample Commit Activity",
            output_path=str(output_dir / "sample_commit_activity.png"),
        )
        logger.info("Sample commit activity: %s", "Success" if success else "Failed")

        success = visualizer.visualize_repository_summary_png(
            title="Sample Repository Summary",
            output_path=str(output_dir / "sample_repo_summary.png"),
        )
        logger.info("Sample repository summary: %s", "Success" if success else "Failed")

    logger.info("Git visualization examples generated in %s", output_dir)

    if not logging.getLogger("").hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of git_visualizer.py."
        )
