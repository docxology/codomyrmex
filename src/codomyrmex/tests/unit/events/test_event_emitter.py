"""Tests for event emitter functionality.

Sprint 2 coverage: targets ``EventEmitter`` from
``codomyrmex.events.emitters.event_emitter``.
"""

import pytest

from codomyrmex.events.core.event_schema import EventType
from codomyrmex.events.emitters.event_emitter import EventEmitter


class _FakeEventBus:
    """Minimal event bus for testing emitter behaviour."""

    def __init__(self):
        self.published: list = []

    def publish(self, event):
        self.published.append(event)


@pytest.mark.unit
class TestEventEmitter:
    """Tests for EventEmitter emit methods."""

    def _make_emitter(self) -> tuple[EventEmitter, _FakeEventBus]:
        bus = _FakeEventBus()
        emitter = EventEmitter(source="test", event_bus=bus)
        return emitter, bus

    def test_emit_publishes_event(self):
        """emit() publishes a single event to the bus."""
        emitter, bus = self._make_emitter()
        emitter.emit(EventType.SYSTEM_STARTUP, data={"key": "value"})
        assert len(bus.published) == 1
        event = bus.published[0]
        assert event.source == "test"
        assert event.data["key"] == "value"

    def test_emit_disabled(self):
        """emit() does nothing when emitter is disabled."""
        emitter, bus = self._make_emitter()
        emitter.enabled = False
        emitter.emit(EventType.SYSTEM_STARTUP, data={"x": 1})
        assert len(bus.published) == 0

    def test_emit_sync_delegates(self):
        """emit_sync() calls emit() underneath."""
        emitter, bus = self._make_emitter()
        emitter.emit_sync(EventType.SYSTEM_STARTUP)
        assert len(bus.published) == 1

    def test_emit_batch(self):
        """emit_batch() publishes multiple events."""
        emitter, bus = self._make_emitter()
        events = [
            {"event_type": EventType.SYSTEM_STARTUP, "data": {"i": 0}},
            {"event_type": EventType.SYSTEM_SHUTDOWN, "data": {"i": 1}},
        ]
        emitter.emit_batch(events)
        assert len(bus.published) == 2

    def test_emit_batch_disabled(self):
        """emit_batch() does nothing when disabled."""
        emitter, bus = self._make_emitter()
        emitter.enabled = False
        emitter.emit_batch([
            {"event_type": EventType.SYSTEM_STARTUP},
        ])
        assert len(bus.published) == 0

    def test_emit_with_correlation_id(self):
        """emit() propagates correlation_id to the event."""
        emitter, bus = self._make_emitter()
        emitter.emit(
            EventType.SYSTEM_STARTUP,
            correlation_id="abc-123",
        )
        event = bus.published[0]
        assert event.correlation_id == "abc-123"

    def test_emit_with_metadata(self):
        """emit() propagates metadata to the event."""
        emitter, bus = self._make_emitter()
        emitter.emit(
            EventType.SYSTEM_STARTUP,
            metadata={"source_file": "test.py"},
        )
        event = bus.published[0]
        assert event.metadata["source_file"] == "test.py"

    def test_start_operation(self):
        """start_operation() returns a correlation ID and emits start event."""
        emitter, bus = self._make_emitter()
        corr_id = emitter.start_operation("deploy")
        assert isinstance(corr_id, str)
        assert len(corr_id) > 0
        assert len(bus.published) >= 1
