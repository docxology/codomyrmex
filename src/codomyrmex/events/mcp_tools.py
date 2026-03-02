"""MCP tools for the events module."""

from typing import Any

from codomyrmex.events.core.event_bus import get_event_bus
from codomyrmex.events.core.event_schema import Event, EventType
from codomyrmex.events.handlers.event_logger import get_event_logger
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="events")
def emit_event(
    event_type: str,
    payload: dict[str, Any],
    source: str = "mcp",
    priority: str = "normal",
) -> dict:
    """Emit an event to the event bus.

    Args:
        event_type: Type/topic of the event (e.g. 'system.startup', 'analysis.start')
        payload: Event data dictionary
        source: Source identifier for the event
        priority: Event priority ('debug', 'info', 'normal', 'warning', 'error', 'critical')

    Returns:
        Status dict with result.
    """
    try:
        bus = get_event_bus()

        # Try to find the EventType enum member
        try:
            etype = EventType(event_type)
        except ValueError:
            # If not a standard EventType, use it as is if it's a string
            # though Event expects EventType. We might want to support CUSTOM.
            etype = EventType.CUSTOM
            payload["original_type"] = event_type

        from codomyrmex.events.core.event_schema import EventPriority
        try:
            epriority = EventPriority(priority.lower())
        except ValueError:
            epriority = EventPriority.NORMAL

        event = Event(
            event_type=etype,
            data=payload,
            source=source,
            priority=epriority
        )
        bus.publish(event)
        return {
            "status": "success",
            "event_id": event.event_id,
            "event_type": event_type,
            "source": source,
            "priority": priority,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="events")
def list_event_types() -> dict:
    """List all registered event types in the event bus.

    Returns:
        Dictionary with available event types and subscriber counts.
    """
    try:
        bus = get_event_bus()
        types = bus.list_event_types()
        return {
            "status": "success",
            "event_types": types,
            "count": len(types),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="events")
def get_event_history(
    event_type: str | None = None,
    limit: int = 50,
) -> dict:
    """Retrieve recent event history from the event bus.

    Args:
        event_type: Optional filter by event type string
        limit: Maximum number of events to return

    Returns:
        Dictionary with list of recent events.
    """
    try:
        logger = get_event_logger()
        entries = logger.get_events(event_type=event_type)

        # Sort by timestamp descending and apply limit
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        entries = entries[:limit]

        history = [entry.to_dict() for entry in entries]

        return {
            "status": "success",
            "events": history,
            "count": len(history),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
