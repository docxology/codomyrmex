"""
Comprehensive zero-mock tests for the Codomyrmex Event System to verify improvements.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

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
    async def test_listener_once_async(self):
        """Signal the owning loop and drain work before checking a second event."""
        bus = EventBus(max_workers=1)
        loop = asyncio.get_running_loop()
        received = asyncio.Event()
        calls = []
        listener = EventListener("test_listener_async", event_bus=bus)

        async def async_handler(event):
            calls.append(event.event_type)
            loop.call_soon_threadsafe(received.set)

        listener.once(EventType.SYSTEM_STARTUP, async_handler)
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        try:
            bus.publish(event)
            await asyncio.wait_for(received.wait(), timeout=2.0)
            # One worker makes this fence follow all previously queued work.
            await asyncio.wrap_future(bus.executor.submit(lambda: None))
            assert not listener.subscriptions
            bus.publish(event)
            await asyncio.wrap_future(bus.executor.submit(lambda: None))
            assert calls == [EventType.SYSTEM_STARTUP]
            assert bus.events_failed == 0
        finally:
            bus.shutdown()

    @pytest.mark.asyncio
    async def test_listener_once_claims_already_queued_async_wrappers(self):
        bus = EventBus(max_workers=1)
        gate = threading.Event()
        blocker = bus.executor.submit(gate.wait, 2.0)
        calls = []
        listener = EventListener("queued_once", event_bus=bus)

        async def handler(event):
            assert not listener.subscriptions
            calls.append(event.event_type)

        listener.once(EventType.SYSTEM_STARTUP, handler)
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        try:
            # Both wrappers are queued before either can claim the listener.
            bus.publish(event)
            bus.publish(event)
            gate.set()
            assert await asyncio.wrap_future(blocker)
            await asyncio.wrap_future(bus.executor.submit(lambda: None))
            assert calls == [EventType.SYSTEM_STARTUP]
            assert bus.events_failed == 0
        finally:
            gate.set()
            bus.shutdown()

    def test_listener_once_claims_concurrent_sync_snapshots(self, event_bus):
        rendezvous = threading.Barrier(2)
        event_bus.subscribe(
            [EventType.SYSTEM_STARTUP],
            lambda event: rendezvous.wait(timeout=2.0),
            priority=10,
        )
        calls = []
        listener = EventListener("concurrent_once", event_bus=event_bus)
        listener.once(EventType.SYSTEM_STARTUP, calls.append)
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        # Both publishers snapshot the once subscription before rendezvous.
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(event_bus.publish, event) for _ in range(2)]
            for future in futures:
                future.result(timeout=3.0)
        assert calls == [event]
        assert not listener.subscriptions
        assert event_bus.events_failed == 0

    def test_listener_once_unsubscribes_before_recursive_publish(self, event_bus):
        calls = []
        listener = EventListener("recursive_once", event_bus=event_bus)
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")

        def handler(received):
            calls.append(received)
            assert not listener.subscriptions
            if len(calls) == 1:
                event_bus.publish(event)

        listener.once(EventType.SYSTEM_STARTUP, handler)
        event_bus.publish(event)
        assert calls == [event]
        assert event_bus.events_failed == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("async_callback", [False, True])
    async def test_listener_once_remains_consumed_after_callback_error(
        self, async_callback
    ):
        bus = EventBus(max_workers=1)
        listener = EventListener("failing_once", event_bus=bus)
        calls = []

        def fail(event):
            calls.append(event)
            assert not listener.subscriptions
            raise ValueError("expected local callback error")

        async def fail_async(event):
            fail(event)

        listener.once(EventType.SYSTEM_STARTUP, fail_async if async_callback else fail)
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        try:
            bus.publish(event)
            await asyncio.wrap_future(bus.executor.submit(lambda: None))
            bus.publish(event)
            await asyncio.wrap_future(bus.executor.submit(lambda: None))
            assert calls == [event]
            assert bus.events_failed == 1
            assert not listener.subscriptions
        finally:
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
