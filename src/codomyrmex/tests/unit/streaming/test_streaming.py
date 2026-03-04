"""Tests for streaming module."""

import pytest

try:
    from codomyrmex.events.streaming import (
        Event,
        EventType,
        InMemoryStream,
        SSEStream,
        StreamProcessor,
        Subscription,
        TopicStream,
        broadcast,
        create_event,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("streaming module not available", allow_module_level=True)


@pytest.mark.unit
class TestEventType:
    """Test suite for EventType."""
    def test_message(self):
        """Verify message behavior."""
        assert EventType.MESSAGE is not None

    def test_error(self):
        """Verify error behavior."""
        assert EventType.ERROR is not None

    def test_connect(self):
        """Verify connect behavior."""
        assert EventType.CONNECT is not None

    def test_disconnect(self):
        """Verify disconnect behavior."""
        assert EventType.DISCONNECT is not None

    def test_heartbeat(self):
        """Verify heartbeat behavior."""
        assert EventType.HEARTBEAT is not None


@pytest.mark.unit
class TestEvent:
    """Test suite for Event."""
    def test_create_event(self):
        """Verify create event behavior."""
        event = Event()
        assert event.type == EventType.MESSAGE
        assert event.data is None
        assert event.id is not None

    def test_event_with_data(self):
        """Verify event with data behavior."""
        event = Event(data={"key": "value"}, type=EventType.ERROR)
        assert event.data == {"key": "value"}
        assert event.type == EventType.ERROR


@pytest.mark.unit
class TestSubscription:
    """Test suite for Subscription."""
    def test_create_subscription(self):
        """Verify create subscription behavior."""
        sub = Subscription()
        assert sub.topic == "*"
        assert sub.active is True

    def test_subscription_with_handler(self):
        """Verify subscription with handler behavior."""
        sub = Subscription(topic="events", handler=lambda e: None)
        assert sub.topic == "events"
        assert sub.handler is not None


@pytest.mark.unit
class TestInMemoryStream:
    """Test suite for InMemoryStream."""
    def test_create_stream(self):
        """Verify create stream behavior."""
        stream = InMemoryStream()
        assert stream is not None


@pytest.mark.unit
class TestSSEStream:
    """Test suite for SSEStream."""
    def test_create_stream(self):
        """Verify create stream behavior."""
        stream = SSEStream()
        assert stream is not None

    def test_create_with_buffer_size(self):
        """Verify create with buffer size behavior."""
        stream = SSEStream(buffer_size=50)
        assert stream is not None


@pytest.mark.unit
class TestTopicStream:
    """Test suite for TopicStream."""
    def test_create_stream(self):
        """Verify create stream behavior."""
        stream = TopicStream()
        assert stream is not None


@pytest.mark.unit
class TestStreamProcessor:
    """Test suite for StreamProcessor."""
    def test_create_processor(self):
        """Verify create processor behavior."""
        source = InMemoryStream()
        processor = StreamProcessor(source=source)
        assert processor is not None


@pytest.mark.unit
class TestCreateEvent:
    """Test suite for CreateEvent."""
    def test_creates_event(self):
        """Verify creates event behavior."""
        event = create_event(data="hello")
        assert isinstance(event, Event)
        assert event.data == "hello"

    def test_with_type(self):
        """Verify with type behavior."""
        event = create_event(data=None, event_type=EventType.HEARTBEAT)
        assert event.type == EventType.HEARTBEAT

    def test_with_metadata(self):
        """Verify with metadata behavior."""
        event = create_event(data="test", source="api")
        assert isinstance(event, Event)


@pytest.mark.unit
class TestBroadcast:
    """Test suite for Broadcast."""
    def test_broadcast_is_callable(self):
        """Verify broadcast is callable behavior."""
        assert callable(broadcast)
