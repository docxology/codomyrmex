"""Zero-mock unit tests for deepseek MCP tools."""

import pytest

from codomyrmex.agents.deepseek.mcp_tools import deepseek_execute


@pytest.mark.unit
class TestDeepSeekClientMCPTools:
    """Tests for DeepSeekClient MCP tools."""

    def test_deepseek_execute_catches_error(self):
        """Test that deepseek_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = deepseek_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
