"""Tests for the events module.

Covers:
- EventBus: subscribe, publish, emit_typed, unsubscribe, stats, shutdown
- Event/EventSchema: creation, serialization, validation
- InMemoryStream/SSEStream/TopicStream: publish, subscribe, buffer, routing
- Streaming models: Event, Subscription, create_event
- NotificationRouter/NotificationService: routing rules, providers, templates, broadcast
- Convenience event creators
"""

import asyncio
import json
import uuid

import pytest


# ===================================================================
# Streaming Models
# ===================================================================

@pytest.mark.unit
class TestStreamingModels:
    """Test streaming event models."""

    def test_event_creation_defaults(self):
        """Test functionality: event creation defaults."""
        from codomyrmex.events.streaming.models import Event, EventType
        e = Event()
        assert e.type == EventType.MESSAGE
        assert e.data is None
        assert isinstance(e.id, str)
        assert len(e.id) > 0

    def test_event_creation_with_data(self):
        """Test functionality: event creation with data."""
        from codomyrmex.events.streaming.models import Event, EventType
        e = Event(type=EventType.ERROR, data={"msg": "fail"})
        assert e.type == EventType.ERROR
        assert e.data == {"msg": "fail"}

    def test_event_to_dict(self):
        """Test functionality: event to dict."""
        from codomyrmex.events.streaming.models import Event, EventType
        e = Event(type=EventType.CONNECT, data="hello")
        d = e.to_dict()
        assert d["type"] == "connect"
        assert d["data"] == "hello"
        assert "id" in d
        assert "timestamp" in d

    def test_event_to_sse(self):
        """Test functionality: event to sse."""
        from codomyrmex.events.streaming.models import Event, EventType
        e = Event(id="test-id", type=EventType.MESSAGE, data="payload")
        sse = e.to_sse()
        assert "id: test-id" in sse
        assert "event: message" in sse
        assert "data:" in sse

    def test_event_from_dict(self):
        """Test functionality: event from dict."""
        from codomyrmex.events.streaming.models import Event, EventType
        d = {"id": "abc", "type": "error", "data": 42, "metadata": {"k": "v"}}
        e = Event.from_dict(d)
        assert e.id == "abc"
        assert e.type == EventType.ERROR
        assert e.data == 42
        assert e.metadata == {"k": "v"}

    def test_event_from_dict_defaults(self):
        """Test functionality: event from dict defaults."""
        from codomyrmex.events.streaming.models import Event, EventType
        e = Event.from_dict({})
        assert e.type == EventType.MESSAGE
        assert e.data is None

    def test_event_type_values(self):
        """Test functionality: event type values."""
        from codomyrmex.events.streaming.models import EventType
        assert EventType.MESSAGE.value == "message"
        assert EventType.ERROR.value == "error"
        assert EventType.HEARTBEAT.value == "heartbeat"
        assert EventType.CONNECT.value == "connect"
        assert EventType.DISCONNECT.value == "disconnect"

    def test_subscription_creation(self):
        """Test functionality: subscription creation."""
        from codomyrmex.events.streaming.models import Subscription
        s = Subscription()
        assert s.topic == "*"
        assert s.active is True
        assert s.handler is None

    def test_subscription_cancel(self):
        """Test functionality: subscription cancel."""
        from codomyrmex.events.streaming.models import Subscription
        s = Subscription()
        assert s.active is True
        s.cancel()
        assert s.active is False

    def test_subscription_should_receive_wildcard(self):
        """Test functionality: subscription should receive wildcard."""
        from codomyrmex.events.streaming.models import Event, Subscription
        s = Subscription(topic="*")
        e = Event(data="test")
        assert s.should_receive(e) is True

    def test_subscription_should_receive_inactive(self):
        """Test functionality: subscription should receive inactive."""
        from codomyrmex.events.streaming.models import Event, Subscription
        s = Subscription(topic="*")
        s.cancel()
        e = Event(data="test")
        assert s.should_receive(e) is False

    def test_subscription_should_receive_topic_match(self):
        """Test functionality: subscription should receive topic match."""
        from codomyrmex.events.streaming.models import Event, Subscription
        s = Subscription(topic="alerts")
        e = Event(data="test", metadata={"topic": "alerts"})
        assert s.should_receive(e) is True

    def test_subscription_should_receive_topic_mismatch(self):
        """Test functionality: subscription should receive topic mismatch."""
        from codomyrmex.events.streaming.models import Event, Subscription
        s = Subscription(topic="alerts")
        e = Event(data="test", metadata={"topic": "metrics"})
        assert s.should_receive(e) is False

    def test_subscription_filter_fn(self):
        """Test functionality: subscription filter fn."""
        from codomyrmex.events.streaming.models import Event, Subscription
        s = Subscription(filter_fn=lambda e: e.data == "yes")
        assert s.should_receive(Event(data="yes")) is True
        assert s.should_receive(Event(data="no")) is False

    def test_create_event_helper(self):
        """Test functionality: create event helper."""
        from codomyrmex.events.streaming.models import EventType, create_event
        e = create_event("hello", event_type=EventType.ERROR, source="test")
        assert e.data == "hello"
        assert e.type == EventType.ERROR
        assert e.metadata.get("source") == "test"


