"""
Git-specific visualization functions that integrate git_operations with data_visualization.

This module provides comprehensive Git visualization capabilities including:
- Git tree/branch visualizations (PNG and Mermaid)
- Commit history timelines
- Repository analysis charts
- Git workflow diagrams
- Integration with git_operations module data

- Uses logging_monitoring for logging.
- Integrates with both matplotlib (PNG) and Mermaid (text diagrams).
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# Import from data_visualization module
from codomyrmex.data_visualization.charts.plot_utils import (
    apply_common_aesthetics,
    get_codomyrmex_logger,
    save_plot,
)
from codomyrmex.data_visualization.mermaid.mermaid_generator import (
    MermaidDiagramGenerator,
)

# Import git_operations if available
try:
    from codomyrmex.git_operations.core.git import (
        check_git_availability,
        get_commit_history,
        get_current_branch,
        get_status,
        is_git_repository,
    )

    GIT_OPERATIONS_AVAILABLE = True
except ImportError:
    GIT_OPERATIONS_AVAILABLE = False

logger = get_codomyrmex_logger(__name__)


class GitVisualizer:
    """Comprehensive Git visualization class supporting both PNG and Mermaid outputs."""

    def __init__(self):
        """Initialize the Git visualizer."""
        self.mermaid_generator = MermaidDiagramGenerator()
        self.colors = {
            "main": "#2E8B57",  # Sea green
            "develop": "#4169E1",  # Royal blue
            "feature": "#FF6347",  # Tomato
            "hotfix": "#DC143C",  # Crimson
            "release": "#9932CC",  # Dark orchid
            "commit": "#696969",  # Dim gray
            "merge": "#FFD700",  # Gold
            "tag": "#FF1493",  # Deep pink
        }

    def visualize_git_tree_png(
        self,
        repository_path: str = None,
        branches: list[dict[str, Any]] = None,
        commits: list[dict[str, Any]] = None,
        title: str = "Git Tree Visualization",
        output_path: str = None,
        show_plot: bool = False,
        figure_size: tuple[int, int] = (12, 8),
        max_commits: int = 20,
    ) -> bool:
        """
        Create a PNG visualization of Git tree/branches using matplotlib.

        Args:
            repository_path: Path to Git repository (if None, uses provided data)
            branches: List of branch dictionaries (used if repository_path is None)
            commits: List of commit dictionaries (used if repository_path is None)
            title: Plot title
            output_path: File path to save PNG
            show_plot: Whether to display the plot
            figure_size: Size of the figure (width, height)
            max_commits: Maximum number of commits to show

        Returns:
            True if successful, False otherwise
        """
        logger.debug(f"Creating Git tree PNG visualization: {title}")

        try:
            # Get data from repository or use provided data
            if repository_path and GIT_OPERATIONS_AVAILABLE:
                if not is_git_repository(repository_path):
                    logger.error(f"Path {repository_path} is not a Git repository")
                    return False

                commits_data = get_commit_history(max_commits, repository_path)
                current_branch = get_current_branch(repository_path)

                # Convert to our expected format
                commits = [
                    {
                        "hash": commit["hash"][:8],
                        "message": commit["message"],
                        "author": commit["author_name"],
                        "date": commit["date"],
                        "branch": current_branch or "main",
                    }
                    for commit in commits_data
                ]

                branches = [{"name": current_branch or "main", "commits": len(commits)}]

            elif branches and commits:
                # Use provided data
                pass
            else:
                # Use sample data for demonstration
                branches = [
                    {"name": "main", "commits": 8},
                    {"name": "develop", "commits": 5},
                    {"name": "feature/auth", "commits": 3},
                ]
                commits = self._generate_sample_commits()

            # Create the visualization
            fig, ax = plt.subplots(figsize=figure_size)

            # Plot branches as horizontal lanes
            branch_y_positions = {}
            for i, branch in enumerate(branches):
                branch_name = branch["name"]
                y_pos = len(branches) - i - 1
                branch_y_positions[branch_name] = y_pos

                # Draw branch line
                color = self._get_branch_color(branch_name)
                ax.axhline(y=y_pos, color=color, linewidth=2, alpha=0.3)

                # Add branch label
                ax.text(
                    -0.5,
                    y_pos,
                    branch_name,
                    fontweight="bold",
                    color=color,
                    va="center",
                    ha="right",
                )

            # Plot commits
            for i, commit in enumerate(commits[:max_commits]):
                branch = commit.get("branch", "main")
                y_pos = branch_y_positions.get(branch, 0)
                x_pos = i

                # Plot commit point
                color = self._get_branch_color(branch)
                ax.scatter(x_pos, y_pos, color=color, s=100, zorder=3)

                # Add commit hash below point
                ax.text(
                    x_pos,
                    y_pos - 0.15,
                    commit.get("hash", ""),
                    fontsize=8,
                    ha="center",
                    va="top",
                )

                # Add commit message (rotated for space)
                message = commit.get("message", "")[:30]
                ax.text(
                    x_pos,
                    y_pos + 0.15,
                    message,
                    fontsize=8,
                    ha="center",
                    va="bottom",
                    rotation=45,
                )

            # Connect commits with lines
            for i in range(1, min(len(commits), max_commits)):
                prev_commit = commits[i - 1]
                curr_commit = commits[i]
                prev_branch = prev_commit.get("branch", "main")
                curr_branch = curr_commit.get("branch", "main")

                prev_y = branch_y_positions.get(prev_branch, 0)
                curr_y = branch_y_positions.get(curr_branch, 0)

                # Draw connection line
                ax.plot([i - 1, i], [prev_y, curr_y], "k-", alpha=0.5, zorder=1)

            # Customize the plot
            apply_common_aesthetics(ax, title, "Commits (timeline →)", "Branches")
            ax.set_xlim(-1, max(max_commits - 1, 5))
            ax.set_ylim(-0.5, len(branches) - 0.5)
            ax.set_yticks(range(len(branches)))
            ax.set_yticklabels([b["name"] for b in reversed(branches)])

            # Add legend
            legend_patches = [
                mpatches.Patch(color=self.colors[key], label=key.capitalize())
                for key in ["main", "develop", "feature", "hotfix"]
                if any(key in b["name"].lower() for b in branches)
            ]
            if legend_patches:
                ax.legend(handles=legend_patches, loc="upper right")

            plt.tight_layout()

            if output_path:
                save_plot(fig, output_path)

            if show_plot:
                plt.show()
            else:
                plt.close(fig)

            logger.info(f"Git tree PNG visualization '{title}' generated successfully")
            return True

        except Exception as e:
            logger.error(
                f"Error creating Git tree PNG visualization: {e}", exc_info=True
            )
            return False

    def visualize_git_tree_mermaid(
        self,
        repository_path: str = None,
        branches: list[dict[str, Any]] = None,
        commits: list[dict[str, Any]] = None,
        title: str = "Git Tree Diagram",
        output_path: str = None,
    ) -> str:
        """
        Create a Mermaid Git tree/branch diagram.

        Args:
            repository_path: Path to Git repository
            branches: List of branch dictionaries
            commits: List of commit dictionaries
            title: Diagram title
            output_path: File path to save Mermaid file

        Returns:
            Mermaid diagram content as string
        """
        logger.debug(f"Creating Git tree Mermaid diagram: {title}")

        try:
            # Get data from repository if available
            if repository_path and GIT_OPERATIONS_AVAILABLE:
                if not is_git_repository(repository_path):
                    logger.error(f"Path {repository_path} is not a Git repository")
                    return ""

                commits_data = get_commit_history(20, repository_path)
                current_branch = get_current_branch(repository_path)

                # Convert to expected format
                branches = [
                    {"name": current_branch or "main", "created_at": "2024-01-01"}
                ]
                commits = [
                    {
                        "hash": commit["hash"],
                        "message": commit["message"],
                        "branch": current_branch or "main",
                        "date": commit["date"],
                    }
                    for commit in commits_data
                ]

            # Create Mermaid diagram
            mermaid_content = self.mermaid_generator.create_git_branch_diagram(
                branches=branches, commits=commits, title=title, output_path=output_path
            )

            logger.info(f"Git tree Mermaid diagram '{title}' generated successfully")
            return mermaid_content

        except Exception as e:
            logger.error(f"Error creating Git tree Mermaid diagram: {e}", exc_info=True)
            return ""

    def visualize_commit_activity_png(
        self,
        repository_path: str = None,
        commits: list[dict[str, Any]] = None,
        title: str = "Commit Activity",
        output_path: str = None,
        show_plot: bool = False,
        figure_size: tuple[int, int] = (12, 6),
        days_back: int = 30,
    ) -> bool:
        """
        Create a PNG chart showing commit activity over time.

        Args:
            repository_path: Path to Git repository
            commits: List of commit dictionaries
            title: Plot title
            output_path: File path to save PNG
            show_plot: Whether to display the plot
            figure_size: Size of the figure
            days_back: Number of days back to analyze

        Returns:
            True if successful, False otherwise
        """
        logger.debug(f"Creating commit activity PNG chart: {title}")

        try:
            # Get commit data
            if repository_path and GIT_OPERATIONS_AVAILABLE:
                commits_data = get_commit_history(100, repository_path)
                commits = commits_data
            elif commits:
                pass
            else:
                # Generate sample data
                commits = self._generate_sample_commits(days_back)

            # Process commit dates
            commit_dates = []
            for commit in commits:
                try:
                    date_str = commit.get("date", "")
                    # Parse different date formats
                    if "T" in date_str:
                        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        date = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
                    commit_dates.append(date.date())
                except (ValueError, TypeError):
                    continue

            if not commit_dates:
                logger.warning("No valid commit dates found")
                return False

            # Create daily commit counts
            from collections import Counter

            commit_counts = Counter(commit_dates)

            # Create date range
            end_date = max(commit_dates)
            start_date = end_date - timedelta(days=days_back)
            date_range = [start_date + timedelta(days=i) for i in range(days_back + 1)]

            # Get counts for each date
            daily_counts = [commit_counts.get(date, 0) for date in date_range]

            # Create the plot
            fig, ax = plt.subplots(figsize=figure_size)

            ax.bar(date_range, daily_counts, color=self.colors["commit"], alpha=0.7)
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Commits")
            ax.set_title(title)

            # Format dates on x-axis
            import matplotlib.dates as mdates

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            ax.xaxis.set_major_locator(
                mdates.DayLocator(interval=max(1, days_back // 10))
            )
            plt.xticks(rotation=45)

            # Add statistics
            total_commits = sum(daily_counts)
            avg_commits = total_commits / days_back
            ax.text(
                0.02,
                0.95,
                f"Total: {total_commits} commits\nAvg: {avg_commits:.1f} commits/day",
                transform=ax.transAxes,
                va="top",
                bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
            )

            plt.tight_layout()

            if output_path:
                save_plot(fig, output_path)

            if show_plot:
                plt.show()
            else:
                plt.close(fig)

            logger.info(f"Commit activity PNG chart '{title}' generated successfully")
            return True

        except Exception as e:
            logger.error(
                f"Error creating commit activity PNG chart: {e}", exc_info=True
            )
            return False

    def _get_repo_data(self, repository_path: str, repo_data: dict[str, Any]) -> dict[str, Any]:
        """Get repository data from path or use provided data."""
        if repository_path and GIT_OPERATIONS_AVAILABLE:
            repo_status = get_status(repository_path)
            commit_history = get_commit_history(100, repository_path)
            current_branch = get_current_branch(repository_path)

            return {
                "status": repo_status,
                "commits": commit_history,
                "current_branch": current_branch,
                "total_commits": len(commit_history),
            }
        elif repo_data:
            return repo_data
        else:
            # Use sample data
            return {
                "status": {"clean": True, "modified": [], "untracked": []},
                "commits": self._generate_sample_commits(),
                "current_branch": "main",
                "total_commits": 50,
            }

    def _plot_repository_status(self, ax, repo_data: dict[str, Any]):
        """Plot repository status pie chart."""
        status = repo_data.get("status", {})
        status_data = {
            "Clean": 1 if status.get("clean", False) else 0,
            "Modified": len(status.get("modified", [])),
            "Untracked": len(status.get("untracked", [])),
        }

        if any(status_data.values()):
            ax.pie(
                status_data.values(),
                labels=status_data.keys(),
                autopct="%1.0f",
                colors=["#90EE90", "#FFD700", "#FF6347"],
            )
        ax.set_title("Repository Status")

    def _plot_commit_timeline(self, ax, commits: list[dict[str, Any]]):
        """Plot recent commits timeline."""
        if not commits:
            return

        dates = []
        for commit in commits[:20]:
            try:
                date_str = commit.get("date", "")
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                dates.append(date)
            except (ValueError, KeyError, AttributeError):
                continue

        if dates:
            ax.plot(dates, range(len(dates)), "o-", color=self.colors["commit"])
            ax.set_xlabel("Date")
            ax.set_ylabel("Commits")
            ax.set_title("Recent Commits Timeline")
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    def _plot_author_contributions(self, ax, commits: list[dict[str, Any]]):
        """Plot top contributors bar chart."""
        author_counts = {}
        for commit in commits:
            author = commit.get("author_name", "Unknown")
            author_counts[author] = author_counts.get(author, 0) + 1

        if author_counts:
            authors = list(author_counts.keys())[:5]  # Top 5 authors
            counts = [author_counts[author] for author in authors]
            ax.barh(authors, counts, color=self.colors["feature"])
            ax.set_title("Top Contributors")
            ax.set_xlabel("Commits")

    def _plot_branch_info(self, ax, repo_data: dict[str, Any]):
        """Plot branch information text."""
        current_branch = repo_data.get("current_branch", "main")
        branch_info = f"Current: {current_branch}\nTotal Commits: {repo_data.get('total_commits', 0)}"
        ax.text(
            0.5,
            0.5,
            branch_info,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            bbox={"boxstyle": "round", "facecolor": self.colors["main"], "alpha": 0.3},
        )
        ax.set_title("Branch Info")
        ax.axis("off")

    def _plot_commit_words(self, ax, commits: list[dict[str, Any]]):
        """Plot common commit words bar chart."""
        commit_words = {}
        for commit in commits:
            message = commit.get("message", "").lower()
            words = message.split()
            for word in words:
                if len(word) > 3:  # Only words longer than 3 characters
                    commit_words[word] = commit_words.get(word, 0) + 1

        if commit_words:
            top_words = sorted(commit_words.items(), key=lambda x: x[1], reverse=True)[:10]
            words, counts = zip(*top_words, strict=False)
            ax.barh(words, counts, color=self.colors["develop"])
            ax.set_title("Common Commit Words")
            ax.set_xlabel("Frequency")

    def _plot_activity_heatmap(self, ax, commits: list[dict[str, Any]]):
        """Plot weekly activity heatmap."""
        commit_dates = []
        for commit in commits:
            try:
                date_str = commit.get("date", "")
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                commit_dates.append(date)
            except (ValueError, KeyError, AttributeError):
                continue

        if not commit_dates:
            return

        # Group by week and day of week
        from collections import defaultdict

        weekly_activity = defaultdict(lambda: defaultdict(int))

        for date in commit_dates:
            week = date.strftime("%Y-W%U")
            day = date.weekday()
            weekly_activity[week][day] += 1

        # Convert to matrix
        weeks = sorted(weekly_activity.keys())[-8:]  # Last 8 weeks
        activity_matrix = []
        for week in weeks:
            week_data = [weekly_activity[week][day] for day in range(7)]
            activity_matrix.append(week_data)

        if activity_matrix:
            im = ax.imshow(activity_matrix, cmap="Greens", aspect="auto")
            ax.set_title("Weekly Commit Activity Heatmap")
            ax.set_xlabel("Day of Week")
            ax.set_ylabel("Week")
            ax.set_xticks(range(7))
            ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
            ax.set_yticks(range(len(weeks)))
            ax.set_yticklabels(weeks, fontsize=8)
            # Add colorbar
            plt.colorbar(im, ax=ax, label="Commits")

    def visualize_repository_summary_png(
        self,
        repository_path: str = None,
        repo_data: dict[str, Any] = None,
        title: str = "Repository Summary",
        output_path: str = None,
        show_plot: bool = False,
        figure_size: tuple[int, int] = (14, 10),
    ) -> bool:
        """
        Create a comprehensive PNG dashboard of repository statistics.

        Args:
            repository_path: Path to Git repository
            repo_data: Repository data dictionary
            title: Plot title
            output_path: File path to save PNG
            show_plot: Whether to display the plot
            figure_size: Size of the figure

        Returns:
            True if successful, False otherwise
        """
        logger.debug(f"Creating repository summary PNG dashboard: {title}")

        try:
            # Get repository data
            repo_data = self._get_repo_data(repository_path, repo_data)

            # Create subplot dashboard
            fig = plt.figure(figsize=figure_size)
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

            commits = repo_data.get("commits", [])

            # Create all subplots using helper methods
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
                f"Repository summary PNG dashboard '{title}' generated successfully"
            )
            return True

        except Exception as e:
            logger.error(
                f"Error creating repository summary PNG dashboard: {e}", exc_info=True
            )
            return False

    def create_comprehensive_git_report(
        self,
        repository_path: str,
        output_dir: str,
        report_name: str = "git_analysis_report",
    ) -> dict[str, bool]:
        """
        Create a comprehensive Git analysis report with both PNG and Mermaid outputs.

        Args:
            repository_path: Path to Git repository
            output_dir: Directory to save all outputs
            report_name: Base name for report files

        Returns:
            Dictionary with success status for each visualization type
        """
        logger.info(f"Creating comprehensive Git report for {repository_path}")

        if not GIT_OPERATIONS_AVAILABLE:
            logger.error("Git operations module not available")
            return {}

        if not check_git_availability():
            logger.error("Git is not available on this system")
            return {}

        if not is_git_repository(repository_path):
            logger.error(f"Path {repository_path} is not a Git repository")
            return {}

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        results = {}

        # 1. Git tree visualizations
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

        # 2. Commit activity analysis
        results["commit_activity"] = self.visualize_commit_activity_png(
            repository_path=repository_path,
            title=f"Commit Activity - {os.path.basename(repository_path)}",
            output_path=os.path.join(output_dir, f"{report_name}_commit_activity.png"),
        )

        # 3. Repository summary dashboard
        results["repo_summary"] = self.visualize_repository_summary_png(
            repository_path=repository_path,
            title=f"Repository Summary - {os.path.basename(repository_path)}",
            output_path=os.path.join(
                output_dir, f"{report_name}_summary_dashboard.png"
            ),
        )

        # 4. Git workflow diagram (Mermaid)
        workflow_content = self.mermaid_generator.create_git_workflow_diagram(
            title=f"Git Workflow - {os.path.basename(repository_path)}",
            output_path=os.path.join(output_dir, f"{report_name}_workflow.mmd"),
        )
        results["workflow_mermaid"] = bool(workflow_content)

        # 5. Repository structure diagram (Mermaid)
        try:
            # Get basic repository structure
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
            logger.error(f"Error creating structure diagram: {e}")
            results["structure_mermaid"] = False

        # Create summary report
        self._create_report_summary(output_dir, report_name, results, repository_path)

        success_count = sum(results.values())
        total_count = len(results)
        logger.info(
            f"Git report creation completed: {success_count}/{total_count} visualizations successful"
        )

        return results

    def _get_branch_color(self, branch_name: str) -> str:
        """Get color for branch based on name."""
        branch_lower = branch_name.lower()
        if "main" in branch_lower or "master" in branch_lower:
            return self.colors["main"]
        elif "develop" in branch_lower:
            return self.colors["develop"]
        elif "feature" in branch_lower:
            return self.colors["feature"]
        elif "hotfix" in branch_lower:
            return self.colors["hotfix"]
        elif "release" in branch_lower:
            return self.colors["release"]
        else:
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
                    "message": f"Sample commit {i+1}",
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
            # Get top-level directories and files
            for item in path.iterdir():
                if item.name.startswith("."):
                    continue

                if item.is_dir():
                    # Get subdirectory structure (limited depth)
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
                        pass
                    structure[item.name] = substructure
                else:
                    structure[item.name] = "file"

        except Exception as e:
            logger.error(f"Error getting repository structure: {e}")

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

        logger.info(f"Report summary saved to {summary_path}")


# Convenience functions for easy import
def visualize_git_repository(
    repository_path: str,
    output_dir: str = "./git_analysis",
    report_name: str = "git_report",
) -> dict[str, bool]:
    """
    Create comprehensive Git repository visualizations.

    Args:
        repository_path: Path to Git repository
        output_dir: Directory to save outputs
        report_name: Base name for output files

    Returns:
        Dictionary with success status for each visualization
    """
    visualizer = GitVisualizer()
    return visualizer.create_comprehensive_git_report(
        repository_path, output_dir, report_name
    )


def create_git_tree_png(
    repository_path: str = None,
    branches: list[dict[str, Any]] = None,
    commits: list[dict[str, Any]] = None,
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
    repository_path: str = None,
    branches: list[dict[str, Any]] = None,
    commits: list[dict[str, Any]] = None,
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
    # Test the Git visualizer
    import sys

    output_dir = Path(__file__).parent.parent / "output" / "git_visualization_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Testing Git Visualization ---")

    visualizer = GitVisualizer()

    # Test with sample data if no git repo provided
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = None

    if repo_path and os.path.exists(repo_path):
        logger.info(f"Creating comprehensive Git report for: {repo_path}")
        results = visualizer.create_comprehensive_git_report(
            repository_path=repo_path,
            output_dir=str(output_dir),
            report_name="test_git_report",
        )
        logger.info(f"Results: {results}")
    else:
        logger.info("Testing with sample data")

        # Test PNG visualization with sample data
        success = visualizer.visualize_git_tree_png(
            title="Sample Git Tree", output_path=str(output_dir / "sample_git_tree.png")
        )
        logger.info(f"Sample Git tree PNG: {'Success' if success else 'Failed'}")

        # Test Mermaid visualization
        mermaid_content = visualizer.visualize_git_tree_mermaid(
            title="Sample Git Diagram",
            output_path=str(output_dir / "sample_git_tree.mmd"),
        )
        logger.info(
            f"Sample Git tree Mermaid: {'Success' if mermaid_content else 'Failed'}"
        )

        # Test commit activity
        success = visualizer.visualize_commit_activity_png(
            title="Sample Commit Activity",
            output_path=str(output_dir / "sample_commit_activity.png"),
        )
        logger.info(f"Sample commit activity: {'Success' if success else 'Failed'}")

        # Test repository summary
        success = visualizer.visualize_repository_summary_png(
            title="Sample Repository Summary",
            output_path=str(output_dir / "sample_repo_summary.png"),
        )
        logger.info(f"Sample repository summary: {'Success' if success else 'Failed'}")

    logger.info(f"Git visualization examples generated in {output_dir}")

    # Basic logging setup if running standalone
    import logging

    if not get_codomyrmex_logger("").hasHandlers():
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of git_visualizer.py."
        )
