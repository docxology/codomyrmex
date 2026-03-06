"""Zero-mock unit tests for every_code MCP tools."""

import pytest

from codomyrmex.agents.every_code.mcp_tools import every_code_execute


@pytest.mark.unit
class TestEveryCodeClientMCPTools:
    """Tests for EveryCodeClient MCP tools."""

    def test_every_code_execute_catches_error(self):
        """Test that every_code_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = every_code_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
