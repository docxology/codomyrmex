"""Zero-mock unit tests for o1 MCP tools."""

import pytest

from codomyrmex.agents.o1.mcp_tools import o1_execute


@pytest.mark.unit
class TestO1ClientMCPTools:
    """Tests for O1Client MCP tools."""

    def test_o1_execute_catches_error(self):
        """Test that o1_execute gracefully catches errors when unconfigured."""
        # Even if unconfigured, it should return a dictionary and not crash the server
        result = o1_execute(prompt="Hello", timeout=1)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
