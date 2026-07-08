"""Zero-mock unit tests for gemini MCP tools."""

import pytest

from codomyrmex.agents.gemini.mcp_tools import gemini_execute


@pytest.mark.unit
class TestGeminiClientMCPTools:
    """Tests for GeminiClient MCP tools."""

    def test_gemini_execute_catches_error(self):
        """Test that gemini_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = gemini_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
