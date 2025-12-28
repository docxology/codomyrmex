"""
Unit Tests for Event-Driven Architecture

Tests for the event system components including EventBus, EventEmitter, EventListener, and EventLogger.
"""

import pytest
import time
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.codomyrmex.events.event_schema import Event, EventType, EventPriority, EventSchema
from src.codomyrmex.events.event_bus import EventBus, get_event_bus, publish_event, subscribe_to_events, unsubscribe_from_events
from src.codomyrmex.events.event_emitter import EventEmitter
from src.codomyrmex.events.event_listener import EventListener, AutoEventListener, event_handler, create_listener, create_auto_listener
from src.codomyrmex.events.event_logger import EventLogger, EventLogEntry, get_event_logger, log_event_to_monitoring, get_event_stats, get_recent_events, export_event_logs, generate_performance_report


class TestEventSchema:
    """Test the event schema and validation."""

    def test_event_creation(self):
        """Test creating events."""
        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test_component",
            data={"message": "System starting"},
            priority=EventPriority.NORMAL
        )

        assert event.event_type == EventType.SYSTEM_STARTUP
        assert event.source == "test_component"
        assert event.data == {"message": "System starting"}
        assert event.priority == EventPriority.NORMAL
        assert event.event_id is not None
        assert event.timestamp is not None

    def test_event_schema_validation(self):
        """Test event schema validation."""
        schema = EventSchema()

        # Valid event
        valid_event = Event(
            event_type=EventType.ANALYSIS_START,
            source="analyzer",
            data={"task_id": "123"},
            priority=EventPriority.NORMAL
        )
        assert schema.validate_event(valid_event)

        # Invalid event (missing required field for analysis events)
        invalid_event = Event(
            event_type=EventType.ANALYSIS_START,
            source="analyzer",
            data={},  # Missing task_id
            priority=EventPriority.NORMAL
        )
        assert not schema.validate_event(invalid_event)

    def test_event_type_enum(self):
        """Test event type enumeration."""
        # Check that all expected event types exist
        expected_types = [
            'SYSTEM_STARTUP', 'SYSTEM_SHUTDOWN', 'SYSTEM_ERROR', 'SYSTEM_CONFIG_CHANGE',
            'MODULE_LOAD', 'MODULE_UNLOAD', 'MODULE_ERROR', 'MODULE_CONFIG_UPDATE',
            'ANALYSIS_START', 'ANALYSIS_PROGRESS', 'ANALYSIS_COMPLETE', 'ANALYSIS_ERROR',
            'BUILD_START', 'BUILD_PROGRESS', 'BUILD_COMPLETE', 'BUILD_ERROR'
        ]

        for expected_type in expected_types:
            assert hasattr(EventType, expected_type)

    def test_event_priority_enum(self):
        """Test event priority enumeration."""
        priorities = [EventPriority.DEBUG, EventPriority.INFO, EventPriority.NORMAL,
                     EventPriority.WARNING, EventPriority.ERROR, EventPriority.CRITICAL]

        for priority in priorities:
            assert isinstance(priority, EventPriority)


class TestEventBus:
    """Test the event bus functionality."""

    def setup_method(self):
        """Set up test method."""
        self.bus = EventBus()

    def test_subscribe_and_publish(self):
        """Test subscribing to and publishing events."""
        received_events = []

        def handler(event):
            received_events.append(event)

        # Subscribe to events
        subscriber_id = self.bus.subscribe([EventType.SYSTEM_STARTUP], handler, "test_subscriber")

        # Publish an event
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        self.bus.publish(event)

        # Check that handler was called
        assert len(received_events) == 1
        assert received_events[0].event_type == EventType.SYSTEM_STARTUP

    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        received_events = []

        def handler(event):
            received_events.append(event)

        # Subscribe
        subscriber_id = self.bus.subscribe([EventType.SYSTEM_STARTUP], handler, "test_subscriber")

        # Publish event (should be received)
        event = self.bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received_events) == 1

        # Unsubscribe
        self.bus.unsubscribe(subscriber_id)

        # Publish another event (should not be received)
        self.bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received_events) == 1

    def test_event_filtering(self):
        """Test event filtering."""
        received_events = []

        def handler(event):
            received_events.append(event)

        def filter_func(event):
            return event.source == "allowed_source"

        # Subscribe with filter
        self.bus.subscribe([EventType.SYSTEM_STARTUP], handler, "test_subscriber",
                          filter_func=filter_func)

        # Publish filtered event (should be received)
        event1 = Event(event_type=EventType.SYSTEM_STARTUP, source="allowed_source")
        self.bus.publish(event1)
        assert len(received_events) == 1

        # Publish non-filtered event (should not be received)
        event2 = Event(event_type=EventType.SYSTEM_STARTUP, source="blocked_source")
        self.bus.publish(event2)
        assert len(received_events) == 1

    def test_event_priority(self):
        """Test event handler priority."""
        call_order = []

        def handler1(event):
            call_order.append(1)

        def handler2(event):
            call_order.append(2)

        # Subscribe with different priorities (higher priority first)
        self.bus.subscribe([EventType.SYSTEM_STARTUP], handler1, "handler1", priority=10)
        self.bus.subscribe([EventType.SYSTEM_STARTUP], handler2, "handler2", priority=5)

        # Publish event
        self.bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        # Check that higher priority handler was called first
        assert call_order == [1, 2]