# ===================================================================
# Stream Implementations
# ===================================================================

@pytest.mark.unit
class TestInMemoryStream:
    """Test InMemoryStream implementation."""

    def test_publish_and_buffer(self):
        """Test functionality: publish and buffer."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import InMemoryStream
        stream = InMemoryStream()
        e = Event(data="test")
        asyncio.run(stream.publish(e))
        recent = stream.get_recent_events(10)
        assert len(recent) == 1
        assert recent[0].data == "test"

    def test_subscribe_and_receive(self):
        """Test functionality: subscribe and receive."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import InMemoryStream
        stream = InMemoryStream()
        received = []
        asyncio.run(
            stream.subscribe(handler=lambda e: received.append(e))
        )
        asyncio.run(
            stream.publish(Event(data="hello"))
        )
        assert len(received) == 1

    def test_unsubscribe(self):
        """Test functionality: unsubscribe."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import InMemoryStream
        stream = InMemoryStream()
        received = []

        async def run():
            sub = await stream.subscribe(handler=lambda e: received.append(e))
            await stream.publish(Event(data="before"))
            await stream.unsubscribe(sub.id)
            await stream.publish(Event(data="after"))

        asyncio.run(run())
        assert len(received) == 1
        assert received[0].data == "before"

    def test_unsubscribe_unknown_id(self):
        """Test functionality: unsubscribe unknown id."""
        from codomyrmex.events.streaming.stream import InMemoryStream
        stream = InMemoryStream()
        result = asyncio.run(
            stream.unsubscribe("nonexistent")
        )
        assert result is False

    def test_buffer_overflow(self):
        """Test functionality: buffer overflow."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import InMemoryStream
        stream = InMemoryStream()
        stream._buffer_size = 5

        async def run():
            for i in range(10):
                await stream.publish(Event(data=i))

        asyncio.run(run())
        recent = stream.get_recent_events(100)
        assert len(recent) == 5

    def test_get_recent_events_count(self):
        """Test functionality: get recent events count."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import InMemoryStream
        stream = InMemoryStream()

        async def run():
            for i in range(5):
                await stream.publish(Event(data=i))

        asyncio.run(run())
        assert len(stream.get_recent_events(3)) == 3
        assert len(stream.get_recent_events(10)) == 5


@pytest.mark.unit
class TestTopicStream:
    """Test TopicStream implementation."""

    def test_publish_to_topic(self):
        """Test functionality: publish to topic."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import TopicStream
        ts = TopicStream()

        async def run():
            await ts.publish("alerts", Event(data="alert!"))

        asyncio.run(run())
        assert "alerts" in ts.list_topics()
        recent = ts.topic("alerts").get_recent_events(10)
        assert len(recent) == 1

    def test_subscribe_to_topic(self):
        """Test functionality: subscribe to topic."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import TopicStream
        ts = TopicStream()
        received = []

        async def run():
            await ts.subscribe("metrics", handler=lambda e: received.append(e))
            await ts.publish("metrics", Event(data="cpu=50"))
            await ts.publish("alerts", Event(data="fire!"))

        asyncio.run(run())
        # Should only receive the "metrics" event
        assert len(received) == 1
        assert received[0].data == "cpu=50"

    def test_list_topics_empty(self):
        """Test functionality: list topics empty."""
        from codomyrmex.events.streaming.stream import TopicStream
        ts = TopicStream()
        assert ts.list_topics() == []

    def test_topic_creates_on_access(self):
        """Test functionality: topic creates on access."""
        from codomyrmex.events.streaming.stream import TopicStream
        ts = TopicStream()
        stream = ts.topic("new_topic")
        assert stream is not None
        assert "new_topic" in ts.list_topics()


@pytest.mark.unit
class TestBroadcast:
    """Test broadcast helper."""

    def test_broadcast_to_multiple_streams(self):
        """Test functionality: broadcast to multiple streams."""
        from codomyrmex.events.streaming.models import Event
        from codomyrmex.events.streaming.stream import InMemoryStream, broadcast
        s1 = InMemoryStream()
        s2 = InMemoryStream()
        e = Event(data="broadcast_msg")
        asyncio.run(broadcast([s1, s2], e))
        assert len(s1.get_recent_events(10)) == 1
        assert len(s2.get_recent_events(10)) == 1


# ===================================================================
# Core Event Bus
# ===================================================================

@pytest.mark.unit
class TestEventBus:
    """Test the core EventBus."""

    def test_subscribe_and_publish(self):
        """Test functionality: subscribe and publish."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        received = []
        bus.subscribe(
            event_patterns=[EventType.SYSTEM_STARTUP.value],
            handler=lambda e: received.append(e),
            subscriber_id="test-sub"
        )
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        bus.publish(event)
        assert len(received) >= 1

    def test_unsubscribe(self):
        """Test functionality: unsubscribe."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        received = []
        bus.subscribe(
            event_patterns=[EventType.SYSTEM_STARTUP.value],
            handler=lambda e: received.append(e),
            subscriber_id="sub-to-remove"
        )
        bus.unsubscribe("sub-to-remove")
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received) == 0

    def test_emit_typed(self):
        """Test functionality: emit typed."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        received = []
        bus.subscribe(
            event_patterns=[EventType.MODULE_LOAD.value],
            handler=lambda e: received.append(e),
        )
        event = Event(event_type=EventType.MODULE_LOAD, source="test")
        bus.emit_typed(event)
        assert len(received) >= 1

    def test_subscribe_typed(self):
        """Test functionality: subscribe typed."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        received = []
        bus.subscribe_typed(
            event_type=EventType.ANALYSIS_START,
            handler=lambda e: received.append(e),
        )
        bus.publish(Event(event_type=EventType.ANALYSIS_START, source="test"))
        assert len(received) >= 1

    def test_get_stats(self):
        """Test functionality: get stats."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        bus.subscribe(event_patterns=["*"], handler=lambda e: None)
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        stats = bus.get_stats()
        assert "events_published" in stats
        assert stats["events_published"] >= 1
        assert "subscribers" in stats

    def test_reset_stats(self):
        """Test functionality: reset stats."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        bus.reset_stats()
        stats = bus.get_stats()
        assert stats["events_published"] == 0

    def test_multiple_subscribers(self):
        """Test functionality: multiple subscribers."""
        from codomyrmex.events.core.event_bus import EventBus
        from codomyrmex.events.core.event_schema import Event, EventType
        bus = EventBus()
        received_a = []
        received_b = []
        bus.subscribe(event_patterns=["*"], handler=lambda e: received_a.append(e))
        bus.subscribe(event_patterns=["*"], handler=lambda e: received_b.append(e))
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received_a) >= 1
        assert len(received_b) >= 1


# ===================================================================
# Event Schema & Validation
# ===================================================================

@pytest.mark.unit
class TestEventSchema:
    """Test Event and EventSchema."""

    def test_event_creation(self):
        """Test functionality: event creation."""
        from codomyrmex.events.core.event_schema import Event, EventType
        e = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        assert e.event_type == EventType.SYSTEM_STARTUP
        assert e.source == "test"
        assert isinstance(e.event_id, str)

    def test_event_to_dict(self):
        """Test functionality: event to dict."""
        from codomyrmex.events.core.event_schema import Event, EventType
        e = Event(event_type=EventType.SYSTEM_STARTUP, source="test", data={"version": "1.0"})
        d = e.to_dict()
        assert d["event_type"] == "system.startup"
        assert d["source"] == "test"
        assert d["data"]["version"] == "1.0"

    def test_event_to_json(self):
        """Test functionality: event to json."""
        from codomyrmex.events.core.event_schema import Event, EventType
        e = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        j = e.to_json()
        parsed = json.loads(j)
        assert parsed["event_type"] == "system.startup"

    def test_event_from_dict(self):
        """Test functionality: event from dict."""
        from codomyrmex.events.core.event_schema import Event, EventType
        d = {
            "event_type": "system.startup",
            "source": "test",
            "data": {"key": "value"},
        }
        e = Event.from_dict(d)
        assert e.event_type == EventType.SYSTEM_STARTUP
        assert e.source == "test"

    def test_event_from_json(self):
        """Test functionality: event from json."""
        from codomyrmex.events.core.event_schema import Event, EventType
        j = json.dumps({"event_type": "system.error", "source": "test", "data": {}})
        e = Event.from_json(j)
        assert e.event_type == EventType.SYSTEM_ERROR

    def test_event_schema_validate(self):
        """Test functionality: event schema validate."""
        from codomyrmex.events.core.event_schema import Event, EventSchema, EventType
        schema = EventSchema()
        e = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            data={"version": "1.0", "components": ["a"]},
        )
        is_valid, errors = schema.validate_event(e)
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)

    def test_event_schema_register_and_get(self):
        """Test functionality: event schema register and get."""
        from codomyrmex.events.core.event_schema import EventSchema, EventType
        schema = EventSchema()
        custom = {"type": "object", "properties": {"x": {"type": "integer"}}}
        schema.register_event_schema(EventType.CUSTOM, custom)
        retrieved = schema.get_event_schema(EventType.CUSTOM)
        assert retrieved == custom

    def test_event_schema_list_registered(self):
        """Test functionality: event schema list registered."""
        from codomyrmex.events.core.event_schema import EventSchema
        schema = EventSchema()
        registered = schema.list_registered_schemas()
        assert isinstance(registered, list)


# ===================================================================
# Convenience Event Creators
# ===================================================================

@pytest.mark.unit
class TestEventCreators:
    """Test convenience event factory functions."""

    def test_create_system_startup_event(self):
        """Test functionality: create system startup event."""
        from codomyrmex.events.core.event_schema import EventType, create_system_startup_event
        e = create_system_startup_event("1.0", ["a", "b"])
        assert e.event_type == EventType.SYSTEM_STARTUP
        assert e.data["version"] == "1.0"
        assert e.data["components_loaded"] == ["a", "b"]

    def test_create_module_load_event(self):
        """Test functionality: create module load event."""
        from codomyrmex.events.core.event_schema import EventType, create_module_load_event
        e = create_module_load_event("agents", "0.1.0", 0.5)
        assert e.event_type == EventType.MODULE_LOAD
        assert e.data["module_name"] == "agents"

    def test_create_analysis_start_event(self):
        """Test functionality: create analysis start event."""
        from codomyrmex.events.core.event_schema import EventType, create_analysis_start_event
        e = create_analysis_start_event("coverage", "/src")
        assert e.event_type == EventType.ANALYSIS_START

    def test_create_analysis_complete_event(self):
        """Test functionality: create analysis complete event."""
        from codomyrmex.events.core.event_schema import EventType, create_analysis_complete_event
        e = create_analysis_complete_event("lint", "/src", {"issues": 0}, 1.5, True)
        assert e.event_type == EventType.ANALYSIS_COMPLETE
        assert e.data["success"] is True

    def test_create_error_event(self):
        """Test functionality: create error event."""
        from codomyrmex.events.core.event_schema import EventType, create_error_event
        e = create_error_event(EventType.SYSTEM_ERROR, "test", "boom")
        assert e.event_type == EventType.SYSTEM_ERROR
        assert e.data["error_message"] == "boom"

    def test_create_metric_event(self):
        """Test functionality: create metric event."""
        from codomyrmex.events.core.event_schema import EventType, create_metric_event
        e = create_metric_event("cpu_usage", 75.5, metric_type="gauge")
        assert e.event_type == EventType.METRIC_UPDATE
        assert e.data["metric_value"] == 75.5

    def test_create_alert_event(self):
        """Test functionality: create alert event."""
        from codomyrmex.events.core.event_schema import create_alert_event
        e = create_alert_event("high_load", "critical", "CPU at 95%", threshold=90, current_value=95)
        assert e.data["alert_name"] == "high_load"


# ===================================================================
# Notification System
# ===================================================================

@pytest.mark.unit
class TestNotificationRouter:
    """Test NotificationRouter routing logic."""

    def test_default_route(self):
        """Test functionality: default route."""
        from codomyrmex.events.notification.models import Notification, NotificationChannel
        from codomyrmex.events.notification.service import NotificationRouter
        router = NotificationRouter()
        n = Notification(id="1", subject="Test", body="Hello")
        assert router.route(n) == NotificationChannel.CONSOLE

    def test_add_default(self):
        """Test functionality: add default."""
        from codomyrmex.events.notification.models import Notification, NotificationChannel
        from codomyrmex.events.notification.service import NotificationRouter
        router = NotificationRouter()
        router.add_default(NotificationChannel.SLACK)
        n = Notification(id="1", subject="Test", body="Hello")
        assert router.route(n) == NotificationChannel.SLACK

    def test_rule_matching(self):
        """Test functionality: rule matching."""
        from codomyrmex.events.notification.models import (
            Notification, NotificationChannel, NotificationPriority,
        )
        from codomyrmex.events.notification.service import NotificationRouter
        router = NotificationRouter()
        router.add_rule(
            lambda n: n.priority == NotificationPriority.CRITICAL,
            NotificationChannel.SLACK,
        )
        critical = Notification(id="1", subject="Alert", body="Fire", priority=NotificationPriority.CRITICAL)
        normal = Notification(id="2", subject="Info", body="OK")
        assert router.route(critical) == NotificationChannel.SLACK
        assert router.route(normal) == NotificationChannel.CONSOLE


@pytest.mark.unit
class TestNotificationService:
    """Test NotificationService send/broadcast/templates."""

    def test_send_without_provider_fails(self):
        """Test functionality: send without provider fails."""
        from codomyrmex.events.notification.models import Notification, NotificationStatus
        from codomyrmex.events.notification.service import NotificationService
        svc = NotificationService()
        result = svc.send(Notification(id="1", subject="Test", body="Hello"))
        assert result.status == NotificationStatus.FAILED

    def test_send_from_missing_template_fails(self):
        """Test functionality: send from missing template fails."""
        from codomyrmex.events.notification.models import NotificationStatus
        from codomyrmex.events.notification.service import NotificationService
        svc = NotificationService()
        result = svc.send_from_template("nonexistent", id="1")
        assert result.status == NotificationStatus.FAILED

    def test_history_tracking(self):
        """Test functionality: history tracking."""
        from codomyrmex.events.notification.models import Notification
        from codomyrmex.events.notification.service import NotificationService
        svc = NotificationService()
        svc.send(Notification(id="1", subject="Test", body="Hello"))
        assert len(svc.history) == 1

    def test_broadcast_multiple_channels(self):
        """Test functionality: broadcast multiple channels."""
        from codomyrmex.events.notification.models import Notification, NotificationChannel
        from codomyrmex.events.notification.service import NotificationService
        svc = NotificationService()
        n = Notification(id="1", subject="Test", body="Hello")
        results = svc.broadcast(n, [NotificationChannel.CONSOLE, NotificationChannel.SLACK])
        assert len(results) == 2
        assert len(svc.history) == 2
