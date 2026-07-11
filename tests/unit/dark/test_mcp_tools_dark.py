"""Tests for dark MCP tools."""

from codomyrmex.dark.mcp_tools import (
    dark_list_presets,
    dark_status,
)


class TestDarkStatus:
    def test_returns_dict_with_status(self):
        result = dark_status()
        assert isinstance(result, dict)
        assert "status" in result

    def test_success_has_pdf_available_flag(self):
        result = dark_status()
        assert result["status"] == "success"
        assert "pdf_available" in result
        assert isinstance(result["pdf_available"], bool)

    def test_version_present(self):
        result = dark_status()
        assert "version" in result
        assert isinstance(result["version"], str)

    def test_presets_is_list(self):
        result = dark_status()
        assert "presets" in result
        assert isinstance(result["presets"], list)


class TestDarkListPresets:
    def test_returns_dict_with_status(self):
        result = dark_list_presets()
        assert isinstance(result, dict)
        assert "status" in result

    def test_success_has_presets(self):
        result = dark_list_presets()
        assert result["status"] == "success"
        assert "presets" in result

    def test_pdf_available_flag_present(self):
        result = dark_list_presets()
        assert "pdf_available" in result
        assert isinstance(result["pdf_available"], bool)
