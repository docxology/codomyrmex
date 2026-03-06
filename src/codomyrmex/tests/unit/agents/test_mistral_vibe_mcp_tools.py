"""Zero-mock unit tests for mistral_vibe MCP tools."""

import pytest

from codomyrmex.agents.mistral_vibe.mcp_tools import mistral_vibe_execute


@pytest.mark.unit
class TestMistralVibeClientMCPTools:
    """Tests for MistralVibeClient MCP tools."""

    def test_mistral_vibe_execute_catches_error(self):
        """Test that mistral_vibe_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = mistral_vibe_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
