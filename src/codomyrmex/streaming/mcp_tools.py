"""
MCP Tools for Streaming Module
"""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.streaming.models import EventType, create_event


@mcp_tool()
def streaming_create_event(
    type_str: str, data: dict[str, Any], topic: str = "*"
) -> dict[str, Any]:
    """Create a new streaming event payload and return it as a dictionary.

    Args:
        type_str: The type of the event (e.g., 'message', 'error', 'connect', 'disconnect', 'heartbeat').
        data: The payload data for the event.
        topic: The topic the event belongs to.

    Returns:
        A dictionary representation of the newly created Event.
    """
    try:
        event_type = EventType(type_str)
    except ValueError:
        return {
            "error": f"Invalid event type '{type_str}'. Allowed types: {[t.value for t in EventType]}"
        }

    event = create_event(data=data, event_type=event_type, topic=topic)
    return event.to_dict()


@mcp_tool()
def streaming_format_sse(event_id: str, type_str: str, data: dict[str, Any]) -> str:
    """Format an event into a Server-Sent Events (SSE) string.

    Args:
        event_id: The ID of the event.
        type_str: The type of the event.
        data: The payload data for the event.

    Returns:
        A string formatted for SSE transmission.
    """
    try:
        event_type = EventType(type_str)
    except ValueError:
        return f"Error: Invalid event type '{type_str}'"

    event = create_event(data=data, event_type=event_type)
    event.id = event_id
    return event.to_sse()
