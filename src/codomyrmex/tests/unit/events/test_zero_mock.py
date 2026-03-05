"""
Comprehensive zero-mock tests for the Codomyrmex Event System.
"""

import pytest

from codomyrmex.events import Event, EventBus, EventType
from codomyrmex.events.emitters.event_emitter import EventEmitter
from codomyrmex.events.event_store import EventStore, StreamEvent
from codomyrmex.events.handlers.event_listener import AutoEventListener, event_handler
from codomyrmex.events.handlers.event_logger import EventLogger


@pytest.fixture
def clean_bus():
    """Provides a fresh EventBus for each test."""
    bus = EventBus()
    yield bus
    bus.shutdown()


@pytest.mark.unit
class TestEventBusZeroMock:
    """Tests for EventBus without any mocks."""

    def test_subscription_and_delivery(self, clean_bus):
        """Test that events are delivered to subscribers."""
        received = []

        def handler(event):
            received.append(event)

        clean_bus.subscribe([EventType.SYSTEM_STARTUP], handler)

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        clean_bus.publish(event)

        assert len(received) == 1
        assert received[0].event_id == event.event_id

    def test_wildcard_subscription(self, clean_bus):
        """Test wildcard pattern matching."""
        received = []
        clean_bus.subscribe(["system.*"], lambda e: received.append(e))

        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        clean_bus.publish(Event(event_type=EventType.SYSTEM_ERROR, source="test"))
        clean_bus.publish(
            Event(event_type=EventType.ANALYSIS_START, source="test")
        )  # Should NOT match

        assert len(received) == 2

    def test_priority_ordering(self, clean_bus):
        """Test that higher priority subscribers are called first."""
        order = []
        clean_bus.subscribe(["*"], lambda e: order.append("low"), priority=0)
        clean_bus.subscribe(["*"], lambda e: order.append("high"), priority=10)

        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        assert order == ["high", "low"]

    def test_filter_function(self, clean_bus):
        """Test subscription filter functions."""
        received = []

        def my_filter(event):
            return event.data.get("relevant") is True

        clean_bus.subscribe(["*"], lambda e: received.append(e), filter_func=my_filter)

        clean_bus.publish(
            Event(
                event_type=EventType.SYSTEM_STARTUP,
                source="test",
                data={"relevant": False},
            )
        )
        clean_bus.publish(
            Event(
                event_type=EventType.SYSTEM_STARTUP,
                source="test",
                data={"relevant": True},
            )
        )

        assert len(received) == 1
        assert received[0].data["relevant"] is True

    def test_unsubscribe(self, clean_bus):
        """Test unsubscription."""
        received = []
        sub_id = clean_bus.subscribe(["*"], lambda e: received.append(e))

        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received) == 1

        clean_bus.unsubscribe(sub_id)
        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received) == 1

    def test_error_in_handler_isolation(self, clean_bus):
        """Test that an error in one handler doesn't stop others."""
        received = []

        def faulty_handler(e):
            raise RuntimeError("Boom")

        clean_bus.subscribe(["*"], faulty_handler)
        clean_bus.subscribe(["*"], lambda e: received.append(e))

        # Should not raise exception
        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        assert len(received) == 1
        assert clean_bus.get_stats()["events_failed"] == 1


@pytest.mark.unit
class TestEventEmitterZeroMock:
    """Tests for EventEmitter."""

    def test_emitter_basics(self, clean_bus):
        received = []
        clean_bus.subscribe(["*"], lambda e: received.append(e))

        emitter = EventEmitter(source="my_component", event_bus=clean_bus)
        emitter.emit(EventType.TASK_STARTED, data={"id": 1})

        assert len(received) == 1
        assert received[0].source == "my_component"
        assert received[0].data == {"id": 1}

    def test_emitter_context_manager(self, clean_bus):
        received = []
        clean_bus.subscribe(["*"], lambda e: received.append(e))

        from codomyrmex.events.emitters.event_emitter import EventOperationContext

        emitter = EventEmitter(source="component", event_bus=clean_bus)
        with EventOperationContext(emitter, "my_op", {"param": "val"}):
            pass

        # Should have 1 start and 1 end event
        assert len(received) == 2
        assert any(e.data.get("phase") == "start" for e in received)
        assert any(e.data.get("phase") == "end" for e in received)


@pytest.mark.unit
class TestEventListenerZeroMock:
    """Tests for EventListener and AutoEventListener."""

    def test_auto_event_listener(self, clean_bus):
        class MyHandler:
            def __init__(self):
                self.count = 0

            @event_handler(EventType.SYSTEM_STARTUP)
            def handle(self, e):
                self.count += 1

        obj = MyHandler()
        listener = AutoEventListener(listener_id="test", event_bus=clean_bus)
        listener.register_handlers(obj)

        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert obj.count == 1


@pytest.mark.unit
class TestEventLoggerZeroMock:
    """Tests for EventLogger."""

    def test_logger_recording(self, clean_bus):
        logger = EventLogger(event_bus=clean_bus)

        clean_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="s1"))
        clean_bus.publish(Event(event_type=EventType.SYSTEM_ERROR, source="s1"))

        stats = logger.get_event_statistics()
        assert stats["total_events"] == 2
        assert stats["event_counts"][EventType.SYSTEM_STARTUP.value] == 1
        assert stats["error_counts"][EventType.SYSTEM_ERROR.value] == 1


@pytest.mark.unit
class TestEventStoreZeroMock:
    """Tests for EventStore."""

    def test_store_append_read(self):
        store = EventStore()

        store.append(StreamEvent(topic="t1", event_type="e1", data={"v": 1}))
        store.append(StreamEvent(topic="t1", event_type="e2", data={"v": 2}))
        store.append(StreamEvent(topic="t2", event_type="e3", data={"v": 3}))

        assert store.count == 3
        assert len(store.read_by_topic("t1")) == 2
        assert len(store.read_by_topic("t2")) == 1

        events = store.read(from_seq=1, to_seq=2)
        assert len(events) == 2
        assert events[0].sequence == 1
        assert events[1].sequence == 2

    def test_compaction(self):
        store = EventStore()
        for _i in range(10):
            store.append(StreamEvent(topic="t", event_type="e"))

        removed = store.compact(before_seq=6)
        assert removed == 5
        assert store.count == 5
        assert store.read()[0].sequence == 6
