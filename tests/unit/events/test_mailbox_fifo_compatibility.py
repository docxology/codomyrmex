"""Private in-process mailboxes preserve public FIFO and durable replay."""

from codomyrmex.events.event_store import EventStore
from codomyrmex.events.integration_bus import IntegrationBus


def test_receive_drain_and_durable_replay_preserve_order():
    bus = IntegrationBus(event_store=EventStore())
    for value in range(8):
        bus.send_to_agent("synthetic-a", {"value": value}, source="fixture")
    bus.send_to_agent("synthetic-b", {"value": 99}, source="fixture")
    first = bus.receive("synthetic-a")
    assert first["message"] == {"value": 0}
    remaining = bus.drain_inbox("synthetic-a")
    assert [item["message"]["value"] for item in remaining] == list(range(1, 8))
    assert bus.receive("synthetic-a") is None
    assert bus.drain_inbox("synthetic-a") == []
    assert bus.mailbox_size == 1
    assert [
        item["message"]["value"] for item in bus.replay_from_store("synthetic-a")
    ] == list(range(8))
    assert bus.receive("synthetic-b")["message"] == {"value": 99}
    assert bus.mailbox_size == 0
