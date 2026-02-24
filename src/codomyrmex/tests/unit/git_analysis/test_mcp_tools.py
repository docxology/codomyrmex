"""Unit tests for git_analysis MCP tool wrappers.

Tests all 12 tools for correct return shape and status handling.
GitPython-backed tools (5) are tested against the actual codomyrmex repo.
GitNexus-backed tools (7) verify graceful degradation when unavailable.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.git_analysis import mcp_tools

PROJECT_ROOT = str(Path(__file__).parents[5])


# ── GitPython-backed MCP tools ──────────────────────────────────────────────


@pytest.mark.unit
def test_commit_history_ok() -> None:
    """git_analysis_commit_history returns status:ok with commits list."""
    result = mcp_tools.git_analysis_commit_history(
        repo_path=PROJECT_ROOT, max_count=5
    )
    assert result["status"] == "ok"
    assert "commits" in result
    assert "count" in result
    assert isinstance(result["commits"], list)
    assert result["count"] == len(result["commits"])


@pytest.mark.unit
def test_commit_history_required_keys() -> None:
    """Each commit in history has the expected metadata keys."""
    result = mcp_tools.git_analysis_commit_history(
        repo_path=PROJECT_ROOT, max_count=3
    )
    assert result["status"] == "ok"
    for commit in result["commits"]:
        assert "sha" in commit
        assert "author" in commit
        assert "date" in commit
        assert "message" in commit


@pytest.mark.unit
def test_contributor_stats_ok() -> None:
    """git_analysis_contributor_stats returns status:ok with contributors list."""
    result = mcp_tools.git_analysis_contributor_stats(repo_path=PROJECT_ROOT)
    assert result["status"] == "ok"
    assert "contributors" in result
    assert "count" in result
    assert result["count"] > 0


@pytest.mark.unit
def test_contributor_stats_fields() -> None:
    """Each contributor entry has required fields."""
    result = mcp_tools.git_analysis_contributor_stats(repo_path=PROJECT_ROOT)
    assert result["status"] == "ok"
    for contributor in result["contributors"]:
        assert "author" in contributor
        assert "commits" in contributor
        assert "insertions" in contributor
        assert "deletions" in contributor


@pytest.mark.unit
def test_code_churn_ok() -> None:
    """git_analysis_code_churn returns status:ok with files list."""
    result = mcp_tools.git_analysis_code_churn(repo_path=PROJECT_ROOT, top_n=10)
    assert result["status"] == "ok"
    assert "files" in result
    assert "count" in result
    assert len(result["files"]) <= 10


@pytest.mark.unit
def test_code_churn_fields() -> None:
    """Each churn entry has 'file' and 'change_count' fields."""
    result = mcp_tools.git_analysis_code_churn(repo_path=PROJECT_ROOT, top_n=5)
    assert result["status"] == "ok"
    for entry in result["files"]:
        assert "file" in entry
        assert "change_count" in entry


@pytest.mark.unit
def test_branch_topology_ok() -> None:
    """git_analysis_branch_topology returns status:ok with branch data."""
    result = mcp_tools.git_analysis_branch_topology(repo_path=PROJECT_ROOT)
    assert result["status"] == "ok"
    assert "active_branch" in result
    assert "branches" in result
    assert "branch_count" in result


@pytest.mark.unit
def test_commit_frequency_ok() -> None:
    """git_analysis_commit_frequency returns status:ok with frequency dict."""
    result = mcp_tools.git_analysis_commit_frequency(
        repo_path=PROJECT_ROOT, by="month"
    )
    assert result["status"] == "ok"
    assert "frequency" in result
    assert "bucket" in result
    assert result["bucket"] == "month"
    assert isinstance(result["frequency"], dict)


@pytest.mark.unit
def test_commit_frequency_week_bucket() -> None:
    """Week-bucketed frequency returns YYYY-WNN format keys."""
    import re
    result = mcp_tools.git_analysis_commit_frequency(
        repo_path=PROJECT_ROOT, by="week"
    )
    assert result["status"] == "ok"
    week_pattern = re.compile(r"^\d{4}-W\d{2}$")
    for key in result["frequency"]:
        assert week_pattern.match(key), f"Key {key!r} not in YYYY-WNN format"


# ── GitNexus-backed MCP tools (graceful degradation tests) ─────────────────


@pytest.mark.unit
def test_index_repo_returns_dict() -> None:
    """git_analysis_index_repo returns a dict (ok or graceful error)."""
    result = mcp_tools.git_analysis_index_repo(repo_path=PROJECT_ROOT)
    assert isinstance(result, dict)
    assert "status" in result
    assert result["status"] in ("ok", "error")


@pytest.mark.unit
def test_query_returns_dict() -> None:
    """git_analysis_query returns a dict (ok or graceful error)."""
    result = mcp_tools.git_analysis_query(
        repo_path=PROJECT_ROOT, query_text="module architecture"
    )
    assert isinstance(result, dict)
    assert "status" in result


@pytest.mark.unit
def test_symbol_context_returns_dict() -> None:
    """git_analysis_symbol_context returns a dict."""
    result = mcp_tools.git_analysis_symbol_context(
        repo_path=PROJECT_ROOT, symbol="GitHistoryAnalyzer"
    )
    assert isinstance(result, dict)
    assert "status" in result


@pytest.mark.unit
def test_impact_returns_dict() -> None:
    """git_analysis_impact returns a dict."""
    result = mcp_tools.git_analysis_impact(
        repo_path=PROJECT_ROOT, symbol="GitHistoryAnalyzer"
    )
    assert isinstance(result, dict)
    assert "status" in result


@pytest.mark.unit
def test_detect_changes_returns_dict() -> None:
    """git_analysis_detect_changes returns a dict."""
    result = mcp_tools.git_analysis_detect_changes(repo_path=PROJECT_ROOT)
    assert isinstance(result, dict)
    assert "status" in result


@pytest.mark.unit
def test_cypher_query_returns_dict() -> None:
    """git_analysis_cypher_query returns a dict."""
    result = mcp_tools.git_analysis_cypher_query(
        repo_path=PROJECT_ROOT,
        cypher_query="MATCH (n) RETURN n LIMIT 5",
    )
    assert isinstance(result, dict)
    assert "status" in result


@pytest.mark.unit
def test_list_indexed_returns_dict() -> None:
    """git_analysis_list_indexed returns a dict."""
    result = mcp_tools.git_analysis_list_indexed()
    assert isinstance(result, dict)
    assert "status" in result


# ── Error handling tests ────────────────────────────────────────────────────


@pytest.mark.unit
def test_commit_history_invalid_path() -> None:
    """GitPython tools return status:error for invalid repo paths."""
    result = mcp_tools.git_analysis_commit_history(
        repo_path="/nonexistent/path/to/repo"
    )
    assert result["status"] == "error"
    assert "error" in result


@pytest.mark.unit
def test_code_churn_invalid_path() -> None:
    """Code churn returns status:error for invalid repo path."""
    result = mcp_tools.git_analysis_code_churn(
        repo_path="/nonexistent/path/to/repo"
    )
    assert result["status"] == "error"


@pytest.mark.unit
def test_mcp_tool_metadata_present() -> None:
    """All 16 MCP tools have _mcp_tool_meta attribute set."""
    tool_functions = [
        mcp_tools.git_analysis_index_repo,
        mcp_tools.git_analysis_query,
        mcp_tools.git_analysis_symbol_context,
        mcp_tools.git_analysis_impact,
        mcp_tools.git_analysis_detect_changes,
        mcp_tools.git_analysis_cypher_query,
        mcp_tools.git_analysis_list_indexed,
        mcp_tools.git_analysis_commit_history,
        mcp_tools.git_analysis_contributor_stats,
        mcp_tools.git_analysis_code_churn,
        mcp_tools.git_analysis_branch_topology,
        mcp_tools.git_analysis_commit_frequency,
        mcp_tools.git_analysis_filtered_history,
        mcp_tools.git_analysis_file_history,
        mcp_tools.git_analysis_directory_churn,
        mcp_tools.git_analysis_hotspots,
    ]
    for func in tool_functions:
        assert hasattr(func, "_mcp_tool_meta"), (
            f"{func.__name__} is missing _mcp_tool_meta"
        )


@pytest.mark.unit
def test_all_tools_have_git_analysis_category() -> None:
    """All MCP tools declare category='git_analysis'."""
    tool_functions = [
        mcp_tools.git_analysis_index_repo,
        mcp_tools.git_analysis_query,
        mcp_tools.git_analysis_symbol_context,
        mcp_tools.git_analysis_impact,
        mcp_tools.git_analysis_detect_changes,
        mcp_tools.git_analysis_cypher_query,
        mcp_tools.git_analysis_list_indexed,
        mcp_tools.git_analysis_commit_history,
        mcp_tools.git_analysis_contributor_stats,
        mcp_tools.git_analysis_code_churn,
        mcp_tools.git_analysis_branch_topology,
        mcp_tools.git_analysis_commit_frequency,
        mcp_tools.git_analysis_filtered_history,
        mcp_tools.git_analysis_file_history,
        mcp_tools.git_analysis_directory_churn,
        mcp_tools.git_analysis_hotspots,
    ]
    for func in tool_functions:
        meta = getattr(func, "_mcp_tool_meta", {})
        assert meta.get("category") == "git_analysis", (
            f"{func.__name__} has category={meta.get('category')!r}, "
            "expected 'git_analysis'"
        )


# ── New tool tests ───────────────────────────────────────────────────────────


@pytest.mark.unit
def test_filtered_history_ok() -> None:
    """git_analysis_filtered_history returns status:ok with commits list."""
    result = mcp_tools.git_analysis_filtered_history(repo_path=PROJECT_ROOT, max_count=5)
    assert result["status"] == "ok"
    assert "commits" in result
    assert "count" in result
    assert isinstance(result["commits"], list)


@pytest.mark.unit
def test_file_history_ok() -> None:
    """git_analysis_file_history returns status:ok for README.md."""
    result = mcp_tools.git_analysis_file_history(
        repo_path=PROJECT_ROOT, file_path="README.md", max_count=5
    )
    assert result["status"] == "ok"
    assert "commits" in result
    assert "file" in result


@pytest.mark.unit
def test_directory_churn_ok() -> None:
    """git_analysis_directory_churn returns status:ok with directories list."""
    result = mcp_tools.git_analysis_directory_churn(repo_path=PROJECT_ROOT, top_n=5)
    assert result["status"] == "ok"
    assert "directories" in result
    assert "count" in result
    assert isinstance(result["directories"], list)


@pytest.mark.unit
def test_hotspots_ok() -> None:
    """git_analysis_hotspots returns status:ok with hotspots list."""
    result = mcp_tools.git_analysis_hotspots(repo_path=PROJECT_ROOT, top_n=5)
    assert result["status"] == "ok"
    assert "hotspots" in result
    assert "count" in result


# ── Input validation tests ───────────────────────────────────────────────────


@pytest.mark.unit
def test_commit_frequency_invalid_by() -> None:
    """git_analysis_commit_frequency returns status:error for invalid 'by' value."""
    result = mcp_tools.git_analysis_commit_frequency(repo_path=PROJECT_ROOT, by="invalid")
    assert result["status"] == "error"
    assert "error" in result


@pytest.mark.unit
def test_code_churn_zero_top_n() -> None:
    """git_analysis_code_churn returns status:error for top_n=0."""
    result = mcp_tools.git_analysis_code_churn(repo_path=PROJECT_ROOT, top_n=0)
    assert result["status"] == "error"
    assert "error" in result


@pytest.mark.unit
def test_commit_history_zero_max_count() -> None:
    """git_analysis_commit_history returns status:error for max_count=0."""
    result = mcp_tools.git_analysis_commit_history(repo_path=PROJECT_ROOT, max_count=0)
    assert result["status"] == "error"
    assert "error" in result
