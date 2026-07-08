"""Zero-mock unit tests for openclaw MCP tools."""

import pytest

from codomyrmex.agents.openclaw.mcp_tools import openclaw_execute


@pytest.mark.unit
class TestOpenClawClientMCPTools:
    """Tests for OpenClawClient MCP tools."""

    def test_openclaw_execute_catches_error(self):
        """Test that openclaw_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = openclaw_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
