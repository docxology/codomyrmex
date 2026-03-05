"""Git Workflow — demonstrates codomyrmex git_operations and git_analysis.

Integrates with:
- codomyrmex.git_operations for repo inspection, branching, and history
- codomyrmex.git_analysis for commit history analysis and contributor stats
- codomyrmex.logging_monitoring for structured logging

Example:
    >>> workflow = GitWorkflow()
    >>> info = workflow.inspect_repo("/path/to/repo")
    >>> print(info["is_git_repo"])
    >>> history = workflow.analyze_history("/path/to/repo")
    >>> print(history["commit_count"])
"""

from pathlib import Path
from typing import Any

from codomyrmex.git_analysis import GitHistoryAnalyzer
from codomyrmex.git_operations import (
    check_git_availability,
    get_current_branch,
    get_diff,
    get_status,
    is_git_repository,
    list_branches,
)
from codomyrmex.logging_monitoring import get_logger

HAS_GIT_MODULES = True  # Exported for integration tests

logger = get_logger(__name__)


class GitWorkflow:
    """Demonstrates git_operations + git_analysis integration.

    Provides a high-level interface for repository inspection and
    history analysis, combining codomyrmex.git_operations (live repo
    state) with codomyrmex.git_analysis (historical commit patterns).

    Example:
        >>> wf = GitWorkflow()
        >>> info = wf.inspect_repo(".")
        >>> print(info["current_branch"])
    """

    def __init__(self) -> None:
        """Initialize GitWorkflow."""
        self.git_available = check_git_availability()
        logger.info(f"GitWorkflow initialized, git available: {self.git_available}")

    def inspect_repo(self, path: str | Path) -> dict[str, Any]:
        """Inspect current repository state.

        Returns status, branch, diff summary, and branch listing.

        Args:
            path: Path to the git repository root.

        Returns:
            Dictionary with repo inspection results:
            - is_git_repo: bool
            - current_branch: str | None
            - status: dict from get_status()
            - branches: list of branch names
            - diff_summary: brief diff info
            - git_available: bool
        """
        path_str = str(path)
        logger.info(f"Inspecting repo at: {path_str}")

        result: dict[str, Any] = {
            "path": path_str,
            "git_available": self.git_available,
            "is_git_repo": False,
            "current_branch": None,
            "status": {},
            "branches": [],
            "diff_summary": "",
        }

        if not self.git_available:
            logger.warning("Git not available on this system")
            return result

        try:
            result["is_git_repo"] = is_git_repository(path_str)
        except Exception as e:
            logger.warning(f"is_git_repository failed: {e}")
            return result

        if not result["is_git_repo"]:
            return result

        try:
            result["current_branch"] = get_current_branch(path_str)
        except Exception as e:
            logger.warning(f"get_current_branch failed: {e}")

        try:
            status = get_status(path_str)
            result["status"] = (
                status if isinstance(status, dict) else {"raw": str(status)}
            )
        except Exception as e:
            logger.warning(f"get_status failed: {e}")

        try:
            branches = list_branches(path_str)
            result["branches"] = branches if isinstance(branches, list) else []
        except Exception as e:
            logger.warning(f"list_branches failed: {e}")

        try:
            diff = get_diff(path_str)
            result["diff_summary"] = str(diff)[:200] if diff else ""
        except Exception as e:
            logger.warning(f"get_diff failed: {e}")

        return result

    def analyze_history(
        self, path: str | Path, max_commits: int = 20
    ) -> dict[str, Any]:
        """Analyze commit history using git_analysis.

        Uses GitHistoryAnalyzer to extract commit frequency, contributor
        stats, and high-churn files from repository history.

        Args:
            path: Path to the git repository root.
            max_commits: Maximum number of commits to analyze.

        Returns:
            Dictionary with history analysis:
            - commit_count: int
            - contributors: list of contributor info dicts
            - churn_files: list of high-churn files
            - analyzer_available: bool
        """
        path_str = str(path)
        logger.info(f"Analyzing git history at: {path_str}")

        result: dict[str, Any] = {
            "path": path_str,
            "analyzer_available": False,
            "commit_count": 0,
            "contributors": [],
            "churn_files": [],
        }

        if not self.git_available:
            return result

        try:
            analyzer = GitHistoryAnalyzer(repo_path=path_str)
            result["analyzer_available"] = True

            commits = analyzer.get_commit_history(max_count=max_commits)
            result["commit_count"] = len(commits) if commits else 0

            try:
                contributors = analyzer.get_contributor_stats()
                result["contributors"] = (
                    contributors if isinstance(contributors, list) else []
                )
            except Exception as e:
                logger.warning(f"get_contributor_stats failed: {e}")

            try:
                churn = analyzer.get_high_churn_files(top_n=10)
                result["churn_files"] = churn if isinstance(churn, list) else []
            except Exception as e:
                logger.warning(f"get_high_churn_files failed: {e}")

        except Exception as e:
            logger.warning(f"GitHistoryAnalyzer failed: {e}")

        return result

    @staticmethod
    def module_info() -> dict[str, Any]:
        """Return information about the git modules being demonstrated.

        Returns:
            Dictionary describing the integrated modules and their APIs.
        """
        return {
            "git_operations": {
                "module": "codomyrmex.git_operations",
                "key_functions": [
                    "is_git_repository",
                    "get_status",
                    "get_diff",
                    "get_current_branch",
                    "list_branches",
                    "commit_changes",
                    "create_branch",
                    "switch_branch",
                ],
            },
            "git_analysis": {
                "module": "codomyrmex.git_analysis",
                "key_classes": ["GitHistoryAnalyzer"],
                "capabilities": [
                    "commit_history",
                    "contributor_stats",
                    "churn_detection",
                ],
            },
        }
