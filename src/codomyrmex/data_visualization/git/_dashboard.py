"""Mixin for Git repository summary dashboard subplot helpers."""

from collections import defaultdict
from datetime import datetime
from typing import Any

import matplotlib.pyplot as plt

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Conditional import of git_operations
try:
    from codomyrmex.git_operations.core.git import (
        get_commit_history,
        get_current_branch,
        get_status,
    )

    _GIT_OPS = True
except ImportError:
    _GIT_OPS = False


class GitDashboardMixin:
    """Dashboard subplot helpers for repository summary visualization.

    Requires ``colors`` and ``_generate_sample_commits`` from the host class.
    """

    def _get_repo_data(
        self, repository_path: str, repo_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Get repository data from path or use provided data."""
        if repository_path and _GIT_OPS:
            repo_status = get_status(repository_path)
            commit_history = get_commit_history(100, repository_path)
            current_branch = get_current_branch(repository_path)

            return {
                "status": repo_status,
                "commits": commit_history,
                "current_branch": current_branch,
                "total_commits": len(commit_history),
            }
        if repo_data:
            return repo_data
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
                date = datetime.fromisoformat(date_str)
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
        author_counts: dict[str, int] = {}
        for commit in commits:
            author = commit.get("author_name", "Unknown")
            author_counts[author] = author_counts.get(author, 0) + 1

        if author_counts:
            authors = list(author_counts.keys())[:5]
            counts = [author_counts[author] for author in authors]
            ax.barh(authors, counts, color=self.colors["feature"])
            ax.set_title("Top Contributors")
            ax.set_xlabel("Commits")

    def _plot_branch_info(self, ax, repo_data: dict[str, Any]):
        """Plot branch information text."""
        current_branch = repo_data.get("current_branch", "main")
        branch_info = (
            f"Current: {current_branch}\n"
            f"Total Commits: {repo_data.get('total_commits', 0)}"
        )
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
        commit_words: dict[str, int] = {}
        for commit in commits:
            message = commit.get("message", "").lower()
            words = message.split()
            for word in words:
                if len(word) > 3:
                    commit_words[word] = commit_words.get(word, 0) + 1

        if commit_words:
            top_words = sorted(commit_words.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]
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
                date = datetime.fromisoformat(date_str)
                commit_dates.append(date)
            except (ValueError, KeyError, AttributeError):
                continue

        if not commit_dates:
            return

        weekly_activity: dict[str, dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for date in commit_dates:
            week = date.strftime("%Y-W%U")
            day = date.weekday()
            weekly_activity[week][day] += 1

        weeks = sorted(weekly_activity.keys())[-8:]
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
            plt.colorbar(im, ax=ax, label="Commits")
