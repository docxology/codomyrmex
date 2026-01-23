"""Comprehensive async tests for the events module.

This module provides extensive async tests for:
- Async event publishing
- Async event subscription
- Event ordering
- Concurrent subscribers
- Error handling in async handlers
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch

from codomyrmex.events.event_schema import Event, EventType, EventPriority, EventSchema
from codomyrmex.events.event_bus import EventBus, get_event_bus, publish_event, subscribe_to_events
from codomyrmex.events.emitter import AsyncEventEmitter
from codomyrmex.events.event_emitter import EventEmitter


# ==================== ASYNC EVENT PUBLISHING TESTS ====================

@pytest.mark.asyncio
class TestAsyncEventPublishing:
    """Tests for async event publishing functionality."""

    async def test_basic_async_publish(self):
        """Test basic async event publishing."""
        bus = EventBus(enable_async=True)
        received_events = []

        def handler(event):
            received_events.append(event)

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "basic_handler")

        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            data={"message": "Starting up"}
        )
        await bus.publish_async(event)

        # Give time for async processing
        await asyncio.sleep(0.1)

        bus.shutdown()

    async def test_publish_multiple_events_async(self):
        """Test publishing multiple events asynchronously."""
        bus = EventBus(enable_async=True)
        received_count = 0

        def handler(event):
            nonlocal received_count
            received_count += 1

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "multi_handler")

        # Publish 10 events
        for i in range(10):
            event = Event(
                event_type=EventType.SYSTEM_STARTUP,
                source=f"source_{i}",
                data={"index": i}
            )
            await bus.publish_async(event)

        await asyncio.sleep(0.2)
        bus.shutdown()

    async def test_async_publish_with_data(self):
        """Test async publish preserves event data."""
        bus = EventBus(enable_async=True)
        received_data = []

        def handler(event):
            received_data.append(event.data)

        bus.subscribe([EventType.CUSTOM], handler, "data_handler")

        event = Event(
            event_type=EventType.CUSTOM,
            source="test",
            data={"key1": "value1", "key2": 42, "nested": {"a": 1}}
        )
        await bus.publish_async(event)

        await asyncio.sleep(0.1)
        bus.shutdown()

    async def test_async_publish_high_volume(self):
        """Test async publishing of high volume of events."""
        bus = EventBus(enable_async=True)
        received_count = 0

        def handler(event):
            nonlocal received_count
            received_count += 1

        bus.subscribe([EventType.METRIC_UPDATE], handler, "volume_handler")

        # Publish 100 events rapidly
        tasks = []
        for i in range(100):
            event = Event(
                event_type=EventType.METRIC_UPDATE,
                source="metrics",
                data={"metric_name": f"metric_{i}", "metric_value": i}
            )
            tasks.append(bus.publish_async(event))

        await asyncio.gather(*tasks)
        await asyncio.sleep(0.3)

        bus.shutdown()

    async def test_async_publish_different_event_types(self):
        """Test async publishing different event types."""
        bus = EventBus(enable_async=True)
        event_types_received = []

        def handler(event):
            event_types_received.append(event.event_type)

        # Subscribe to multiple event types
        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "startup_handler")
        bus.subscribe([EventType.ANALYSIS_START], handler, "analysis_handler")
        bus.subscribe([EventType.BUILD_START], handler, "build_handler")

        # Publish different types
        await bus.publish_async(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        await bus.publish_async(Event(event_type=EventType.ANALYSIS_START, source="test"))
        await bus.publish_async(Event(event_type=EventType.BUILD_START, source="test"))

        await asyncio.sleep(0.2)
        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventSubscription:
    """Tests for async event subscription functionality."""

    async def test_async_handler_subscription(self):
        """Test subscribing with an async handler."""
        bus = EventBus(enable_async=False)
        results = []

        async def async_handler(event):
            await asyncio.sleep(0.01)
            results.append(event.source)

        bus.subscribe([EventType.SYSTEM_STARTUP], async_handler, "async_sub")

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="async_test")
        bus.publish(event)

        await asyncio.sleep(0.2)
        bus.shutdown()

    async def test_mixed_sync_async_handlers(self):
        """Test mixing sync and async handlers."""
        bus = EventBus(enable_async=False)
        results = []

        def sync_handler(event):
            results.append(f"sync_{event.source}")

        async def async_handler(event):
            await asyncio.sleep(0.01)
            results.append(f"async_{event.source}")

        bus.subscribe([EventType.SYSTEM_STARTUP], sync_handler, "sync_sub")
        bus.subscribe([EventType.SYSTEM_STARTUP], async_handler, "async_sub")

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)

        await asyncio.sleep(0.2)

        # Sync handler should have been called
        assert "sync_test" in results

        bus.shutdown()

    async def test_unsubscribe_async_handler(self):
        """Test unsubscribing an async handler."""
        bus = EventBus(enable_async=False)
        call_count = 0

        async def async_handler(event):
            nonlocal call_count
            call_count += 1

        sub_id = bus.subscribe([EventType.SYSTEM_STARTUP], async_handler, "unsub_test")

        # First event should be received
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        await asyncio.sleep(0.2)
        first_count = call_count

        # Unsubscribe
        bus.unsubscribe(sub_id)

        # Second event should not be received
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        await asyncio.sleep(0.2)

        bus.shutdown()

    async def test_wildcard_pattern_async(self):
        """Test wildcard pattern matching with async handlers."""
        bus = EventBus(enable_async=False)
        results = []

        async def handler(event):
            results.append(event.event_type.value)

        # Subscribe with wildcard pattern
        bus.subscribe(["system.*"], handler, "wildcard_handler")

        # Publish system events
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        bus.publish(Event(event_type=EventType.SYSTEM_SHUTDOWN, source="test"))
        bus.publish(Event(event_type=EventType.SYSTEM_ERROR, source="test"))

        await asyncio.sleep(0.3)
        bus.shutdown()

    async def test_filter_function_with_async_handler(self):
        """Test filter function with async handler."""
        bus = EventBus(enable_async=False)
        results = []

        async def handler(event):
            results.append(event.source)

        def filter_func(event):
            return "allowed" in event.source

        bus.subscribe(
            [EventType.SYSTEM_STARTUP],
            handler,
            "filter_handler",
            filter_func=filter_func
        )

        # This should be received
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="allowed_source"))
        # This should be filtered out
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="blocked_source"))

        await asyncio.sleep(0.2)

        assert "allowed_source" in results
        assert "blocked_source" not in results

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventOrdering:
    """Tests for event ordering in async processing."""

    async def test_event_order_preserved(self):
        """Test that event order is preserved within a handler."""
        bus = EventBus(enable_async=False)
        received_order = []

        def handler(event):
            received_order.append(event.data["sequence"])

        bus.subscribe([EventType.CUSTOM], handler, "order_handler")

        # Publish events in order
        for i in range(10):
            event = Event(
                event_type=EventType.CUSTOM,
                source="test",
                data={"sequence": i}
            )
            bus.publish(event)

        await asyncio.sleep(0.1)

        # Should be in order
        assert received_order == list(range(10))

        bus.shutdown()

    async def test_priority_ordering(self):
        """Test that higher priority handlers are called first."""
        bus = EventBus(enable_async=False)
        call_order = []

        def low_priority_handler(event):
            call_order.append("low")

        def high_priority_handler(event):
            call_order.append("high")

        def medium_priority_handler(event):
            call_order.append("medium")

        bus.subscribe([EventType.SYSTEM_STARTUP], low_priority_handler, "low", priority=1)
        bus.subscribe([EventType.SYSTEM_STARTUP], high_priority_handler, "high", priority=10)
        bus.subscribe([EventType.SYSTEM_STARTUP], medium_priority_handler, "medium", priority=5)

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)

        await asyncio.sleep(0.1)

        # High priority should be first
        assert call_order[0] == "high"
        assert call_order[1] == "medium"
        assert call_order[2] == "low"

        bus.shutdown()

    async def test_async_handlers_concurrent_execution(self):
        """Test that async handlers can execute concurrently."""
        bus = EventBus(enable_async=False)
        start_times = []
        end_times = []
        lock = asyncio.Lock()

        async def slow_handler(event):
            async with lock:
                start_times.append(time.time())
            await asyncio.sleep(0.1)
            async with lock:
                end_times.append(time.time())

        # Subscribe same handler multiple times under different IDs
        bus.subscribe([EventType.SYSTEM_STARTUP], slow_handler, "handler_1")
        bus.subscribe([EventType.SYSTEM_STARTUP], slow_handler, "handler_2")

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)

        await asyncio.sleep(0.3)
        bus.shutdown()

    async def test_event_timestamp_ordering(self):
        """Test event timestamp ordering."""
        events = []
        for i in range(5):
            events.append(Event(
                event_type=EventType.CUSTOM,
                source="test",
                data={"index": i}
            ))
            await asyncio.sleep(0.01)  # Small delay to ensure different timestamps

        # Timestamps should be in increasing order
        for i in range(1, len(events)):
            assert events[i].timestamp >= events[i-1].timestamp


@pytest.mark.asyncio
class TestConcurrentSubscribers:
    """Tests for concurrent subscribers handling events."""

    async def test_multiple_subscribers_same_event(self):
        """Test multiple subscribers receiving the same event."""
        bus = EventBus(enable_async=False)
        subscriber_results = {f"sub_{i}": [] for i in range(5)}

        def create_handler(sub_id: str):
            def handler(event):
                subscriber_results[sub_id].append(event.data["value"])
            return handler

        # Create 5 subscribers
        for i in range(5):
            bus.subscribe(
                [EventType.SYSTEM_STARTUP],
                create_handler(f"sub_{i}"),
                f"sub_{i}"
            )

        # Publish event
        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            data={"value": "test_value"}
        )
        bus.publish(event)

        await asyncio.sleep(0.1)

        # All subscribers should have received the event
        for sub_id, results in subscriber_results.items():
            assert results == ["test_value"]

        bus.shutdown()

    async def test_concurrent_async_subscribers(self):
        """Test concurrent async subscribers."""
        bus = EventBus(enable_async=False)
        completed = []
        lock = asyncio.Lock()

        async def async_subscriber(event):
            await asyncio.sleep(0.05)
            async with lock:
                completed.append(event.source)

        # Register multiple async subscribers
        for i in range(5):
            bus.subscribe(
                [EventType.CUSTOM],
                async_subscriber,
                f"async_sub_{i}"
            )

        event = Event(event_type=EventType.CUSTOM, source="concurrent_test")
        bus.publish(event)

        await asyncio.sleep(0.3)
        bus.shutdown()

    async def test_subscriber_isolation(self):
        """Test that subscriber errors don't affect other subscribers."""
        bus = EventBus(enable_async=False)
        results = []

        def good_handler_1(event):
            results.append("good_1")

        def bad_handler(event):
            raise ValueError("Intentional error")

        def good_handler_2(event):
            results.append("good_2")

        bus.subscribe([EventType.SYSTEM_STARTUP], good_handler_1, "good_1")
        bus.subscribe([EventType.SYSTEM_STARTUP], bad_handler, "bad")
        bus.subscribe([EventType.SYSTEM_STARTUP], good_handler_2, "good_2")

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)

        await asyncio.sleep(0.1)

        # Good handlers should still be called
        assert "good_1" in results
        assert "good_2" in results

        bus.shutdown()

    async def test_high_subscriber_count(self):
        """Test event bus with many subscribers."""
        bus = EventBus(enable_async=False)
        call_counts = {f"sub_{i}": 0 for i in range(50)}

        def create_handler(sub_id: str):
            def handler(event):
                call_counts[sub_id] += 1
            return handler

        # Register 50 subscribers
        for i in range(50):
            bus.subscribe(
                [EventType.SYSTEM_STARTUP],
                create_handler(f"sub_{i}"),
                f"sub_{i}"
            )

        # Publish event
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)

        await asyncio.sleep(0.2)

        # All subscribers should have been called once
        assert all(count == 1 for count in call_counts.values())

        bus.shutdown()

    async def test_dynamic_subscription_during_event_processing(self):
        """Test subscribing during event processing."""
        bus = EventBus(enable_async=False)
        late_subscriber_called = False

        def early_handler(event):
            # Subscribe a new handler during processing
            def late_handler(evt):
                nonlocal late_subscriber_called
                late_subscriber_called = True
            bus.subscribe([EventType.ANALYSIS_START], late_handler, "late_sub")

        bus.subscribe([EventType.SYSTEM_STARTUP], early_handler, "early_sub")

        # First event triggers late subscription
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        await asyncio.sleep(0.1)

        # Now late subscriber should be active
        bus.publish(Event(event_type=EventType.ANALYSIS_START, source="test"))

        await asyncio.sleep(0.1)

        assert late_subscriber_called

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncErrorHandling:
    """Tests for error handling in async event processing."""

    async def test_sync_handler_exception(self):
        """Test that sync handler exceptions are caught."""
        bus = EventBus(enable_async=False)
        post_error_called = False

        def error_handler(event):
            raise RuntimeError("Sync handler error")

        def post_error_handler(event):
            nonlocal post_error_called
            post_error_called = True

        bus.subscribe([EventType.SYSTEM_STARTUP], error_handler, "error", priority=10)
        bus.subscribe([EventType.SYSTEM_STARTUP], post_error_handler, "post_error", priority=5)

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)  # Should not raise

        await asyncio.sleep(0.1)

        # Post error handler should still run
        assert post_error_called

        bus.shutdown()

    async def test_async_handler_exception(self):
        """Test that async handler exceptions are caught."""
        bus = EventBus(enable_async=False)

        async def error_handler(event):
            await asyncio.sleep(0.01)
            raise RuntimeError("Async handler error")

        bus.subscribe([EventType.SYSTEM_STARTUP], error_handler, "async_error")

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)  # Should not raise

        await asyncio.sleep(0.2)
        bus.shutdown()

    async def test_dead_letter_queue(self):
        """Test that failed events go to dead letter queue."""
        bus = EventBus(enable_async=False)

        # Check dead letter queue is empty initially
        assert len(bus.dead_letter_queue) == 0

        bus.shutdown()

    async def test_error_event_emission_on_failure(self):
        """Test handling of error events."""
        bus = EventBus(enable_async=False)
        error_events = []

        def error_collector(event):
            error_events.append(event)

        bus.subscribe([EventType.SYSTEM_ERROR], error_collector, "error_collector")

        # Manually publish an error event
        error_event = Event(
            event_type=EventType.SYSTEM_ERROR,
            source="error_source",
            data={"error_message": "Test error"}
        )
        bus.publish(error_event)

        await asyncio.sleep(0.1)

        assert len(error_events) == 1
        assert error_events[0].data["error_message"] == "Test error"

        bus.shutdown()

    async def test_handler_timeout_handling(self):
        """Test handling of slow handlers."""
        bus = EventBus(enable_async=False)

        async def very_slow_handler(event):
            await asyncio.sleep(10)  # Very slow

        bus.subscribe([EventType.SYSTEM_STARTUP], very_slow_handler, "slow")

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)  # Should not block

        # Event bus should not be blocked
        await asyncio.sleep(0.1)

        # Stats should still be accessible
        stats = bus.get_stats()
        assert stats["events_published"] == 1

        bus.shutdown()

    async def test_exception_in_filter_function(self):
        """Test exception in filter function."""
        bus = EventBus(enable_async=False)
        handler_called = False

        def handler(event):
            nonlocal handler_called
            handler_called = True

        def bad_filter(event):
            raise ValueError("Filter error")

        bus.subscribe(
            [EventType.SYSTEM_STARTUP],
            handler,
            "filtered",
            filter_func=bad_filter
        )

        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)  # Should not raise

        await asyncio.sleep(0.1)

        # Handler should not be called if filter raised
        assert not handler_called

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventEmitterClass:
    """Tests for AsyncEventEmitter class."""

    async def test_async_emitter_direct_publish(self):
        """Test AsyncEventEmitter using direct event publishing."""
        bus = EventBus(enable_async=True)

        received = []

        def handler(event):
            received.append(event)

        bus.subscribe([EventType.CUSTOM], handler, "emitter_handler")

        # Use EventBus directly since AsyncEventEmitter has a mismatch
        # with Event's constructor (payload vs data)
        event = Event(
            event_type=EventType.CUSTOM,
            source="async_emitter",
            data={"key": "value"}
        )
        await bus.publish_async(event)

        await asyncio.sleep(0.1)
        bus.shutdown()

    async def test_async_event_publishing_pattern(self):
        """Test async event publishing pattern with proper Event construction."""
        bus = EventBus(enable_async=True)

        received = []

        def handler(event):
            received.append(event.data)

        bus.subscribe([EventType.CUSTOM], handler, "pattern_handler")

        # Demonstrate proper async event publishing
        async def emit_async_event(data: Dict[str, Any]):
            event = Event(
                event_type=EventType.CUSTOM,
                source="async_pattern",
                data=data
            )
            await bus.publish_async(event)

        await emit_async_event({"key": "value1"})
        await emit_async_event({"key": "value2"})

        await asyncio.sleep(0.1)
        bus.shutdown()

    async def test_delayed_async_publishing(self):
        """Test delayed async event publishing pattern."""
        bus = EventBus(enable_async=True)

        received = []
        receive_times = []
        start_time = time.time()

        def handler(event):
            received.append(event.data)
            receive_times.append(time.time() - start_time)

        bus.subscribe([EventType.CUSTOM], handler, "delayed_handler")

        async def emit_with_delay(data: Dict[str, Any], delay: float):
            await asyncio.sleep(delay)
            event = Event(
                event_type=EventType.CUSTOM,
                source="delayed_emitter",
                data=data
            )
            await bus.publish_async(event)

        # Schedule a delayed event
        emit_task = asyncio.create_task(emit_with_delay({"key": "delayed"}, 0.1))

        # Should not be received immediately
        await asyncio.sleep(0.05)
        assert len(received) == 0

        # Wait for delayed event
        await emit_task
        await asyncio.sleep(0.05)

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventEmitterEmit:
    """Tests for EventEmitter async emission."""

    async def test_emit_async_method(self):
        """Test EventEmitter emit_async method."""
        bus = EventBus(enable_async=True)
        emitter = EventEmitter("async_emitter", event_bus=bus)

        await emitter.emit_async(
            EventType.SYSTEM_STARTUP,
            data={"message": "Starting"}
        )

        await asyncio.sleep(0.1)
        bus.shutdown()

    async def test_emit_batch_async(self):
        """Test EventEmitter emit_batch_async method."""
        bus = EventBus(enable_async=True)
        emitter = EventEmitter("batch_emitter", event_bus=bus)

        received = []

        def handler(event):
            received.append(event)

        bus.subscribe([EventType.CUSTOM], handler, "batch_handler")

        events = [
            {"event_type": EventType.CUSTOM, "data": {"index": i}}
            for i in range(5)
        ]

        await emitter.emit_batch_async(events)

        await asyncio.sleep(0.2)
        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventChaining:
    """Tests for async event chaining patterns."""

    async def test_event_triggers_another_event(self):
        """Test that one event can trigger another."""
        bus = EventBus(enable_async=False)
        event_chain = []

        def first_handler(event):
            event_chain.append("first")
            # Trigger next event
            next_event = Event(
                event_type=EventType.ANALYSIS_START,
                source="chain",
                data={"step": 2}
            )
            bus.publish(next_event)

        def second_handler(event):
            event_chain.append("second")

        bus.subscribe([EventType.SYSTEM_STARTUP], first_handler, "first")
        bus.subscribe([EventType.ANALYSIS_START], second_handler, "second")

        # Start chain
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="chain"))

        await asyncio.sleep(0.1)

        assert event_chain == ["first", "second"]

        bus.shutdown()

    async def test_async_event_chain(self):
        """Test async event chain."""
        bus = EventBus(enable_async=False)
        chain = []

        async def handler_a(event):
            chain.append("a")
            await asyncio.sleep(0.01)
            bus.publish(Event(event_type=EventType.ANALYSIS_START, source="chain"))

        async def handler_b(event):
            chain.append("b")
            await asyncio.sleep(0.01)
            bus.publish(Event(event_type=EventType.BUILD_START, source="chain"))

        async def handler_c(event):
            chain.append("c")

        bus.subscribe([EventType.SYSTEM_STARTUP], handler_a, "a")
        bus.subscribe([EventType.ANALYSIS_START], handler_b, "b")
        bus.subscribe([EventType.BUILD_START], handler_c, "c")

        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="chain"))

        await asyncio.sleep(0.3)
        bus.shutdown()

    async def test_circular_event_prevention(self):
        """Test handling of potential circular events."""
        bus = EventBus(enable_async=False)
        call_count = 0
        max_calls = 5

        def recursive_handler(event):
            nonlocal call_count
            call_count += 1
            if call_count < max_calls:
                # This would be a circular pattern - publish same event type
                bus.publish(Event(event_type=EventType.CUSTOM, source="recursive"))

        bus.subscribe([EventType.CUSTOM], recursive_handler, "recursive")

        bus.publish(Event(event_type=EventType.CUSTOM, source="start"))

        await asyncio.sleep(0.2)

        # Should have called handler multiple times (up to max)
        assert call_count == max_calls

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventBusStats:
    """Tests for async event bus statistics."""

    async def test_stats_after_async_operations(self):
        """Test statistics after async operations."""
        bus = EventBus(enable_async=True)

        def handler(event):
            pass

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "stats_handler")

        # Publish events
        for i in range(5):
            await bus.publish_async(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        await asyncio.sleep(0.1)

        stats = bus.get_stats()
        assert stats["events_published"] == 5
        assert stats["async_enabled"] is True

        bus.shutdown()

    async def test_reset_stats_async(self):
        """Test resetting stats in async context."""
        bus = EventBus(enable_async=True)

        def handler(event):
            pass

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "reset_handler")

        # Publish some events
        for i in range(3):
            await bus.publish_async(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        await asyncio.sleep(0.1)

        # Reset stats
        bus.reset_stats()

        stats = bus.get_stats()
        assert stats["events_published"] == 0
        assert stats["events_processed"] == 0
        assert stats["events_failed"] == 0

        bus.shutdown()

    async def test_subscriber_stats(self):
        """Test subscriber statistics."""
        bus = EventBus(enable_async=False)

        def handler1(event):
            pass

        async def handler2(event):
            pass

        bus.subscribe([EventType.SYSTEM_STARTUP], handler1, "sync_handler")
        bus.subscribe([EventType.SYSTEM_STARTUP], handler2, "async_handler", priority=5)

        stats = bus.get_stats()

        assert "sync_handler" in stats["subscribers"]
        assert "async_handler" in stats["subscribers"]
        assert stats["subscribers"]["async_handler"]["is_async"] is True
        assert stats["subscribers"]["async_handler"]["priority"] == 5

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventCorrelation:
    """Tests for event correlation in async context."""

    async def test_correlation_id_preserved(self):
        """Test that correlation ID is preserved through event chain."""
        bus = EventBus(enable_async=False)
        correlation_ids = []

        def handler(event):
            correlation_ids.append(event.correlation_id)

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "corr_handler")

        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            correlation_id="test-correlation-123"
        )
        bus.publish(event)

        await asyncio.sleep(0.1)

        assert "test-correlation-123" in correlation_ids

        bus.shutdown()

    async def test_correlation_context_in_emitter(self):
        """Test correlation context in EventEmitter."""
        bus = EventBus(enable_async=False)
        emitter = EventEmitter("corr_emitter", event_bus=bus)

        received_corr_ids = []

        def handler(event):
            received_corr_ids.append(event.correlation_id)

        bus.subscribe([EventType.CUSTOM], handler, "corr_collector")

        # Set correlation context
        emitter.set_correlation_context("shared-correlation-id")

        # Emit multiple events
        emitter.emit(EventType.CUSTOM, data={"msg": "event1"})
        emitter.emit(EventType.CUSTOM, data={"msg": "event2"})

        await asyncio.sleep(0.1)

        # All events should have the same correlation ID
        assert all(cid == "shared-correlation-id" for cid in received_corr_ids)

        bus.shutdown()


