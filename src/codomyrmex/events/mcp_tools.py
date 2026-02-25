"""MCP tools for the events module."""

from typing import Any, Dict, List, Optional

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="events")
def emit_event(
    event_type: str,
    payload: Dict[str, Any],
    source: str = "mcp",
    priority: str = "normal",
) -> dict:
    """Emit an event to the event bus.

    Args:
        event_type: Type/topic of the event (e.g. 'tool.called', 'task.completed')
        payload: Event data dictionary
        source: Source identifier for the event
        priority: Event priority ('low', 'normal', 'high', 'critical')

    Returns:
        Status dict with event_id and timestamp.
    """
    from codomyrmex.events import EventBus, Event

    try:
        bus = EventBus()
        event = Event(event_type=event_type, data=payload, source=source)
        bus.emit(event)
        return {
            "status": "success",
            "event_type": event_type,
            "source": source,
            "priority": priority,
        }
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="events")
def list_event_types() -> dict:
    """List all registered event types in the event bus.

    Returns:
        Dictionary with available event types and subscriber counts.
    """
    from codomyrmex.events import EventBus

    try:
        bus = EventBus()
        types = bus.list_event_types() if hasattr(bus, "list_event_types") else []
        return {
            "status": "success",
            "event_types": types,
            "count": len(types),
        }
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(category="events")
def get_event_history(
    event_type: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """Retrieve recent event history from the event bus.

    Args:
        event_type: Optional filter by event type
        limit: Maximum number of events to return

    Returns:
        Dictionary with list of recent events.
    """
    from codomyrmex.events import EventBus

    try:
        bus = EventBus()
        if hasattr(bus, "get_history"):
            history = bus.get_history(event_type=event_type, limit=limit)
        else:
            history = []
        return {
            "status": "success",
            "events": history,
            "count": len(history),
        }
    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
        return {"status": "error", "message": str(e)}
