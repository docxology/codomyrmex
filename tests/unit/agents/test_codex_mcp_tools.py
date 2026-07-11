"""Zero-mock unit tests for codex MCP tools."""

import pytest

from codomyrmex.agents.codex.mcp_tools import codex_execute


@pytest.mark.unit
class TestCodexClientMCPTools:
    """Tests for CodexClient MCP tools."""

    def test_codex_execute_catches_error(self):
        """Test that codex_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = codex_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
