"""Zero-mock unit tests for reporting MCP tools."""

from codomyrmex.reporting.mcp_tools import reporting_process


def test_reporting_process() -> None:
    """Test that the MCP tool properly processes data to a report."""
    result = reporting_process("test data")

    assert result["status"] == "success"
    assert result["report"] == "test data"
