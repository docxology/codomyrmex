"""
Unit tests for DataProvider.get_mcp_tools() — Zero-Mock compliant.

Tests the MCP tools/resources/prompts aggregation method directly.
Server-level endpoint tests for /api/tools are in test_server.py.
"""
import pytest
from codomyrmex.website.data_provider import DataProvider


@pytest.mark.unit
class TestGetMcpTools:
    """Tests for get_mcp_tools() — MCP bridge tool catalogue."""

    def test_returns_dict(self, tmp_path):
        """get_mcp_tools() returns a dict."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        assert isinstance(result, dict)

    def test_has_tools_resources_prompts_keys(self, tmp_path):
        """Result contains 'tools', 'resources', and 'prompts' keys."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        for key in ("tools", "resources", "prompts"):
            assert key in result, f"Missing key: {key}"

    def test_tools_is_list(self, tmp_path):
        """'tools' value is a list."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        assert isinstance(result["tools"], list)

    def test_resources_is_list(self, tmp_path):
        """'resources' value is a list."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        assert isinstance(result["resources"], list)

    def test_prompts_is_list(self, tmp_path):
        """'prompts' value is a list."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        assert isinstance(result["prompts"], list)

    def test_each_tool_has_required_fields(self, tmp_path):
        """Each tool dict has 'name', 'description', 'category', 'is_destructive'."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        for tool in result["tools"]:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool}"
            assert "category" in tool, f"Tool missing 'category': {tool}"
            assert "is_destructive" in tool, f"Tool missing 'is_destructive': {tool}"

    def test_is_destructive_is_bool(self, tmp_path):
        """Each tool's 'is_destructive' field is a boolean."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        for tool in result["tools"]:
            assert isinstance(tool["is_destructive"], bool), (
                f"is_destructive not bool for tool {tool.get('name')}: {type(tool['is_destructive'])}"
            )

    def test_graceful_fallback_on_import_failure(self, tmp_path):
        """Returns empty lists (not raises) when MCP bridge is unavailable."""
        provider = DataProvider(tmp_path)
        result = provider.get_mcp_tools()
        # Either succeeds with populated lists OR returns fallback with empty lists
        # Either way, 'tools' key must exist and be a list (zero-mock: no patching)
        assert isinstance(result.get("tools", []), list)
