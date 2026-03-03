"""Strictly zero-mock unit tests for the text_generation module's MCP tools."""

from codomyrmex.text_generation.mcp_tools import generate_text


def test_generate_text() -> None:
    """Test the generate_text MCP tool."""
    result = generate_text("Hello world", max_length=5)
    assert result == "Generated text for: Hello"
