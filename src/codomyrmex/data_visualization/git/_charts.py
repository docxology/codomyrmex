"""Mixin for Git tree, branch, and commit activity chart visualizations."""

from datetime import datetime, timedelta
from typing import Any

import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from codomyrmex.data_visualization.utils import apply_common_aesthetics, save_plot
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Conditional import of git_operations
try:
    from codomyrmex.git_operations.core.git import (
        get_commit_history,
        get_current_branch,
        is_git_repository,
    )

    _GIT_OPS = True
except ImportError:
    _GIT_OPS = False


class GitChartsMixin:
    """Tree/branch PNG, Mermaid tree, and commit-activity chart generation.

    Requires ``mermaid_generator``, ``colors``, ``_get_branch_color``,
    and ``_generate_sample_commits`` from the host class.
    """

    def visualize_git_tree_png(
        self,
        repository_path: str | None = None,
        branches: list[dict[str, Any]] | None = None,
        commits: list[dict[str, Any]] | None = None,
        title: str = "Git Tree Visualization",
        output_path: str | None = None,
        show_plot: bool = False,
        figure_size: tuple[int, int] = (12, 8),
        max_commits: int = 20,
    ) -> bool:
        """Create a PNG visualization of Git tree/branches using matplotlib."""
        logger.debug("Creating Git tree PNG visualization: %s", title)

        try:
            if repository_path and _GIT_OPS:
                if not is_git_repository(repository_path):
                    logger.error("Path %s is not a Git repository", repository_path)
                    return False

                commits_data = get_commit_history(max_commits, repository_path)
                current_branch = get_current_branch(repository_path)

                commits = [
                    {
                        "hash": commit["hash"][:8],
                        "message": commit["message"],
                        "author_name": commit["author_name"],
                        "date": commit["date"],
                        "branch": current_branch or "main",
                    }
                    for commit in commits_data
                ]

                branches = [{"name": current_branch or "main", "commits": len(commits)}]

            elif branches and commits:
                pass
            else:
                branches = [
                    {"name": "main", "commits": 8},
                    {"name": "develop", "commits": 5},
                    {"name": "feature/auth", "commits": 3},
                ]
                commits = self._generate_sample_commits()

            fig, ax = plt.subplots(figsize=figure_size)

            branch_y_positions = {}
            for i, branch in enumerate(branches):
                branch_name = branch["name"]
                y_pos = len(branches) - i - 1
                branch_y_positions[branch_name] = y_pos

                color = self._get_branch_color(branch_name)
                ax.axhline(y=y_pos, color=color, linewidth=2, alpha=0.3)
                ax.text(
                    -0.5,
                    y_pos,
                    branch_name,
                    fontweight="bold",
                    color=color,
                    va="center",
                    ha="right",
                )

            for i, commit in enumerate(commits[:max_commits]):
                branch = commit.get("branch", "main")
                y_pos = branch_y_positions.get(branch, 0)
                x_pos = i

                color = self._get_branch_color(branch)
                ax.scatter(x_pos, y_pos, color=color, s=100, zorder=3)
                ax.text(
                    x_pos,
                    y_pos - 0.15,
                    commit.get("hash", ""),
                    fontsize=8,
                    ha="center",
                    va="top",
                )
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

            for i in range(1, min(len(commits), max_commits)):
                prev_commit = commits[i - 1]
                curr_commit = commits[i]
                prev_branch = prev_commit.get("branch", "main")
                curr_branch = curr_commit.get("branch", "main")

                prev_y = branch_y_positions.get(prev_branch, 0)
                curr_y = branch_y_positions.get(curr_branch, 0)
                ax.plot([i - 1, i], [prev_y, curr_y], "k-", alpha=0.5, zorder=1)

            apply_common_aesthetics(ax, title, "Commits (timeline →)", "Branches")
            ax.set_xlim(-1, max(max_commits - 1, 5))
            ax.set_ylim(-0.5, len(branches) - 0.5)
            ax.set_yticks(range(len(branches)))
            ax.set_yticklabels([b["name"] for b in reversed(branches)])

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

            logger.info("Git tree PNG visualization '%s' generated successfully", title)
            return True

        except Exception as e:
            logger.error(
                "Error creating Git tree PNG visualization: %s", e, exc_info=True
            )
            return False

    def visualize_git_tree_mermaid(
        self,
        repository_path: str | None = None,
        branches: list[dict[str, Any]] | None = None,
        commits: list[dict[str, Any]] | None = None,
        title: str = "Git Tree Diagram",
        output_path: str | None = None,
    ) -> str:
        """Create a Mermaid Git tree/branch diagram."""
        logger.debug("Creating Git tree Mermaid diagram: %s", title)

        try:
            if repository_path and _GIT_OPS:
                if not is_git_repository(repository_path):
                    logger.error("Path %s is not a Git repository", repository_path)
                    return ""

                commits_data = get_commit_history(20, repository_path)
                current_branch = get_current_branch(repository_path)

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

            mermaid_content = self.mermaid_generator.create_git_branch_diagram(
                branches=branches, commits=commits, title=title, output_path=output_path
            )

            logger.info("Git tree Mermaid diagram '%s' generated successfully", title)
            return mermaid_content

        except Exception as e:
            logger.error(
                "Error creating Git tree Mermaid diagram: %s", e, exc_info=True
            )
            return ""

    def visualize_commit_activity_png(
        self,
        repository_path: str | None = None,
        commits: list[dict[str, Any]] | None = None,
        title: str = "Commit Activity",
        output_path: str | None = None,
        show_plot: bool = False,
        figure_size: tuple[int, int] = (12, 6),
        days_back: int = 30,
    ) -> bool:
        """Create a PNG chart showing commit activity over time."""
        logger.debug("Creating commit activity PNG chart: %s", title)

        try:
            if repository_path and _GIT_OPS:
                commits_data = get_commit_history(100, repository_path)
                commits = commits_data
            elif commits:
                pass
            else:
                commits = self._generate_sample_commits(days_back)

            commit_dates = []
            for commit in commits:
                try:
                    date_str = commit.get("date", "")
                    if "T" in date_str:
                        date = datetime.fromisoformat(date_str)
                    else:
                        date = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
                    commit_dates.append(date.date())
                except (ValueError, TypeError):
                    continue

            if not commit_dates:
                logger.warning("No valid commit dates found")
                return False

            from collections import Counter

            commit_counts = Counter(commit_dates)

            end_date = max(commit_dates)
            start_date = end_date - timedelta(days=days_back)
            date_range = [start_date + timedelta(days=i) for i in range(days_back + 1)]
            daily_counts = [commit_counts.get(date, 0) for date in date_range]

            fig, ax = plt.subplots(figsize=figure_size)

            ax.bar(date_range, daily_counts, color=self.colors["commit"], alpha=0.7)
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of Commits")
            ax.set_title(title)

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
            ax.xaxis.set_major_locator(
                mdates.DayLocator(interval=max(1, days_back // 10))
            )
            plt.xticks(rotation=45)

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

            logger.info("Commit activity PNG chart '%s' generated successfully", title)
            return True

        except Exception as e:
            logger.error(
                "Error creating commit activity PNG chart: %s", e, exc_info=True
            )
            return False
