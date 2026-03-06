"""Unit tests for the Perplexity client and tools.

Enforces zero-mock policy. All tests either test structural mechanics
or perform live API executions if the configuration allows.
"""

import os

import pytest

from codomyrmex.agents.core import AgentRequest
from codomyrmex.agents.perplexity import PerplexityClient
from codomyrmex.agents.perplexity.mcp_tools import perplexity_execute


class TestPerplexityClientExecution:
    """Test standard execution paths for the Perplexity API agent."""

    def test_perplexity_missing_key(self):
        """Test graceful failure when PERPLEXITY_API_KEY is missing."""
        old_env = os.environ.get("PERPLEXITY_API_KEY")
        if "PERPLEXITY_API_KEY" in os.environ:
            del os.environ["PERPLEXITY_API_KEY"]

        try:
            from codomyrmex.agents.core.exceptions import AgentConfigurationError
            with pytest.raises(AgentConfigurationError) as exc_info:
                PerplexityClient()
            assert "API key not configured" in str(exc_info.value)

        finally:
            if old_env is not None:
                os.environ["PERPLEXITY_API_KEY"] = old_env

    @pytest.mark.skipif(
        not os.environ.get("PERPLEXITY_API_KEY"),
        reason="Real API key required for live test",
    )
    def test_perplexity_live_execute(self):
        """Execute a simple real query against the live Perplexity API."""
        client = PerplexityClient()
        assert client.test_connection()

        req = AgentRequest(prompt="What color is the sky? Answer in one word.")
        resp = client.execute(req)

        assert resp.is_success()
        assert resp.content.strip()
        assert resp.metadata["agent"] == "perplexity"

    @pytest.mark.skipif(
        not os.environ.get("PERPLEXITY_API_KEY"),
        reason="Real API key required for live test",
    )
    def test_perplexity_mcp_tool_live(self):
        """Test the MCP tool wrapper directly."""
        result = perplexity_execute(prompt="Hello, are you there? Reply yes.", timeout=30)
        assert result["status"] == "success"
        assert result["content"]



