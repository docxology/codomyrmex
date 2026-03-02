"""Unit tests for the notification MCP tools."""

import pytest
from codomyrmex.notification.mcp_tools import (
    notification_send,
    notification_list_channels,
    notification_get_history,
    _AVAILABLE_CHANNELS,
    _NOTIFICATION_HISTORY
)

@pytest.fixture(autouse=True)
def reset_history():
    """Reset the notification history before each test to ensure test isolation."""
    _NOTIFICATION_HISTORY.clear()
    yield
    _NOTIFICATION_HISTORY.clear()

def test_notification_list_channels():
    """Test listing available notification channels."""
    channels = notification_list_channels()
    assert isinstance(channels, list)
    assert len(channels) == 4
    assert "email" in channels
    assert "slack" in channels
    assert "sms" in channels
    assert "in_app" in channels

def test_notification_send_success():
    """Test successfully sending a notification."""
    result = notification_send(channel="email", message="Hello, World!")

    assert result["status"] == "success"
    assert "Successfully sent" in result["message"]
    assert "notification_id" in result

    # Verify it was added to history
    assert len(_NOTIFICATION_HISTORY) == 1
    history_item = _NOTIFICATION_HISTORY[0]
    assert history_item["channel"] == "email"
    assert history_item["message"] == "Hello, World!"
    assert history_item["status"] == "sent"
    assert "timestamp" in history_item

def test_notification_send_invalid_channel():
    """Test sending a notification to an invalid channel."""
    result = notification_send(channel="invalid_channel", message="Hello!")

    assert result["status"] == "error"
    assert "is not configured or available" in result["message"]

    # Verify it was NOT added to history
    assert len(_NOTIFICATION_HISTORY) == 0

def test_notification_get_history_empty():
    """Test retrieving history when it's empty."""
    history = notification_get_history()
    assert isinstance(history, list)
    assert len(history) == 0

def test_notification_get_history_limit():
    """Test retrieving history respects the limit parameter."""
    # Send 15 notifications
    for i in range(15):
        notification_send(channel="slack", message=f"Message {i}")

    # Check default limit (10)
    history_default = notification_get_history()
    assert len(history_default) == 10

    # Newest items should be first, so the first item should be 'Message 14'
    assert history_default[0]["message"] == "Message 14"
    assert history_default[-1]["message"] == "Message 5"

    # Check custom limit (5)
    history_custom = notification_get_history(limit=5)
    assert len(history_custom) == 5
    assert history_custom[0]["message"] == "Message 14"
    assert history_custom[-1]["message"] == "Message 10"

    # Check larger limit than available (20)
    history_all = notification_get_history(limit=20)
    assert len(history_all) == 15
    assert history_all[0]["message"] == "Message 14"
    assert history_all[-1]["message"] == "Message 0"
