"""
Unit tests for the Streaming MCP Tools.
"""

from codomyrmex.streaming.mcp_tools import streaming_create_event, streaming_format_sse


def test_streaming_create_event_success():
    """Test creating a valid event."""
    result = streaming_create_event("message", {"text": "hello"}, "test-topic")

    assert isinstance(result, dict)
    assert result["type"] == "message"
    assert result["data"] == {"text": "hello"}
    assert result["metadata"]["topic"] == "test-topic"
    assert "id" in result
    assert "timestamp" in result


def test_streaming_create_event_invalid_type():
    """Test creating an event with an invalid type returns an error dict."""
    result = streaming_create_event("invalid_type", {"text": "hello"})

    assert isinstance(result, dict)
    assert "error" in result
    assert "invalid_type" in result["error"]
    assert "message" in result["error"]


def test_streaming_format_sse_success():
    """Test formatting an event to SSE string."""
    result = streaming_format_sse("test-123", "connect", {"client_id": "abc"})

    assert isinstance(result, str)
    assert "id: test-123" in result
    assert "event: connect" in result
    assert 'data: {"client_id": "abc"}' in result
    assert result.endswith("\n")


def test_streaming_format_sse_invalid_type():
    """Test formatting with an invalid event type."""
    result = streaming_format_sse("test-123", "invalid", {"foo": "bar"})

    assert isinstance(result, str)
    assert "Error:" in result
    assert "invalid" in result
