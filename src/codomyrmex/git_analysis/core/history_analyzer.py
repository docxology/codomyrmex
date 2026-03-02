"""GitPython-based repository history and contributor analysis.

Complements git_operations (operational git commands — clone/commit/push/pull)
with analytical capabilities: commit frequency, contributor stats, code churn,
and branch topology — all computed directly from the git object model.

GitPython is a core dependency of codomyrmex (no extra install required).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import git  # GitPython (core dep — see pyproject.toml)


class GitHistoryAnalyzer:
    """Analyzes git history for a repository.

    All methods operate on the git object model directly (no subprocess calls),
    making them fast and portable.

    Example:
        >>> analyzer = GitHistoryAnalyzer(".")
        >>> stats = analyzer.get_contributor_stats()
        >>> print(stats[0]["author"], stats[0]["commits"])
    """

    def __init__(self, repo_path: str) -> None:
        """Initialize this instance."""
        self._path = str(Path(repo_path).resolve())
        self._repo = git.Repo(self._path, search_parent_directories=True)

    def get_commit_history(
        self, max_count: int = 50, branch: str | None = None
    ) -> list[dict[str, Any]]:
        """Return commit metadata list sorted newest-first.

        Each entry contains: sha, author, email, date (ISO-8601), message
        (first line), insertions, deletions, files_changed.

        Args:
            max_count: Maximum number of commits to return.
            branch: Branch name to walk. Defaults to the active branch.
        """
        ref = branch or self._repo.active_branch.name
        commits = []
        for commit in self._repo.iter_commits(ref, max_count=max_count):
            stats = commit.stats.total
            commits.append({
                "sha": commit.hexsha[:12],
                "author": commit.author.name,
                "email": commit.author.email,
                "date": commit.authored_datetime.isoformat(),
                "message": commit.message.strip().split("\n")[0],
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
                "files_changed": stats["files"],
            })
        return commits

    def get_contributor_stats(self) -> list[dict[str, Any]]:
        """Return per-author aggregate statistics across ALL commits.

        Returns entries sorted by commit count descending. Each entry:
        author, commits, insertions, deletions, first_commit, last_commit.
        """
        stats: dict[str, dict[str, Any]] = defaultdict(lambda: {
            "commits": 0,
            "insertions": 0,
            "deletions": 0,
            "first_commit": None,
            "last_commit": None,
        })
        for commit in self._repo.iter_commits():
            name = commit.author.name
            s = stats[name]
            s["commits"] += 1
            total = commit.stats.total
            s["insertions"] += total["insertions"]
            s["deletions"] += total["deletions"]
            date = commit.authored_datetime.isoformat()
            if s["first_commit"] is None or date < s["first_commit"]:
                s["first_commit"] = date
            if s["last_commit"] is None or date > s["last_commit"]:
                s["last_commit"] = date
        return [
            {"author": name, **data}
            for name, data in sorted(
                stats.items(), key=lambda x: x[1]["commits"], reverse=True
            )
        ]

    def get_code_churn(self, top_n: int = 20) -> list[dict[str, Any]]:
        """Return the top N most-frequently-changed files (churn analysis).

        Churn is measured as the number of commits that touched each file.
        High-churn files are candidates for refactoring or test coverage focus.

        Args:
            top_n: Number of top-churned files to return.
        """
        file_changes: dict[str, int] = defaultdict(int)
        for commit in self._repo.iter_commits():
            for path in commit.stats.files:
                file_changes[path] += 1
        sorted_files = sorted(
            file_changes.items(), key=lambda x: x[1], reverse=True
        )
        return [
            {"file": path, "change_count": count}
            for path, count in sorted_files[:top_n]
        ]

    def get_branch_topology(self) -> dict[str, Any]:
        """Return branch names, their tip commits, and active branch.

        Returns:
            Dict with keys: active_branch (str), branches (list), branch_count (int).
            Each branch entry: name, tip_sha, tip_message, tip_date.
        """
        branches = []
        for branch in self._repo.branches:
            branches.append({
                "name": branch.name,
                "tip_sha": branch.commit.hexsha[:12],
                "tip_message": branch.commit.message.strip().split("\n")[0],
                "tip_date": branch.commit.authored_datetime.isoformat(),
            })
        return {
            "active_branch": self._repo.active_branch.name,
            "branches": branches,
            "branch_count": len(branches),
        }

    def get_commit_frequency(self, by: str = "week") -> dict[str, int]:
        """Return commit counts bucketed by time period.

        Args:
            by: Bucket size — one of "day" (YYYY-MM-DD), "week" (YYYY-WNN),
                or "month" (YYYY-MM). Defaults to "week".

        Returns:
            Dict mapping period key → commit count, sorted chronologically.
        """
        buckets: dict[str, int] = defaultdict(int)
        for commit in self._repo.iter_commits():
            dt: datetime = commit.authored_datetime
            if by == "day":
                key = dt.strftime("%Y-%m-%d")
            elif by == "week":
                iso = dt.isocalendar()
                key = f"{iso.year}-W{iso.week:02d}"
            else:  # month
                key = dt.strftime("%Y-%m")
            buckets[key] += 1
        return dict(sorted(buckets.items()))

    def get_commit_history_filtered(
        self,
        max_count: int = 50,
        since: str | None = None,
        until: str | None = None,
        author: str | None = None,
        branch: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return commit history with optional date and author filters.

        Args:
            max_count: Maximum commits to return. Capped at 10000.
            since: ISO-8601 date string — only commits after this date.
            until: ISO-8601 date string — only commits before this date.
            author: Author name substring filter (case-insensitive).
            branch: Branch to walk. Defaults to active branch.
        """
        max_count = min(max(1, max_count), 10000)
        ref = branch or self._repo.active_branch.name
        kwargs: dict[str, Any] = {"max_count": max_count}
        if since:
            kwargs["after"] = since
        if until:
            kwargs["before"] = until
        commits = []
        author_lower = author.lower() if author else None
        for commit in self._repo.iter_commits(ref, **kwargs):
            if author_lower and author_lower not in commit.author.name.lower():
                continue
            stats = commit.stats.total
            commits.append({
                "sha": commit.hexsha[:12],
                "author": commit.author.name,
                "email": commit.author.email,
                "date": commit.authored_datetime.isoformat(),
                "message": commit.message.strip().split("\n")[0],
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
                "files_changed": stats["files"],
            })
        return commits

    def get_file_history(
        self,
        file_path: str,
        max_count: int = 50,
    ) -> list[dict[str, Any]]:
        """Return commit history touching a specific file.

        Args:
            file_path: Relative path to file within the repository.
            max_count: Maximum commits to return.
        """
        max_count = min(max(1, max_count), 10000)
        commits = []
        for commit in self._repo.iter_commits(paths=file_path, max_count=max_count):
            stats = commit.stats.total
            commits.append({
                "sha": commit.hexsha[:12],
                "author": commit.author.name,
                "email": commit.author.email,
                "date": commit.authored_datetime.isoformat(),
                "message": commit.message.strip().split("\n")[0],
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
                "files_changed": stats["files"],
            })
        return commits

    def get_churn_by_directory(self, top_n: int = 10) -> list[dict[str, Any]]:
        """Return commit frequency aggregated by top-level directory.

        Useful for identifying which modules have the most activity.

        Returns:
            List sorted by change_count desc:
            [{"directory": str, "change_count": int, "files": int}]
        """
        top_n = min(max(1, top_n), 10000)
        dir_changes: dict[str, int] = defaultdict(int)
        dir_files: dict[str, set] = defaultdict(set)
        for commit in self._repo.iter_commits():
            for path in commit.stats.files:
                parts = Path(path).parts
                top_dir = parts[0] if len(parts) > 1 else "."
                dir_changes[top_dir] += 1
                dir_files[top_dir].add(path)
        sorted_dirs = sorted(dir_changes.items(), key=lambda x: x[1], reverse=True)
        return [
            {
                "directory": d,
                "change_count": count,
                "files": len(dir_files[d]),
            }
            for d, count in sorted_dirs[:top_n]
        ]

    def get_hotspot_analysis(self, top_n: int = 20) -> list[dict[str, Any]]:
        """Identify high-risk files combining churn frequency with recency.

        Hotspot score = change_count / (1 + days_since_last_change/30).
        Files changed recently score higher than equally-churned stale files.

        Returns:
            List sorted by hotspot_score desc:
            [{"file": str, "change_count": int, "last_changed": str, "hotspot_score": float}]
        """
        top_n = min(max(1, top_n), 10000)
        file_count: dict[str, int] = defaultdict(int)
        file_last: dict[str, datetime] = {}
        now = datetime.now(tz=None)
        for commit in self._repo.iter_commits():
            commit_dt = commit.authored_datetime.replace(tzinfo=None)
            for path in commit.stats.files:
                file_count[path] += 1
                if path not in file_last or commit_dt > file_last[path]:
                    file_last[path] = commit_dt
        results = []
        for path, count in file_count.items():
            last_dt = file_last.get(path, now)
            days_ago = max(0, (now - last_dt).days)
            score = count / (1.0 + days_ago / 30.0)
            results.append({
                "file": path,
                "change_count": count,
                "last_changed": last_dt.isoformat(),
                "hotspot_score": round(score, 4),
            })
        results.sort(key=lambda x: x["hotspot_score"], reverse=True)
        return results[:top_n]
