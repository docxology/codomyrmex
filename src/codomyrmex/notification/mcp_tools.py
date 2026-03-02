"""MCP tools for the notification module."""

from datetime import datetime
from codomyrmex.model_context_protocol.tool_decorator import mcp_tool

# In-memory storage for mock backend
_AVAILABLE_CHANNELS = ["email", "slack", "sms", "in_app"]
_NOTIFICATION_HISTORY = []

@mcp_tool(category="notification", description="send a notification via configured channels")
def notification_send(channel: str, message: str) -> dict:
    """Send a notification to the specified channel.

    Args:
        channel: The channel to send the notification to (e.g. 'email', 'slack')
        message: The message to send in the notification

    Returns:
        A dictionary containing the status of the notification sending.
    """
    if channel not in _AVAILABLE_CHANNELS:
        return {
            "status": "error",
            "message": f"Channel '{channel}' is not configured or available. Available channels: {', '.join(_AVAILABLE_CHANNELS)}"
        }

    # Store the notification in history
    notification_record = {
        "channel": channel,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "status": "sent"
    }
    _NOTIFICATION_HISTORY.append(notification_record)

    return {
        "status": "success",
        "message": f"Successfully sent notification via {channel}",
        "notification_id": len(_NOTIFICATION_HISTORY) - 1
    }

@mcp_tool(category="notification", description="list available notification channels")
def notification_list_channels() -> list[str]:
    """List all configured and available notification channels.

    Returns:
        A list of string channel names.
    """
    return list(_AVAILABLE_CHANNELS)

@mcp_tool(category="notification", description="retrieve recent notification history")
def notification_get_history(limit: int = 10) -> list[dict]:
    """Retrieve the recent notification history.

    Args:
        limit: The maximum number of recent notifications to retrieve. Defaults to 10.

    Returns:
        A list of dictionaries representing the recent notification history.
    """
    # Return the last 'limit' items from the history, reversed so newest is first
    return list(reversed(_NOTIFICATION_HISTORY[-limit:])) if _NOTIFICATION_HISTORY else []
