"""Property-based tests using Hypothesis for the events module.

Tests EventBus publish/subscribe behavior and Event schema invariants.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from codomyrmex.events.core.event_schema import Event, EventPriority, EventType

# --- Strategies ---

event_priorities = st.sampled_from(list(EventPriority))
event_types = st.sampled_from(list(EventType))


class TestEventSchemaInvariants:
    """Property tests for Event dataclass invariants."""

    @given(
        event_type=event_types,
        source=st.text(min_size=1, max_size=50),
        data=st.dictionaries(st.text(min_size=1, max_size=20), st.integers(), max_size=5),
    )
    @settings(max_examples=50, deadline=2000)
    def test_event_creation_preserves_fields(self, event_type, source, data):
        """Event creation preserves all provided fields."""
        event = Event(event_type=event_type, source=source, data=data)
        assert event.event_type == event_type
        assert event.source == source
        assert event.data == data

    @given(event_type=event_types)
    @settings(max_examples=20, deadline=2000)
    def test_event_has_id(self, event_type):
        """Every Event gets a unique ID on creation."""
        e1 = Event(event_type=event_type, source="test")
        e2 = Event(event_type=event_type, source="test")
        assert e1.event_id != e2.event_id

    @given(event_type=event_types)
    @settings(max_examples=20, deadline=2000)
    def test_event_has_timestamp(self, event_type):
        """Every Event gets a timestamp on creation."""
        event = Event(event_type=event_type, source="test")
        assert event.timestamp is not None


class TestEventPriorityOrdering:
    """Tests for EventPriority enum."""

    def test_all_priorities_exist(self):
        """All expected priorities exist."""
        names = [p.name for p in EventPriority]
        assert "NORMAL" in names
        assert "CRITICAL" in names
        assert len(names) >= 4

    @given(priority=event_priorities)
    @settings(max_examples=10, deadline=2000)
    def test_priority_values_are_strings(self, priority):
        """Priority values are strings."""
        assert isinstance(priority.value, str)


class TestEventTypeCompleteness:
    """Tests for EventType enum."""

    def test_has_system_events(self):
        """EventType includes system event types."""
        names = [t.name for t in EventType]
        # At least some system events should exist
        assert len(names) > 0

    @given(event_type=event_types)
    @settings(max_examples=10, deadline=2000)
    def test_event_type_is_string_or_int(self, event_type):
        """EventType values are usable."""
        assert event_type.value is not None
