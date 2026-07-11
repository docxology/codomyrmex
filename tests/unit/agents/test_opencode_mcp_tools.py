"""Zero-mock unit tests for opencode MCP tools."""

import pytest

from codomyrmex.agents.opencode.mcp_tools import opencode_execute


@pytest.mark.unit
class TestOpenCodeClientMCPTools:
    """Tests for OpenCodeClient MCP tools."""

    def test_opencode_execute_catches_error(self):
        """Test that opencode_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = opencode_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
