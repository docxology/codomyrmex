"""MCP tools for the events module."""

from typing import Any

from codomyrmex.events.core.event_bus import get_event_bus
from codomyrmex.events.core.event_schema import Event, EventPriority, EventType
from codomyrmex.events.event_store import get_event_store
from codomyrmex.events.handlers.event_logger import get_event_logger
from codomyrmex.events.replayer import EventReplayer
from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="events")
def emit_event(
    event_type: str,
    payload: dict[str, Any],
    source: str = "mcp",
    priority: str = "normal",
) -> dict[str, Any]:
    """Emit an event to the event bus.

    Args:
        event_type: Type/topic of the event (e.g. 'system.startup', 'analysis.start').
        payload: Event data dictionary.
        source: Source identifier for the event.
        priority: Event priority ('debug', 'info', 'normal', 'warning', 'error', 'critical').

    Returns:
        Status dict with result.
    """
    try:
        bus = get_event_bus()

        # Try to find the EventType enum member
        try:
            etype = EventType(event_type)
        except ValueError:
            # If not a standard EventType, use CUSTOM and include original type in payload
            etype = EventType.CUSTOM
            payload["original_type"] = event_type

        # Try to find the EventPriority enum member
        try:
            epriority = EventPriority(priority.lower())
        except ValueError:
            epriority = EventPriority.NORMAL

        event = Event(event_type=etype, data=payload, source=source, priority=epriority)
        bus.publish(event)

        return {
            "status": "success",
            "event_id": event.event_id,
            "event_type": event_type,
            "source": source,
            "priority": priority,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to emit event: {e!s}"}


@mcp_tool(category="events")
def list_event_types() -> dict[str, Any]:
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
        return {"status": "error", "message": f"Failed to list event types: {e!s}"}


@mcp_tool(category="events")
def get_event_history(
    event_type: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Retrieve recent event history from the event logger.

    Args:
        event_type: Optional filter by event type string.
        limit: Maximum number of events to return.

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
        return {"status": "error", "message": f"Failed to get event history: {e!s}"}


@mcp_tool(category="events")
def query_event_store(
    topic: str | None = None,
    from_seq: int = 1,
    to_seq: int = 0,
    limit: int = 0,
) -> dict[str, Any]:
    """Query the persistent event store for historical events.

    Args:
        topic: Optional topic filter.
        from_seq: Start sequence number (inclusive).
        to_seq: End sequence number (inclusive, 0 for latest).
        limit: Maximum number of events to return (only if topic is specified).

    Returns:
        Dictionary with list of events from the store.
    """
    try:
        store = get_event_store()
        if topic:
            events = store.read_by_topic(topic, limit=limit)
        else:
            events = store.read(from_seq=from_seq, to_seq=to_seq)

        return {
            "status": "success",
            "events": [e.to_dict() for e in events],
            "count": len(events),
            "latest_sequence": store.latest_sequence,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to query event store: {e!s}"}


@mcp_tool(category="events")
def replay_events(
    from_seq: int = 1,
    to_seq: int = 0,
    topics: list[str] | None = None,
) -> dict[str, Any]:
    """Replay events from the store through the event bus.

    This tool re-publishes historical events to the bus, allowing
    subscribers to process them again.

    Args:
        from_seq: Start sequence number.
        to_seq: End sequence number (0 for latest).
        topics: Optional list of topics to replay.

    Returns:
        Summary of the replay operation.
    """
    try:
        store = get_event_store()
        bus = get_event_bus()
        replayer = EventReplayer(store)

        # Create handlers that re-publish to the bus
        handlers = {}
        if topics:
            for topic in topics:

                def make_handler(t: str):
                    return lambda e: bus.publish(
                        Event(
                            event_type=EventType.CUSTOM,
                            source=f"replayer:{e.source}",
                            data={**e.data, "replayed": True, "original_topic": t},
                        )
                    )

                handlers[topic] = make_handler(topic)
        else:
            # If no topics specified, we'd need to know all topics to replay them all
            # with handlers. Or we can just read them and publish.
            events = store.read(from_seq, to_seq)
            for e in events:
                bus.publish(
                    Event(
                        event_type=EventType.CUSTOM,
                        source=f"replayer:{e.source}",
                        data={**e.data, "replayed": True, "original_topic": e.topic},
                    )
                )
            return {
                "status": "success",
                "events_replayed": len(events),
                "message": f"Replayed {len(events)} events directly.",
            }

        result = replayer.replay(from_seq=from_seq, to_seq=to_seq, handlers=handlers)

        return {
            "status": "success",
            "events_replayed": result.events_replayed,
            "duration_ms": result.duration_ms,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to replay events: {e!s}"}


@mcp_tool(category="events")
def events_send_to_agent(
    agent_id: str,
    message: dict[str, Any],
    source: str = "mcp",
) -> dict[str, Any]:
    """Send a direct message to a specific agent's inbox via the IntegrationBus.

    The message is stored in the agent's in-memory mailbox and also emitted
    as an integration event (topic ``agent.inbox.<agent_id>``) so that any
    subscriber can react to incoming messages.

    Args:
        agent_id: Destination agent identifier (e.g. ``"reviewer"``).
        message: Arbitrary payload dict to deliver.
        source: Sender identifier string.

    Returns:
        dict with status, event_id, and agent_id.
    """
    try:
        from codomyrmex.events.integration_bus import IntegrationBus

        bus = IntegrationBus()
        event_id = bus.send_to_agent(agent_id, message, source=source)
        return {
            "status": "success",
            "event_id": event_id,
            "agent_id": agent_id,
            "message": f"Message delivered to agent '{agent_id}' inbox.",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to send message: {e!s}"}


@mcp_tool(category="events")
def events_agent_inbox(
    agent_id: str,
    timeout: float = 0.0,
    drain: bool = False,
) -> dict[str, Any]:
    """Read messages from an agent's inbox.

    By default returns the **oldest** single message (FIFO).  Set *drain=True*
    to atomically drain all pending messages at once.

    Args:
        agent_id: Recipient agent identifier.
        timeout: Seconds to wait if inbox is empty (0 = no wait).
        drain: If True, return all pending messages at once.

    Returns:
        dict with status, messages list, and count.
    """
    try:
        from codomyrmex.events.integration_bus import IntegrationBus

        bus = IntegrationBus()
        if drain:
            messages = bus.drain_inbox(agent_id)
        else:
            msg = bus.receive(agent_id, timeout=timeout)
            messages = [msg] if msg is not None else []

        return {
            "status": "success",
            "agent_id": agent_id,
            "messages": messages,
            "count": len(messages),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to read inbox: {e!s}"}