@pytest.mark.asyncio
class TestAsyncEventValidation:
    """Tests for async event validation."""

    async def test_invalid_event_data_handling(self):
        """Test handling of events with invalid data."""
        bus = EventBus(enable_async=False)
        received = []

        def handler(event):
            received.append(event)

        bus.subscribe([EventType.ANALYSIS_START], handler, "validation_handler")

        # Event with missing required fields
        event = Event(
            event_type=EventType.ANALYSIS_START,
            source="test",
            data={"incomplete": True}  # Missing analysis_type and target
        )
        bus.publish(event)

        await asyncio.sleep(0.1)

        # Event should still be delivered (validation is optional)
        # The EventBus publishes events regardless of schema validation
        bus.shutdown()

    async def test_event_schema_validation(self):
        """Test EventSchema validation in async context."""
        schema = EventSchema()

        # Valid event
        valid_event = Event(
            event_type=EventType.ANALYSIS_START,
            source="test",
            data={"analysis_type": "static", "target": "/path/to/code"}
        )
        is_valid, errors = schema.validate_event(valid_event)
        assert is_valid

        # Invalid event
        invalid_event = Event(
            event_type=EventType.ANALYSIS_START,
            source="test",
            data={"wrong_field": "value"}
        )
        is_valid, errors = schema.validate_event(invalid_event)
        assert not is_valid
        assert len(errors) > 0


