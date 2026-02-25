"""Tests for events.core.event_bus — EventBus, Subscription, and helpers.

Covers:
- EventBus subscribe / publish / unsubscribe lifecycle
- Subscription.matches_event with exact type and wildcard patterns
- get_stats and reset_stats accounting
- shutdown cleans up executor
- Module-level helpers: get_event_bus, subscribe_to_events, unsubscribe_from_events
- Event construction via EventSchema
"""

import pytest

from codomyrmex.events.core.event_bus import (
    EventBus,
    Subscription,
    get_event_bus,
    subscribe_to_events,
    unsubscribe_from_events,
)
from codomyrmex.events.core.event_schema import Event, EventType

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(event_type: EventType = EventType.SYSTEM_STARTUP, data: dict | None = None) -> Event:
    return Event(event_type=event_type, source="test", data=data or {})


# ---------------------------------------------------------------------------
# Subscription.matches_event
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSubscriptionMatchesEvent:
    """Tests for Subscription.matches_event."""

    def test_exact_type_matches(self):
        """Subscription with exact EventType matches that event."""
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={EventType.SYSTEM_STARTUP.value},
            handler=lambda e: None,
        )
        event = _make_event(EventType.SYSTEM_STARTUP)
        assert sub.matches_event(event) is True

    def test_wrong_type_does_not_match(self):
        """Subscription does not match a different event type."""
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={EventType.SYSTEM_SHUTDOWN.value},
            handler=lambda e: None,
        )
        event = _make_event(EventType.SYSTEM_STARTUP)
        assert sub.matches_event(event) is False

    def test_wildcard_pattern_matches(self):
        """Wildcard pattern 'system.*' matches any system event."""
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={"system.*"},
            handler=lambda e: None,
        )
        event = _make_event(EventType.SYSTEM_ERROR)
        assert sub.matches_event(event) is True

    def test_wildcard_does_not_match_other_domain(self):
        """Wildcard 'system.*' does not match 'module.load'."""
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={"system.*"},
            handler=lambda e: None,
        )
        event = _make_event(EventType.MODULE_LOAD)
        assert sub.matches_event(event) is False

    def test_filter_func_blocks_match(self):
        """Filter function returning False blocks an otherwise matching event."""
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={EventType.SYSTEM_STARTUP.value},
            handler=lambda e: None,
            filter_func=lambda e: False,  # always reject
        )
        event = _make_event(EventType.SYSTEM_STARTUP)
        assert sub.matches_event(event) is False

    def test_filter_func_allows_match(self):
        """Filter function returning True still allows an otherwise matching event."""
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={EventType.SYSTEM_STARTUP.value},
            handler=lambda e: None,
            filter_func=lambda e: True,
        )
        event = _make_event(EventType.SYSTEM_STARTUP)
        assert sub.matches_event(event) is True


# ---------------------------------------------------------------------------
# EventBus lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEventBusSubscribePublish:
    """Tests for EventBus subscribe, publish, and unsubscribe."""

    def test_subscribe_returns_id(self):
        """subscribe() returns a non-empty subscriber_id string."""
        bus = EventBus()
        sid = bus.subscribe([EventType.SYSTEM_STARTUP], handler=lambda e: None)
        assert isinstance(sid, str)
        assert len(sid) > 0
        bus.shutdown()

    def test_publish_delivers_to_subscriber(self):
        """publish() calls the handler for matching event types."""
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe([EventType.SYSTEM_STARTUP], handler=received.append)

        event = _make_event(EventType.SYSTEM_STARTUP)
        bus.publish(event)

        assert len(received) == 1
        assert received[0].event_type == EventType.SYSTEM_STARTUP
        bus.shutdown()

    def test_publish_does_not_deliver_to_wrong_subscriber(self):
        """publish() does not deliver to handlers subscribed to other event types."""
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe([EventType.SYSTEM_SHUTDOWN], handler=received.append)

        event = _make_event(EventType.SYSTEM_STARTUP)
        bus.publish(event)

        assert len(received) == 0
        bus.shutdown()

    def test_unsubscribe_stops_delivery(self):
        """unsubscribe() prevents further delivery to the handler."""
        bus = EventBus()
        received: list[Event] = []
        sid = bus.subscribe([EventType.SYSTEM_STARTUP], handler=received.append)

        bus.unsubscribe(sid)
        bus.publish(_make_event(EventType.SYSTEM_STARTUP))

        assert len(received) == 0
        bus.shutdown()

    def test_unsubscribe_unknown_id_returns_false(self):
        """unsubscribe() on an unknown ID returns False without crashing."""
        bus = EventBus()
        result = bus.unsubscribe("nonexistent-subscriber-id")
        assert result is False
        bus.shutdown()

    def test_multiple_subscribers_all_receive(self):
        """Multiple subscribers to the same event type all receive the event."""
        bus = EventBus()
        counts = [0, 0]
        bus.subscribe([EventType.MODULE_LOAD], handler=lambda e: counts.__setitem__(0, counts[0] + 1))
        bus.subscribe([EventType.MODULE_LOAD], handler=lambda e: counts.__setitem__(1, counts[1] + 1))

        bus.publish(_make_event(EventType.MODULE_LOAD))

        assert counts == [1, 1]
        bus.shutdown()


# ---------------------------------------------------------------------------
# get_stats / reset_stats
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEventBusStats:
    """Tests for EventBus get_stats and reset_stats."""

    def test_initial_stats_are_zero(self):
        """A fresh EventBus reports zero events published."""
        bus = EventBus()
        stats = bus.get_stats()
        assert isinstance(stats, dict)
        assert stats.get("events_published", 0) == 0
        bus.shutdown()

    def test_stats_increment_on_publish(self):
        """get_stats() reflects the number of events published."""
        bus = EventBus()
        bus.subscribe([EventType.SYSTEM_STARTUP], handler=lambda e: None)

        bus.publish(_make_event(EventType.SYSTEM_STARTUP))
        bus.publish(_make_event(EventType.SYSTEM_STARTUP))

        stats = bus.get_stats()
        assert stats.get("events_published", 0) >= 2
        bus.shutdown()

    def test_reset_stats_clears_counters(self):
        """reset_stats() resets event_published to zero."""
        bus = EventBus()
        bus.subscribe([EventType.SYSTEM_STARTUP], handler=lambda e: None)
        bus.publish(_make_event(EventType.SYSTEM_STARTUP))

        bus.reset_stats()
        stats = bus.get_stats()
        assert stats.get("events_published", 0) == 0
        bus.shutdown()


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestModuleLevelHelpers:
    """Tests for module-level convenience functions."""

    def test_get_event_bus_returns_event_bus(self):
        """get_event_bus() returns an EventBus instance."""
        bus = get_event_bus()
        assert isinstance(bus, EventBus)

    def test_subscribe_to_events_returns_id(self):
        """subscribe_to_events() returns a subscriber ID string."""
        sid = subscribe_to_events(
            [EventType.SYSTEM_STARTUP],
            handler=lambda e: None,
            subscriber_id="test-subscriber-helpers",
        )
        assert isinstance(sid, str)
        unsubscribe_from_events(sid)

    def test_unsubscribe_from_events_returns_bool(self):
        """unsubscribe_from_events() returns True for a known subscriber."""
        sid = subscribe_to_events(
            [EventType.SYSTEM_ERROR],
            handler=lambda e: None,
        )
        result = unsubscribe_from_events(sid)
        assert result is True
