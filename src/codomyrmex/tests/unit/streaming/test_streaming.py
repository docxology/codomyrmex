"""Tests for streaming module."""

import pytest

try:
    from codomyrmex.streaming import (
        Event,
        EventType,
        InMemoryStream,
        SSEStream,
        Stream,
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
    def test_message(self):
        assert EventType.MESSAGE is not None

    def test_error(self):
        assert EventType.ERROR is not None

    def test_connect(self):
        assert EventType.CONNECT is not None

    def test_disconnect(self):
        assert EventType.DISCONNECT is not None

    def test_heartbeat(self):
        assert EventType.HEARTBEAT is not None


@pytest.mark.unit
class TestEvent:
    def test_create_event(self):
        event = Event()
        assert event.type == EventType.MESSAGE
        assert event.data is None
        assert event.id is not None

    def test_event_with_data(self):
        event = Event(data={"key": "value"}, type=EventType.ERROR)
        assert event.data == {"key": "value"}
        assert event.type == EventType.ERROR


@pytest.mark.unit
class TestSubscription:
    def test_create_subscription(self):
        sub = Subscription()
        assert sub.topic == "*"
        assert sub.active is True

    def test_subscription_with_handler(self):
        sub = Subscription(topic="events", handler=lambda e: None)
        assert sub.topic == "events"
        assert sub.handler is not None


@pytest.mark.unit
class TestInMemoryStream:
    def test_create_stream(self):
        stream = InMemoryStream()
        assert stream is not None


@pytest.mark.unit
class TestSSEStream:
    def test_create_stream(self):
        stream = SSEStream()
        assert stream is not None

    def test_create_with_buffer_size(self):
        stream = SSEStream(buffer_size=50)
        assert stream is not None


@pytest.mark.unit
class TestTopicStream:
    def test_create_stream(self):
        stream = TopicStream()
        assert stream is not None


@pytest.mark.unit
class TestStreamProcessor:
    def test_create_processor(self):
        source = InMemoryStream()
        processor = StreamProcessor(source=source)
        assert processor is not None


@pytest.mark.unit
class TestCreateEvent:
    def test_creates_event(self):
        event = create_event(data="hello")
        assert isinstance(event, Event)
        assert event.data == "hello"

    def test_with_type(self):
        event = create_event(data=None, event_type=EventType.HEARTBEAT)
        assert event.type == EventType.HEARTBEAT

    def test_with_metadata(self):
        event = create_event(data="test", source="api")
        assert isinstance(event, Event)


@pytest.mark.unit
class TestBroadcast:
    def test_broadcast_is_callable(self):
        assert callable(broadcast)
