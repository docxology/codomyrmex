"""Tests for static_analysis MCP tools.

Zero-mock policy: tests use real source directories and real analysis functions.
"""

from __future__ import annotations

from pathlib import Path

# Path to the codomyrmex source tree — real, always present
SRC_DIR = Path(__file__).parent.parent.parent.parent  # src/codomyrmex/


def test_import_mcp_tools() -> None:
    """All three MCP tools are importable without errors."""
    from codomyrmex.static_analysis.mcp_tools import (
        static_analysis_audit_exports,
        static_analysis_find_dead_exports,
        static_analysis_full_audit,
    )
    assert callable(static_analysis_audit_exports)
    assert callable(static_analysis_find_dead_exports)
    assert callable(static_analysis_full_audit)


def test_audit_exports_returns_list() -> None:
    """static_analysis_audit_exports returns a list of dicts for a real src dir."""
    from codomyrmex.static_analysis.mcp_tools import static_analysis_audit_exports

    results = static_analysis_audit_exports(str(SRC_DIR))
    assert isinstance(results, list)
    # Every finding has the expected keys
    for item in results:
        assert "module" in item
        assert "issue" in item
        assert "detail" in item


def test_audit_exports_nonexistent_dir_returns_empty() -> None:
    """static_analysis_audit_exports returns [] for a nonexistent directory."""
    from codomyrmex.static_analysis.mcp_tools import static_analysis_audit_exports

    results = static_analysis_audit_exports("/nonexistent_path_xyzzy")
    assert results == []


def test_find_dead_exports_returns_list() -> None:
    """static_analysis_find_dead_exports returns a list of dicts."""
    from codomyrmex.static_analysis.mcp_tools import static_analysis_find_dead_exports

    # Use a small subtree to keep this test fast
    agentic_dir = SRC_DIR / "agentic_memory"
    results = static_analysis_find_dead_exports(str(agentic_dir))
    assert isinstance(results, list)
    for item in results:
        assert "module" in item
        assert "export_name" in item
        assert "detail" in item


def test_full_audit_returns_dict_with_summary() -> None:
    """static_analysis_full_audit returns a dict with summary counts."""
    from codomyrmex.static_analysis.mcp_tools import static_analysis_full_audit

    agentic_dir = SRC_DIR / "agentic_memory"
    report = static_analysis_full_audit(str(agentic_dir))
    assert isinstance(report, dict)
    assert "missing_all" in report
    assert "dead_exports" in report
    assert "unused_functions" in report
    assert "summary" in report
    summary = report["summary"]
    assert "modules_missing_all" in summary
    assert "dead_export_count" in summary
    assert "unused_function_count" in summary
    assert isinstance(summary["modules_missing_all"], int)
    assert isinstance(summary["dead_export_count"], int)
    assert isinstance(summary["unused_function_count"], int)


def test_mcp_tool_meta_attached() -> None:
    """Each MCP tool function has _mcp_tool_meta attribute for bridge discovery."""
    from codomyrmex.static_analysis.mcp_tools import (
        static_analysis_audit_exports,
        static_analysis_find_dead_exports,
        static_analysis_full_audit,
    )
    for fn in (static_analysis_audit_exports, static_analysis_find_dead_exports, static_analysis_full_audit):
        assert hasattr(fn, "_mcp_tool_meta"), f"{fn.__name__} missing _mcp_tool_meta"
