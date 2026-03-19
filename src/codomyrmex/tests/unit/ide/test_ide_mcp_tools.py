"""Tests for codomyrmex.ide.mcp_tools — IDE MCP tool functions."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from codomyrmex.ide.mcp_tools import (
    ide_cursor_get_active_file,
    ide_cursor_rules_read,
    ide_cursor_workspace_info,
    ide_get_active_file,
    ide_list_tools,
)


@pytest.mark.unit
class TestIdeGetActiveFileAntigravity:
    """Antigravity-backed ide_get_active_file returns structured dict."""

    def test_returns_dict_with_backend(self):
        result = ide_get_active_file()
        assert isinstance(result, dict)
        assert "status" in result
        assert result.get("backend") == "antigravity"


@pytest.mark.unit
class TestIdeListToolsAntigravity:
    """Antigravity ide_list_tools returns tool list or error."""

    def test_returns_dict_with_backend(self):
        result = ide_list_tools()
        assert isinstance(result, dict)
        assert result.get("backend") == "antigravity"
        assert result["status"] in ("success", "error")


@pytest.mark.unit
class TestIdeCursorMcpTools:
    """Cursor-backed MCP tools use real temp workspaces."""

    def test_workspace_info_on_empty_dir(self, tmp_path):
        result = ide_cursor_workspace_info(workspace_path=str(tmp_path))
        assert result["status"] == "success"
        assert result["backend"] == "cursor"
        assert result["connected"] is True
        assert result["workspace"] == str(tmp_path.resolve())
        assert result["cursor_dir_exists"] is False
        assert result["cursorrules_exists"] is False
        assert "features" in result["capabilities"]

    def test_workspace_info_missing_path(self, tmp_path):
        missing = tmp_path / "does_not_exist"
        result = ide_cursor_workspace_info(workspace_path=str(missing))
        assert result["status"] == "success"
        assert result["connected"] is False

    def test_get_active_file_prefers_newer_file(self, tmp_path):
        older = tmp_path / "older.py"
        newer = tmp_path / "newer.py"
        older.write_text("a", encoding="utf-8")
        time.sleep(0.02)
        newer.write_text("b", encoding="utf-8")
        result = ide_cursor_get_active_file(workspace_path=str(tmp_path))
        assert result["status"] == "success"
        assert result["found"] is True
        assert result["active_file"] == str(newer.resolve())

    def test_rules_read_missing_file(self, tmp_path):
        result = ide_cursor_rules_read(workspace_path=str(tmp_path))
        assert result["status"] == "success"
        assert result["exists"] is False
        assert result["content"] == ""
        assert result["truncated"] is False

    def test_rules_read_truncation(self, tmp_path):
        rules = tmp_path / ".cursorrules"
        long_text = "x" * 50
        rules.write_text(long_text, encoding="utf-8")
        result = ide_cursor_rules_read(workspace_path=str(tmp_path), max_chars=20)
        assert result["status"] == "success"
        assert result["exists"] is True
        assert result["truncated"] is True
        assert result["total_chars"] == 50
        assert len(result["content"]) == 20

    def test_get_active_file_nonexistent_workspace(self, tmp_path):
        missing = tmp_path / "nope"
        result = ide_cursor_get_active_file(workspace_path=str(missing))
        assert result["status"] == "error"
        assert "message" in result


@pytest.mark.unit
class TestIdeMcpToolMetadata:
    """MCP bridge metadata and committed Cursor rule layout."""

    def test_ide_mcp_functions_expose_tool_meta(self):
        import codomyrmex.ide.mcp_tools as m

        for name in (
            "ide_cursor_workspace_info",
            "ide_cursor_get_active_file",
            "ide_cursor_rules_read",
            "ide_get_active_file",
            "ide_list_tools",
        ):
            fn = getattr(m, name)
            meta = getattr(fn, "_mcp_tool_meta", None)
            assert meta is not None, name
            assert meta["name"].startswith("codomyrmex.")
            assert meta["category"] == "ide"

    def test_committed_cursor_project_rule_exists(self):
        # .../src/codomyrmex/tests/unit/ide/test_ide_mcp_tools.py -> repo root
        root = Path(__file__).resolve().parents[5]
        rule = root / ".cursor" / "rules" / "codomyrmex-workspace.mdc"
        assert rule.is_file(), f"Expected committed Cursor rule at {rule}"
        text = rule.read_text(encoding="utf-8")
        assert "alwaysApply:" in text
        assert "CLAUDE.md" in text
