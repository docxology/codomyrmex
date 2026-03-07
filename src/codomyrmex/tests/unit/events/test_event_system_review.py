"""
Comprehensive zero-mock tests for the Codomyrmex Event System to verify improvements.
"""

import asyncio

import pytest

from codomyrmex.events import Event, EventBus, EventPriority, EventType
from codomyrmex.events.handlers.event_listener import EventListener
from codomyrmex.events.integration_bus import IntegrationBus


@pytest.fixture
def event_bus():
    bus = EventBus()
    yield bus
    bus.shutdown()


@pytest.fixture
def integration_bus():
    return IntegrationBus()


class TestEventBusReview:
    def test_priority_ordering(self, event_bus):
        """Verify that handlers with higher priority are executed first."""
        execution_order = []

        event_bus.subscribe(
            [EventType.CUSTOM], lambda e: execution_order.append("low"), priority=0
        )
        event_bus.subscribe(
            [EventType.CUSTOM], lambda e: execution_order.append("high"), priority=10
        )
        event_bus.subscribe(
            [EventType.CUSTOM], lambda e: execution_order.append("medium"), priority=5
        )

        event_bus.publish(Event(event_type=EventType.CUSTOM, source="test"))

        assert execution_order == ["high", "medium", "low"]

    def test_wildcard_subscriptions(self, event_bus):
        """Verify wildcard matching (glob patterns)."""
        received = []
        event_bus.subscribe(["system.*"], received.append)

        event_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        event_bus.publish(Event(event_type=EventType.SYSTEM_ERROR, source="test"))
        event_bus.publish(Event(event_type=EventType.ANALYSIS_START, source="test"))

        assert len(received) == 2

    def test_handler_exceptions(self, event_bus):
        """Verify that an exception in one handler does not affect others."""
        received = []

        def faulty_handler(e):
            raise ValueError("Failure")

        event_bus.subscribe(["*"], faulty_handler)
        event_bus.subscribe(["*"], received.append)

        event_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_listener_once_async(self, event_bus):
        """Verify that 'once' async handlers only fire once."""
        # Use a fresh bus and listener for this test to avoid state issues
        bus = EventBus()
        received = asyncio.Event()
        listener = EventListener("test_listener_async", event_bus=bus)

        async def async_handler(e):
            received.set()

        listener.once(EventType.SYSTEM_STARTUP, async_handler)

        # Create a proper Event
        from codomyrmex.events.core.event_schema import Event

        ev = Event(event_type=EventType.SYSTEM_STARTUP, source="test")

        # Publish will use the executor for async handlers
        bus.publish(ev)

        # Wait for the worker thread to finish
        try:
            await asyncio.wait_for(received.wait(), timeout=2.0)
        except TimeoutError:
            pytest.fail("Async handler was not called")

        assert received.is_set()

        # Reset and check it doesn't fire again
        received.clear()
        bus.publish(ev)
        await asyncio.sleep(0.2)

        assert not received.is_set()
        bus.shutdown()

    def test_event_filtering(self, event_bus):
        """Verify subscription filters."""
        received = []

        def important_only(event):
            return event.priority == EventPriority.CRITICAL

        event_bus.subscribe(["*"], received.append, filter_func=important_only)

        event_bus.publish(
            Event(
                event_type=EventType.SYSTEM_STARTUP,
                source="test",
                priority=EventPriority.NORMAL,
            )
        )
        event_bus.publish(
            Event(
                event_type=EventType.SYSTEM_ERROR,
                source="test",
                priority=EventPriority.CRITICAL,
            )
        )

        assert len(received) == 1
        assert received[0].priority == EventPriority.CRITICAL


class TestIntegrationBusReview:
    def test_wildcard_subscriptions(self, integration_bus):
        """Verify wildcard matching in IntegrationBus (currently likely failing for glob)."""
        received = []
        # The current implementation of IntegrationBus.emit only checks exact topic and "*"
        integration_bus.subscribe("system.*", received.append)

        integration_bus.emit("system.startup", "test")

        # This is expected to FAIL with current implementation
        assert len(received) == 1

    def test_priority_ordering(self, integration_bus):
        """Verify priority ordering in IntegrationBus."""
        execution_order = []

        integration_bus.subscribe(
            "test", lambda e: execution_order.append("low"), priority=0
        )
        integration_bus.subscribe(
            "test", lambda e: execution_order.append("high"), priority=10
        )
        integration_bus.subscribe(
            "test", lambda e: execution_order.append("medium"), priority=5
        )

        integration_bus.emit("test", "test")

        assert execution_order == ["high", "medium", "low"]

    def test_handler_exceptions(self, integration_bus):
        """Verify exception isolation in IntegrationBus."""
        received = []

        def faulty_handler(e):
            raise ValueError("Failure")

        integration_bus.subscribe("test", faulty_handler)
        integration_bus.subscribe("test", received.append)

        integration_bus.emit("test", "test")

        assert len(received) == 1


class TestEventEmitterEventListenerReview:
    def test_listener_once(self, event_bus):
        """Verify that 'once' handlers only fire once."""
        received = []
        listener = EventListener("test_listener", event_bus=event_bus)

        listener.once(EventType.SYSTEM_STARTUP, received.append)

        event_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        event_bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        assert len(received) == 1