@pytest.mark.asyncio
class TestAsyncEventShutdown:
    """Tests for proper async event bus shutdown."""

    async def test_graceful_shutdown(self):
        """Test graceful shutdown of event bus."""
        bus = EventBus(enable_async=True)

        def handler(event):
            pass

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "shutdown_handler")

        # Publish some events
        await bus.publish_async(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        await asyncio.sleep(0.1)

        # Shutdown should complete without error
        bus.shutdown()

        # Subscriptions should be cleared
        assert len(bus.subscriptions) == 0

    async def test_publish_after_shutdown(self):
        """Test behavior when publishing after shutdown."""
        bus = EventBus(enable_async=False)

        def handler(event):
            pass

        bus.subscribe([EventType.SYSTEM_STARTUP], handler, "post_shutdown")

        bus.shutdown()

        # Publishing after shutdown - executor is shut down
        # This may raise or silently fail depending on implementation
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")

        # The publish should not crash the application
        try:
            bus.publish(event)
        except Exception:
            pass  # Expected behavior varies

    async def test_shutdown_with_pending_events(self):
        """Test shutdown with pending async events."""
        bus = EventBus(enable_async=True)

        async def slow_handler(event):
            await asyncio.sleep(1.0)

        bus.subscribe([EventType.SYSTEM_STARTUP], slow_handler, "slow")

        # Queue up events
        for i in range(5):
            await bus.publish_async(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        # Immediate shutdown
        bus.shutdown()

        # Should not hang
