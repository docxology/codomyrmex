"""Zero-mock unit tests for claude MCP tools."""

import pytest

from codomyrmex.agents.claude.mcp_tools import claude_execute


@pytest.mark.unit
class TestClaudeClientMCPTools:
    """Tests for ClaudeClient MCP tools."""

    def test_claude_execute_catches_error(self):
        """Test that claude_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = claude_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
