"""Unit tests for IntegrationBus P2P mailbox methods.

Zero-mock: uses real IntegrationBus instances.
"""

from __future__ import annotations

import threading
import time

from codomyrmex.events.integration_bus import IntegrationBus

# ── send_to_agent ─────────────────────────────────────────────────────────────


def test_send_to_agent_returns_event_id() -> None:
    bus = IntegrationBus()
    event_id = bus.send_to_agent("worker-1", {"task": "analyze"})
    assert isinstance(event_id, str)
    assert event_id.startswith("evt-")


def test_send_to_agent_deposits_in_mailbox() -> None:
    bus = IntegrationBus()
    bus.send_to_agent("agent-a", {"payload": 42})
    assert bus.mailbox_size == 1


def test_send_to_agent_emits_integration_event() -> None:
    bus = IntegrationBus()
    received: list[str] = []
    bus.subscribe("agent.inbox.agent-b", lambda e: received.append(e.event_id))
    bus.send_to_agent("agent-b", {"hello": "world"})
    assert len(received) == 1


def test_send_to_multiple_agents_isolates_mailboxes() -> None:
    bus = IntegrationBus()
    bus.send_to_agent("alpha", {"x": 1})
    bus.send_to_agent("alpha", {"x": 2})
    bus.send_to_agent("beta", {"y": 9})
    assert len(bus._mailboxes["alpha"]) == 2
    assert len(bus._mailboxes["beta"]) == 1


# ── receive ───────────────────────────────────────────────────────────────────


def test_receive_returns_oldest_message_first() -> None:
    bus = IntegrationBus()
    bus.send_to_agent("worker", {"order": 1})
    bus.send_to_agent("worker", {"order": 2})
    msg = bus.receive("worker")
    assert msg is not None
    assert msg["message"]["order"] == 1


def test_receive_returns_none_when_empty() -> None:
    bus = IntegrationBus()
    msg = bus.receive("nobody", timeout=0.0)
    assert msg is None


def test_receive_with_timeout_waits() -> None:
    bus = IntegrationBus()

    def delayed_send():
        time.sleep(0.1)
        bus.send_to_agent("slow-agent", {"arrived": True})

    t = threading.Thread(target=delayed_send, daemon=True)
    t.start()
    msg = bus.receive("slow-agent", timeout=0.5)
    t.join()
    assert msg is not None
    assert msg["message"]["arrived"] is True


# ── drain_inbox ───────────────────────────────────────────────────────────────


def test_drain_inbox_returns_all_messages() -> None:
    bus = IntegrationBus()
    for i in range(5):
        bus.send_to_agent("drainer", {"i": i})
    messages = bus.drain_inbox("drainer")
    assert len(messages) == 5
    assert bus.mailbox_size == 0


def test_drain_inbox_empty_returns_empty_list() -> None:
    bus = IntegrationBus()
    assert bus.drain_inbox("ghost") == []


# ── mailbox_size property ─────────────────────────────────────────────────────


def test_mailbox_size_aggregates_all_agents() -> None:
    bus = IntegrationBus()
    bus.send_to_agent("a1", {"m": 1})
    bus.send_to_agent("a2", {"m": 2})
    bus.send_to_agent("a2", {"m": 3})
    assert bus.mailbox_size == 3
    bus.receive("a1")
    assert bus.mailbox_size == 2
