"""Zero-mock unit tests for opencode MCP tools."""

import pytest

from codomyrmex.agents.opencode.mcp_tools import opencode_execute


@pytest.mark.unit
class TestOpenCodeClientMCPTools:
    """Tests for OpenCodeClient MCP tools."""

    def test_opencode_execute_catches_error(self, monkeypatch):
        """The MCP wrapper reports a real unavailable-command failure."""
        from codomyrmex.agents.core.config import get_config, reset_config, set_config

        previous_config = get_config()
        monkeypatch.setenv("OPENCODE_COMMAND", "nonexistent-opencode-command-xyz")
        reset_config()
        try:
            result = opencode_execute(prompt="Hello", timeout=1)
        finally:
            set_config(previous_config)

        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "content" in result
        assert result["error"]
