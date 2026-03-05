"""Tests for codomyrmex.aider.mcp_tools — MCP tool functions."""

from __future__ import annotations

import os
import shutil

import pytest

from codomyrmex.aider.mcp_tools import (
    aider_architect,
    aider_ask,
    aider_check,
    aider_config,
    aider_edit,
)

# ---------------------------------------------------------------------------
# aider_check — works with or without aider installed
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderCheck:
    """Tests for aider_check MCP tool."""

    def test_returns_success_status(self):
        """aider_check must always return status='success'."""
        result = aider_check()
        assert result["status"] == "success"

    def test_installed_is_bool(self):
        """aider_check must return 'installed' as a bool."""
        result = aider_check()
        assert isinstance(result["installed"], bool)

    def test_installed_matches_reality(self):
        """aider_check 'installed' must match whether aider is actually in PATH."""
        result = aider_check()
        expected = shutil.which("aider") is not None
        assert result["installed"] is expected

    def test_model_is_string(self):
        """aider_check must return 'model' as a string."""
        result = aider_check()
        assert isinstance(result["model"], str)

    @pytest.mark.skipif(
        shutil.which("aider") is not None,
        reason="Only relevant when aider is NOT installed",
    )
    def test_install_hint_when_not_installed(self):
        """aider_check must include install_hint when aider is not installed."""
        result = aider_check()
        assert result["installed"] is False
        assert "install_hint" in result

    @pytest.mark.skipif(shutil.which("aider") is None, reason="aider not installed")
    def test_version_nonempty_when_installed(self):
        """aider_check must return non-empty version when aider is installed."""
        result = aider_check()
        assert result["installed"] is True
        assert len(result["version"]) > 0


# ---------------------------------------------------------------------------
# aider_config — no subprocess needed, always testable
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderConfigTool:
    """Tests for aider_config MCP tool."""

    def test_returns_success(self):
        """aider_config must always return status='success'."""
        result = aider_config()
        assert result["status"] == "success"

    def test_model_key_present(self):
        """aider_config must include a 'model' key."""
        result = aider_config()
        assert "model" in result
        assert isinstance(result["model"], str)

    def test_timeout_key_present(self):
        """aider_config must include a 'timeout' key."""
        result = aider_config()
        assert "timeout" in result
        assert isinstance(result["timeout"], int)

    def test_has_anthropic_key_reports_correctly(self):
        """aider_config must report has_anthropic_key matching env var."""
        result = aider_config()
        expected = bool(os.environ.get("ANTHROPIC_API_KEY", ""))
        assert result["has_anthropic_key"] is expected

    def test_has_openai_key_reports_correctly(self):
        """aider_config must report has_openai_key matching env var."""
        result = aider_config()
        expected = bool(os.environ.get("OPENAI_API_KEY", ""))
        assert result["has_openai_key"] is expected

    def test_has_any_key_reports_correctly(self):
        """aider_config must report has_any_key as logical OR of key flags."""
        result = aider_config()
        expected = result["has_anthropic_key"] or result["has_openai_key"]
        assert result["has_any_key"] is expected


# ---------------------------------------------------------------------------
# aider_edit — input validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderEdit:
    """Tests for aider_edit MCP tool."""

    def test_empty_file_paths_returns_error(self):
        """aider_edit with empty file_paths must return error."""
        result = aider_edit(file_paths=[], instruction="fix bug")
        assert result["status"] == "error"
        assert "file_paths" in result["message"]

    @pytest.mark.skipif(
        shutil.which("aider") is not None,
        reason="Only relevant when aider is NOT installed",
    )
    def test_returns_error_when_not_installed(self):
        """aider_edit must return error when aider is not installed."""
        result = aider_edit(file_paths=["nonexistent.py"], instruction="fix bug")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


# ---------------------------------------------------------------------------
# aider_ask — input validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderAsk:
    """Tests for aider_ask MCP tool."""

    @pytest.mark.skipif(
        shutil.which("aider") is not None,
        reason="Only relevant when aider is NOT installed",
    )
    def test_returns_error_when_not_installed(self):
        """aider_ask must return error when aider is not installed."""
        result = aider_ask(file_paths=["nonexistent.py"], question="what is this?")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


# ---------------------------------------------------------------------------
# aider_architect — input validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestAiderArchitect:
    """Tests for aider_architect MCP tool."""

    def test_empty_file_paths_returns_error(self):
        """aider_architect with empty file_paths must return error."""
        result = aider_architect(file_paths=[], task="refactor everything")
        assert result["status"] == "error"
        assert "file_paths" in result["message"]

    @pytest.mark.skipif(
        shutil.which("aider") is not None,
        reason="Only relevant when aider is NOT installed",
    )
    def test_returns_error_when_not_installed(self):
        """aider_architect must return error when aider is not installed."""
        result = aider_architect(file_paths=["nonexistent.py"], task="refactor")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


# ---------------------------------------------------------------------------
# Return structure consistency
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestReturnStructure:
    """Ensure all MCP tools return dicts with 'status' key."""

    def test_aider_check_has_status(self):
        """aider_check must return a dict with 'status' key."""
        result = aider_check()
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ("success", "error")

    def test_aider_config_has_status(self):
        """aider_config must return a dict with 'status' key."""
        result = aider_config()
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ("success", "error")

    def test_aider_edit_has_status(self):
        """aider_edit must return a dict with 'status' key."""
        result = aider_edit(file_paths=[], instruction="x")
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ("success", "error")

    def test_aider_architect_has_status(self):
        """aider_architect must return a dict with 'status' key."""
        result = aider_architect(file_paths=[], task="x")
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] in ("success", "error")


# ---------------------------------------------------------------------------
# MCP metadata verification
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aider
class TestMCPMetadata:
    """Verify MCP tool decorator metadata is correctly attached."""

    def test_all_tools_have_mcp_tool_meta(self):
        """All aider MCP tools must have _mcp_tool_meta attribute."""
        tools = [aider_check, aider_edit, aider_ask, aider_architect, aider_config]
        for tool in tools:
            meta = getattr(tool, "_mcp_tool_meta", None)
            assert meta is not None, f"{tool.__name__} missing _mcp_tool_meta"

    def test_all_tools_have_aider_category(self):
        """All aider MCP tools must have category='aider'."""
        tools = [aider_check, aider_edit, aider_ask, aider_architect, aider_config]
        for tool in tools:
            meta = getattr(tool, "_mcp_tool_meta", {})
            assert meta.get("category") == "aider", (
                f"{tool.__name__} has category={meta.get('category')}"
            )

    def test_all_tools_have_description(self):
        """All aider MCP tools must have a non-empty description."""
        tools = [aider_check, aider_edit, aider_ask, aider_architect, aider_config]
        for tool in tools:
            meta = getattr(tool, "_mcp_tool_meta", {})
            assert meta.get("description"), f"{tool.__name__} has empty description"

    def test_tool_names_prefixed_with_codomyrmex(self):
        """All tool names must be prefixed with 'codomyrmex.'."""
        tools = [aider_check, aider_edit, aider_ask, aider_architect, aider_config]
        for tool in tools:
            meta = getattr(tool, "_mcp_tool_meta", {})
            assert meta["name"].startswith("codomyrmex."), (
                f"{tool.__name__} name={meta['name']} missing codomyrmex. prefix"
            )
