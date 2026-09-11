"""Tests for the preprocessing MCP tools."""

from codomyrmex.preprocessing.mcp_tools import preprocess_data


def test_preprocess_data():
    """Test preprocess_data tool."""
    result = preprocess_data("  Hello World  ")
    assert result == {"status": "success", "preprocessed": "hello world"}

def test_preprocess_data_empty():
    """Test preprocess_data tool with empty string."""
    result = preprocess_data("")
    assert result == {"status": "success", "preprocessed": ""}
