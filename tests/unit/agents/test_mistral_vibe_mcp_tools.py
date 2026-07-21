"""Zero-mock unit tests for mistral_vibe MCP tools."""

import pytest

from codomyrmex.agents.mistral_vibe.mcp_tools import mistral_vibe_execute


@pytest.mark.unit
class TestMistralVibeClientMCPTools:
    """Tests for MistralVibeClient MCP tools."""

    def test_mistral_vibe_execute_catches_error(self, monkeypatch):
        """Test that mistral_vibe_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        # Force a missing command so an installed local Vibe CLI is never invoked by
        # the unit suite. Live CLI coverage is an explicit external-service concern.
        monkeypatch.setenv("MISTRAL_VIBE_COMMAND", "codomyrmex-missing-vibe-command")
        from codomyrmex.agents.core.config import reset_config

        reset_config()
        try:
            result = mistral_vibe_execute(prompt="Hello", timeout=1)
        finally:
            reset_config()
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