class TestEventEmitter:
    """Test the event emitter functionality."""

    def test_emit_event(self):
        """Test emitting events."""
        emitter = EventEmitter("test_emitter")
        bus = Mock()

        with patch('src.codomyrmex.events.event_emitter.get_event_bus', return_value=bus):
            emitter.emit(EventType.SYSTEM_STARTUP, data={"message": "test"})

            # Check that publish was called
            bus.publish.assert_called_once()
            event = bus.publish.call_args[0][0]
            assert event.event_type == EventType.SYSTEM_STARTUP
            assert event.source == "test_emitter"
            assert event.data == {"message": "test"}

    def test_emit_sync_vs_async(self):
        """Test synchronous and asynchronous event emission."""
        emitter = EventEmitter("test_emitter")
        bus = Mock()

        with patch('src.codomyrmex.events.event_emitter.get_event_bus', return_value=bus):
            # Sync emit
            emitter.emit_sync(EventType.SYSTEM_STARTUP)
            assert bus.publish.called

            bus.reset_mock()

            # Async emit (would need event loop in real scenario)
            # This is more of a structure test
            assert hasattr(emitter, 'emit_async')


class TestEventListener:
    """Test the event listener functionality."""

    def test_event_listener_registration(self):
        """Test registering event handlers."""
        listener = EventListener("test_listener")
        bus = Mock()

        with patch('src.codomyrmex.events.event_listener.get_event_bus', return_value=bus):
            def handler(event):
                pass

            # Register handler
            handler_name = listener.on(EventType.SYSTEM_STARTUP, handler, "test_handler")

            assert handler_name == "test_handler"
            assert handler_name in listener.subscriptions
            bus.subscribe.assert_called_once()

    def test_event_listener_unregistration(self):
        """Test unregistering event handlers."""
        listener = EventListener("test_listener")
        bus = Mock()

        with patch('src.codomyrmex.events.event_listener.get_event_bus', return_value=bus):
            def handler(event):
                pass

            # Register and then unregister
            handler_name = listener.on(EventType.SYSTEM_STARTUP, handler, "test_handler")
            success = listener.off(handler_name)

            assert success
            assert handler_name not in listener.subscriptions
            bus.unsubscribe.assert_called_once()

    def test_once_handler(self):
        """Test one-time event handlers."""
        listener = EventListener("test_listener")
        bus = Mock()

        with patch('src.codomyrmex.events.event_listener.get_event_bus', return_value=bus):
            call_count = 0

            def handler(event):
                nonlocal call_count
                call_count += 1

            # Register one-time handler
            listener.once(EventType.SYSTEM_STARTUP, handler, "once_handler")

            # Simulate multiple events
            event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")

            # First call should work
            if bus.subscribe.called:
                # Get the handler that was registered
                call_args = bus.subscribe.call_args
                registered_handler = call_args[1]['handler']
                registered_handler(event)

                assert call_count == 1

                # Second call should not work (handler should be removed)
                registered_handler(event)
                assert call_count == 1  # Should still be 1

    def test_convenience_listeners(self):
        """Test convenience methods for listening to event groups."""
        listener = EventListener("test_listener")
        bus = Mock()

        with patch('src.codomyrmex.events.event_listener.get_event_bus', return_value=bus):
            def handler(event):
                pass

            # Test analysis events
            handlers = listener.listen_to_analysis_events(handler)
            assert len(handlers) == 4  # ANALYSIS_START, PROGRESS, COMPLETE, ERROR
            assert len(listener.subscriptions) == 4

            # Test build events
            handlers = listener.listen_to_build_events(handler)
            assert len(handlers) == 4
            assert len(listener.subscriptions) == 8

    def test_auto_event_listener(self):
        """Test automatic event listener registration."""

        class TestComponent:
            @event_handler([EventType.SYSTEM_STARTUP])
            def handle_startup(self, event):
                pass

            @event_handler([EventType.SYSTEM_SHUTDOWN], priority=10)
            def handle_shutdown(self, event):
                pass

        component = TestComponent()
        listener = AutoEventListener("auto_listener")

        # Register handlers automatically
        listener.register_handlers(component)

        assert len(listener.subscriptions) == 2


