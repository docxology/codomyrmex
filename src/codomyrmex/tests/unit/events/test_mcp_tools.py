"""Zero-mock tests for the events module MCP tools."""

import pytest

from codomyrmex.events.core.event_bus import get_event_bus
from codomyrmex.events.core.event_schema import EventType
from codomyrmex.events.event_store import StreamEvent, get_event_store
from codomyrmex.events.handlers.event_logger import get_event_logger
from codomyrmex.events.mcp_tools import (
    emit_event,
    get_event_history,
    list_event_types,
    query_event_store,
    replay_events,
)


@pytest.fixture(autouse=True)
def clean_system():
    """Ensure a clean state for the event system before each test."""
    # Reset the singleton bus
    import codomyrmex.events.core.event_bus as bus_mod

    bus_mod._event_bus = None
    get_event_bus()

    # Reset the singleton logger
    import codomyrmex.events.handlers.event_logger as logger_mod

    logger_mod._logger = None
    get_event_logger()

    # Reset the singleton store
    import codomyrmex.events.event_store as store_mod

    store_mod._event_store = None
    get_event_store()


@pytest.mark.unit
def test_emit_event_mcp():
    """Test emitting an event via MCP tool."""
    result = emit_event(
        event_type="test.event",
        payload={"foo": "bar"},
        source="mcp_test",
        priority="high",
    )

    assert result["status"] == "success"
    assert result["event_type"] == "test.event"
    assert "event_id" in result

    # Verify it reached the logger
    logger = get_event_logger()
    history = logger.get_events()
    assert len(history) == 1
    assert history[0].event.data["foo"] == "bar"
    assert history[0].event.source == "mcp_test"


@pytest.mark.unit
def test_list_event_types_mcp():
    """Test listing event types via MCP tool."""
    # Subscribe to something to make it show up
    bus = get_event_bus()
    bus.subscribe(["system.*"], lambda e: None)

    result = list_event_types()
    assert result["status"] == "success"
    assert "system.*" in result["event_types"]
    assert result["count"] >= 1


@pytest.mark.unit
def test_get_event_history_mcp():
    """Test getting event history via MCP tool."""
    emit_event("type.a", {"val": 1})
    emit_event("type.b", {"val": 2})

    result = get_event_history()
    assert result["status"] == "success"
    assert result["count"] == 2
    # Since these are custom types, the event_type will be "custom"
    assert all(e["event_type"] == "custom" for e in result["events"])
    assert any(e["data"]["original_type"] == "type.a" for e in result["events"])
    assert any(e["data"]["original_type"] == "type.b" for e in result["events"])

    # Test filtering
    result_filtered = get_event_history(event_type="custom")
    assert result_filtered["count"] == 2


@pytest.mark.unit
def test_query_event_store_mcp():
    """Test querying the event store via MCP tool."""
    store = get_event_store()
    store.append(StreamEvent(topic="topic.1", event_type="e1", data={"x": 10}))
    store.append(StreamEvent(topic="topic.2", event_type="e2", data={"x": 20}))

    # Query all
    result = query_event_store()
    assert result["status"] == "success"
    assert result["count"] == 2
    assert result["latest_sequence"] == 2

    # Query by topic
    result_topic = query_event_store(topic="topic.1")
    assert result_topic["count"] == 1
    assert result_topic["events"][0]["topic"] == "topic.1"
    assert result_topic["events"][0]["data"]["x"] == 10


@pytest.mark.unit
def test_replay_events_mcp():
    """Test replaying events via MCP tool."""
    store = get_event_store()
    store.append(
        StreamEvent(topic="t1", event_type="e1", data={"id": "orig1"}, source="src1")
    )

    # Track replayed events on the bus
    replayed = []
    bus = get_event_bus()
    bus.subscribe(["*"], replayed.append)

    result = replay_events(topics=["t1"])
    assert result["status"] == "success"
    assert result["events_replayed"] == 1

    # Verify replayed event reached the bus
    # The first event is the one we just replayed.
    # Actually bus.subscribe with "*" might catch other things, but here it's clean.
    assert len(replayed) == 1
    assert replayed[0].event_type == EventType.CUSTOM
    assert replayed[0].source == "replayer:src1"
    assert replayed[0].data["id"] == "orig1"
    assert replayed[0].data["replayed"] is True


@pytest.mark.unit
def test_replay_events_no_topic_mcp():
    """Test replaying all events without topic filter."""
    store = get_event_store()
    store.append(StreamEvent(topic="t1", event_type="e1", data={"v": 1}, source="s1"))
    store.append(StreamEvent(topic="t2", event_type="e2", data={"v": 2}, source="s2"))

    replayed = []
    get_event_bus().subscribe(["*"], replayed.append)

    result = replay_events()
    assert result["status"] == "success"
    assert result["events_replayed"] == 2
    assert len(replayed) == 2
