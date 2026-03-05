"""Integration tests for git_workflow.py — git_operations + git_analysis integration."""

import sys
from pathlib import Path

import pytest

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

# Path to the codomyrmex repo root (a real git repo for tests)
REPO_ROOT = str(Path(__file__).parent.parent.parent.parent)


class TestGitOperationsImports:
    """Verify codomyrmex.git_operations imports used in git_workflow."""

    def test_import_is_git_repository(self):
        """is_git_repository is importable and callable."""
        from codomyrmex.git_operations import is_git_repository

        assert callable(is_git_repository)

    def test_import_get_status(self):
        """get_status is importable and callable."""
        from codomyrmex.git_operations import get_status

        assert callable(get_status)

    def test_import_get_current_branch(self):
        """get_current_branch is importable and callable."""
        from codomyrmex.git_operations import get_current_branch

        assert callable(get_current_branch)

    def test_import_list_branches(self):
        """list_branches is importable and callable."""
        from codomyrmex.git_operations import list_branches

        assert callable(list_branches)

    def test_import_check_git_availability(self):
        """check_git_availability is importable and callable."""
        from codomyrmex.git_operations import check_git_availability

        assert callable(check_git_availability)


class TestGitAnalysisImports:
    """Verify codomyrmex.git_analysis imports used in git_workflow."""

    def test_import_git_history_analyzer(self):
        """GitHistoryAnalyzer is importable."""
        from codomyrmex.git_analysis import GitHistoryAnalyzer

        assert GitHistoryAnalyzer is not None

    def test_git_history_analyzer_has_get_commit_history(self):
        """GitHistoryAnalyzer has get_commit_history method."""
        from codomyrmex.git_analysis import GitHistoryAnalyzer

        assert callable(getattr(GitHistoryAnalyzer, "get_commit_history", None))

    def test_git_history_analyzer_has_contributor_stats(self):
        """GitHistoryAnalyzer has get_contributor_stats method."""
        from codomyrmex.git_analysis import GitHistoryAnalyzer

        assert callable(getattr(GitHistoryAnalyzer, "get_contributor_stats", None))


class TestGitWorkflowModule:
    """Functional tests for GitWorkflow class."""

    def test_has_git_modules_flag(self):
        """HAS_GIT_MODULES flag is True in git_workflow.py."""
        from src.git_workflow import HAS_GIT_MODULES

        assert HAS_GIT_MODULES is True

    def test_git_workflow_instantiation(self):
        """GitWorkflow can be instantiated without errors."""
        from src.git_workflow import GitWorkflow

        wf = GitWorkflow()
        assert wf is not None
        assert isinstance(wf.git_available, bool)

    def test_module_info_returns_dict(self):
        """GitWorkflow.module_info() returns expected dict structure."""
        from src.git_workflow import GitWorkflow

        info = GitWorkflow.module_info()
        assert isinstance(info, dict)
        assert "git_operations" in info
        assert "git_analysis" in info
        assert "key_functions" in info["git_operations"]

    def test_inspect_repo_returns_dict(self):
        """inspect_repo() returns a dict with expected keys."""
        from src.git_workflow import GitWorkflow

        wf = GitWorkflow()
        result = wf.inspect_repo(REPO_ROOT)
        assert isinstance(result, dict)
        assert "is_git_repo" in result
        assert "git_available" in result

    def test_inspect_repo_on_valid_git_repo(self):
        """inspect_repo() detects the codomyrmex repo correctly."""
        from src.git_workflow import GitWorkflow

        from codomyrmex.git_operations import check_git_availability

        if not check_git_availability():
            pytest.skip("Git not installed on this system")

        wf = GitWorkflow()
        result = wf.inspect_repo(REPO_ROOT)
        assert result["is_git_repo"] is True
        assert result["current_branch"] is not None

    def test_analyze_history_returns_dict(self):
        """analyze_history() returns a dict with expected keys."""
        from src.git_workflow import GitWorkflow

        wf = GitWorkflow()
        result = wf.analyze_history(REPO_ROOT)
        assert isinstance(result, dict)
        assert "commit_count" in result
        assert "contributors" in result
        assert "analyzer_available" in result