class TestEventLogger:
    """Test the event logger functionality."""

    def setup_method(self):
        """Set up test method."""
        self.logger = EventLogger(max_entries=100)

    def test_event_logging(self):
        """Test logging events."""
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")

        # Log event
        self.logger.log_event(event, handler_count=2, processing_time=0.1)

        # Check that event was logged
        entries = self.logger.get_recent_events()
        assert len(entries) == 1
        assert entries[0].event.event_type == EventType.SYSTEM_STARTUP

    def test_event_statistics(self):
        """Test event statistics generation."""
        # Log multiple events
        events = [
            Event(event_type=EventType.SYSTEM_STARTUP, source="test"),
            Event(event_type=EventType.SYSTEM_STARTUP, source="test"),
            Event(event_type=EventType.ANALYSIS_ERROR, source="test"),
        ]

        for event in events:
            self.logger.log_event(event)

        stats = self.logger.get_event_statistics()

        assert stats['total_events'] == 3
        assert stats['event_counts']['SYSTEM_STARTUP'] == 2
        assert stats['error_counts']['ANALYSIS_ERROR'] == 1

    def test_event_filtering_by_type(self):
        """Test filtering events by type."""
        # Log different event types
        events = [
            Event(event_type=EventType.SYSTEM_STARTUP, source="test"),
            Event(event_type=EventType.ANALYSIS_START, source="test"),
            Event(event_type=EventType.BUILD_START, source="test"),
        ]

        for event in events:
            self.logger.log_event(event)

        # Get only analysis events
        analysis_events = self.logger.get_events_by_type(EventType.ANALYSIS_START)
        assert len(analysis_events) == 1
        assert analysis_events[0].event.event_type == EventType.ANALYSIS_START

    def test_error_events_filtering(self):
        """Test filtering error events."""
        # Log mix of events including errors
        events = [
            Event(event_type=EventType.SYSTEM_STARTUP, source="test"),
            Event(event_type=EventType.ANALYSIS_ERROR, source="test"),
            Event(event_type=EventType.BUILD_ERROR, source="test"),
        ]

        for event in events:
            self.logger.log_event(event)

        # Get error events
        error_events = self.logger.get_error_events()
        assert len(error_events) == 2

    def test_time_range_filtering(self):
        """Test filtering events by time range."""
        base_time = datetime.now()

        # Log events at different times (simulate with different timestamps)
        event1 = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        event2 = Event(event_type=EventType.ANALYSIS_START, source="test")

        # Manually set timestamps to simulate time differences
        event1.timestamp = base_time - timedelta(hours=2)
        event2.timestamp = base_time - timedelta(hours=1)

        self.logger.log_event(event1)
        self.logger.log_event(event2)

        # Get events in range
        start_time = base_time - timedelta(hours=1, minutes=30)
        end_time = base_time
        events_in_range = self.logger.get_events_in_time_range(start_time, end_time)

        assert len(events_in_range) == 1
        assert events_in_range[0].event.event_type == EventType.ANALYSIS_START

    def test_performance_report(self):
        """Test performance report generation."""
        # Log events with processing times
        events = [
            Event(event_type=EventType.SYSTEM_STARTUP, source="test"),
            Event(event_type=EventType.ANALYSIS_START, source="test"),
        ]

        self.logger.log_event(events[0], processing_time=0.1)
        self.logger.log_event(events[1], processing_time=0.2)

        report = self.logger.get_performance_report()

        assert 'event_statistics' in report
        assert 'total_processing_time' in report
        assert report['total_processing_time'] == 0.3
        assert 'average_processing_time_per_event' in report

    def test_log_export(self, tmp_path):
        """Test exporting logs to file."""
        # Log some events
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        self.logger.log_event(event)

        # Export to JSON
        json_file = tmp_path / "logs.json"
        self.logger.export_logs(str(json_file), format='json')

        assert json_file.exists()

        # Export to CSV
        csv_file = tmp_path / "logs.csv"
        self.logger.export_logs(str(csv_file), format='csv')

        assert csv_file.exists()

    def test_log_clearing(self):
        """Test clearing logs."""
        # Log some events
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        self.logger.log_event(event)

        assert len(self.logger.get_recent_events()) == 1

        # Clear logs
        self.logger.clear_logs()

        assert len(self.logger.get_recent_events()) == 0


class TestGlobalFunctions:
    """Test global convenience functions."""

    def test_get_event_bus(self):
        """Test getting the global event bus."""
        bus1 = get_event_bus()
        bus2 = get_event_bus()

        assert bus1 is bus2
        assert isinstance(bus1, EventBus)

    def test_publish_event_function(self):
        """Test the global publish_event function."""
        with patch('src.codomyrmex.events.event_bus.get_event_bus') as mock_get_bus:
            mock_bus = Mock()
            mock_get_bus.return_value = mock_bus

            event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
            publish_event(event)

            mock_bus.publish.assert_called_once_with(event)

    def test_get_event_logger(self):
        """Test getting the global event logger."""
        logger1 = get_event_logger()
        logger2 = get_event_logger()

        assert logger1 is logger2
        assert isinstance(logger1, EventLogger)

    def test_create_listener_functions(self):
        """Test listener creation functions."""
        listener = create_listener("test_listener")
        assert isinstance(listener, EventListener)
        assert listener.listener_id == "test_listener"

        # Test auto listener
        class TestComponent:
            @event_handler([EventType.SYSTEM_STARTUP])
            def handle_event(self, event):
                pass

        component = TestComponent()
        auto_listener = create_auto_listener("auto_test", component)
        assert isinstance(auto_listener, AutoEventListener)
        assert len(auto_listener.subscriptions) == 1
