"""Zero-mock unit tests for the soul module MCP tools."""

from codomyrmex.soul.mcp_tools import soul_get_personality, soul_reflect


def test_soul_reflect_default_personality() -> None:
    """Test soul_reflect with default personality."""
    query = "What is my purpose?"
    result = soul_reflect(query)
    assert result == "Reflecting on 'What is my purpose?' with personality 'default'."


def test_soul_reflect_custom_personality() -> None:
    """Test soul_reflect with custom personality."""
    query = "Who am I?"
    personality = "philosophical"
    result = soul_reflect(query, personality=personality)
    assert result == "Reflecting on 'Who am I?' with personality 'philosophical'."


def test_soul_reflect_empty_query_error() -> None:
    """Test soul_reflect handles empty query correctly (native exception)."""
    result = soul_reflect("")
    assert result == "Error: Query cannot be empty."


def test_soul_get_personality_default() -> None:
    """Test soul_get_personality with default personality."""
    result = soul_get_personality()
    assert result == "default"


def test_soul_get_personality_custom() -> None:
    """Test soul_get_personality with custom personality."""
    result = soul_get_personality(personality="stoic")
    assert result == "stoic"
