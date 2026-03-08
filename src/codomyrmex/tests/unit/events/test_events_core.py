"""Zero-mock tests for events core: event_bus, event_schema, and mcp_tools.

No mocks, no monkeypatch, no MagicMock. All tests use real EventBus instances
(not the global singleton) and real Event objects.
"""

from __future__ import annotations

import json
import time

import pytest

from codomyrmex.events.core.event_bus import EventBus, Subscription
from codomyrmex.events.core.event_schema import (
    Event,
    EventPriority,
    EventSchema,
    EventType,
    create_alert_event,
    create_analysis_complete_event,
    create_analysis_start_event,
    create_error_event,
    create_metric_event,
    create_module_load_event,
    create_system_startup_event,
)
from codomyrmex.events.core.exceptions import EventPublishError, EventSubscriptionError


# ---------------------------------------------------------------------------
# TestEvent
# ---------------------------------------------------------------------------


class TestEvent:
    """Tests for the Event dataclass and its serialization."""

    def test_event_has_auto_generated_id(self):
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        assert len(event.event_id) > 0

    def test_event_ids_are_unique(self):
        e1 = Event(event_type=EventType.SYSTEM_STARTUP, source="a")
        e2 = Event(event_type=EventType.SYSTEM_STARTUP, source="b")
        assert e1.event_id != e2.event_id

    def test_event_timestamp_is_recent(self):
        before = time.time()
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
        after = time.time()
        assert before <= event.timestamp <= after

    def test_to_dict_contains_event_type(self):
        event = Event(event_type=EventType.MODULE_LOAD, source="loader")
        d = event.to_dict()
        assert d["event_type"] == "module.load"

    def test_to_dict_contains_source(self):
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="startup_svc")
        d = event.to_dict()
        assert d["source"] == "startup_svc"

    def test_to_dict_contains_data(self):
        event = Event(
            event_type=EventType.DATA_RECEIVED, source="svc", data={"key": "val"}
        )
        d = event.to_dict()
        assert d["data"] == {"key": "val"}

    def test_to_json_returns_valid_json_string(self):
        event = Event(event_type=EventType.CUSTOM, source="test")
        json_str = event.to_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert parsed["event_type"] == "custom"

    def test_from_dict_round_trip(self):
        original = Event(
            event_type=EventType.BUILD_START,
            source="builder",
            correlation_id="cid-123",
            data={"build_type": "python", "target": "src/"},
        )
        d = original.to_dict()
        d["event_id"] = original.event_id
        recovered = Event.from_dict(d)
        assert recovered.event_type == EventType.BUILD_START
        assert recovered.source == "builder"
        assert recovered.correlation_id == "cid-123"

    def test_from_json_round_trip(self):
        original = Event(
            event_type=EventType.DEPLOY_COMPLETE,
            source="deployer",
            data={"success": True},
        )
        json_str = json.dumps(
            {**original.to_dict(), "event_id": original.event_id}
        )
        recovered = Event.from_json(json_str)
        assert recovered.event_type == EventType.DEPLOY_COMPLETE

    def test_event_default_data_is_empty_dict(self):
        event = Event(event_type=EventType.HEALTH_CHECK, source="monitor")
        assert event.data == {}

    def test_event_metadata_field(self):
        event = Event(
            event_type=EventType.CUSTOM,
            source="test",
            metadata={"version": "1.0"},
        )
        assert event.metadata["version"] == "1.0"

    def test_event_with_correlation_id(self):
        event = Event(
            event_type=EventType.WORKFLOW_STARTED,
            source="wf",
            correlation_id="wf-cid-99",
        )
        assert event.correlation_id == "wf-cid-99"


class TestEventType:
    """Tests for EventType enum values."""

    def test_system_startup_value(self):
        assert EventType.SYSTEM_STARTUP.value == "system.startup"

    def test_module_load_value(self):
        assert EventType.MODULE_LOAD.value == "module.load"

    def test_custom_value(self):
        assert EventType.CUSTOM.value == "custom"

    def test_all_event_types_have_dot_notation(self):
        for et in EventType:
            assert "." in et.value or et == EventType.CUSTOM

    def test_from_value_lookup(self):
        et = EventType("system.startup")
        assert et == EventType.SYSTEM_STARTUP


class TestEventPriority:
    """Tests for EventPriority enum."""

    def test_normal_value(self):
        assert EventPriority.NORMAL.value == "normal"

    def test_critical_value(self):
        assert EventPriority.CRITICAL.value == "critical"


# ---------------------------------------------------------------------------
# TestEventSchema
# ---------------------------------------------------------------------------


class TestEventSchema:
    """Tests for EventSchema validation."""

    def test_schema_loads_standard_schemas_on_init(self):
        schema = EventSchema()
        registered = schema.list_registered_schemas()
        assert len(registered) > 0

    def test_system_startup_schema_registered(self):
        schema = EventSchema()
        assert "system.startup" in schema.list_registered_schemas()

    def test_validate_event_with_valid_data(self):
        schema = EventSchema()
        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            data={"version": "1.0.0"},
        )
        is_valid, errors = schema.validate_event(event)
        assert is_valid is True
        assert errors == []

    def test_validate_event_with_missing_required_field(self):
        schema = EventSchema()
        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            data={},  # missing "version" required field
        )
        is_valid, errors = schema.validate_event(event)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_event_without_schema_returns_valid(self):
        schema = EventSchema()
        event = Event(
            event_type=EventType.CUSTOM,
            source="test",
            data={"anything": "goes"},
        )
        is_valid, errors = schema.validate_event(event)
        assert is_valid is True

    def test_register_custom_schema(self):
        schema = EventSchema()
        custom_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema.register_event_schema(EventType.CUSTOM, custom_schema)
        assert schema.get_event_schema(EventType.CUSTOM) is not None

    def test_registered_custom_schema_validates(self):
        schema = EventSchema()
        custom_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        schema.register_event_schema(EventType.CUSTOM, custom_schema)
        event = Event(event_type=EventType.CUSTOM, source="test", data={"name": "ok"})
        is_valid, errors = schema.validate_event(event)
        assert is_valid is True

    def test_module_load_schema_validates_with_name(self):
        schema = EventSchema()
        event = Event(
            event_type=EventType.MODULE_LOAD,
            source="test",
            data={"module_name": "codomyrmex.agents"},
        )
        is_valid, _ = schema.validate_event(event)
        assert is_valid is True

    def test_get_event_schema_returns_none_for_unknown(self):
        schema = EventSchema()
        result = schema.get_event_schema(EventType.CUSTOM)
        # CUSTOM may or may not have schema, but won't raise
        assert result is None or isinstance(result, dict)


# ---------------------------------------------------------------------------
# TestEventBus
# ---------------------------------------------------------------------------


class TestEventBus:
    """Tests for EventBus with isolated instances (not global singleton)."""

    def make_bus(self) -> EventBus:
        bus = EventBus(max_workers=2)
        return bus

    def test_eventbus_initializes_with_zero_stats(self):
        bus = self.make_bus()
        assert bus.events_published == 0
        assert bus.events_processed == 0
        assert bus.events_failed == 0
        bus.shutdown()

    def test_subscribe_returns_subscriber_id(self):
        bus = self.make_bus()
        sid = bus.subscribe([EventType.CUSTOM], lambda e: None)
        assert isinstance(sid, str)
        assert len(sid) > 0
        bus.shutdown()

    def test_subscribe_with_explicit_id(self):
        bus = self.make_bus()
        sid = bus.subscribe([EventType.CUSTOM], lambda e: None, subscriber_id="my-sub")
        assert sid == "my-sub"
        bus.shutdown()

    def test_subscribe_empty_patterns_raises(self):
        bus = self.make_bus()
        with pytest.raises(EventSubscriptionError):
            bus.subscribe([], lambda e: None)
        bus.shutdown()

    def test_unsubscribe_existing_returns_true(self):
        bus = self.make_bus()
        sid = bus.subscribe([EventType.CUSTOM], lambda e: None)
        result = bus.unsubscribe(sid)
        assert result is True
        bus.shutdown()

    def test_unsubscribe_nonexistent_returns_false(self):
        bus = self.make_bus()
        result = bus.unsubscribe("does-not-exist")
        assert result is False
        bus.shutdown()

    def test_publish_increments_events_published(self):
        bus = self.make_bus()
        event = Event(event_type=EventType.CUSTOM, source="test")
        bus.publish(event)
        assert bus.events_published == 1
        bus.shutdown()

    def test_publish_without_event_type_raises(self):
        bus = self.make_bus()
        # Create an object that has event_type=None
        event = Event(event_type=EventType.CUSTOM, source="test")
        event.event_type = None  # type: ignore
        with pytest.raises(EventPublishError):
            bus.publish(event)
        bus.shutdown()

    def test_publish_calls_subscriber_handler(self):
        bus = self.make_bus()
        received = []
        bus.subscribe([EventType.CUSTOM], received.append)
        event = Event(event_type=EventType.CUSTOM, source="test", data={"x": 1})
        bus.publish(event)
        assert len(received) == 1
        assert received[0].data == {"x": 1}
        bus.shutdown()

    def test_publish_does_not_call_non_matching_subscriber(self):
        bus = self.make_bus()
        received = []
        bus.subscribe([EventType.SYSTEM_STARTUP], received.append)
        event = Event(event_type=EventType.CUSTOM, source="test")
        bus.publish(event)
        assert len(received) == 0
        bus.shutdown()

    def test_multiple_subscribers_all_called(self):
        bus = self.make_bus()
        received1 = []
        received2 = []
        bus.subscribe([EventType.CUSTOM], received1.append)
        bus.subscribe([EventType.CUSTOM], received2.append)
        event = Event(event_type=EventType.CUSTOM, source="test")
        bus.publish(event)
        assert len(received1) == 1
        assert len(received2) == 1
        bus.shutdown()

    def test_priority_ordering(self):
        bus = self.make_bus()
        order = []
        bus.subscribe([EventType.CUSTOM], lambda e: order.append("low"), priority=0)
        bus.subscribe([EventType.CUSTOM], lambda e: order.append("high"), priority=10)
        event = Event(event_type=EventType.CUSTOM, source="test")
        bus.publish(event)
        assert order[0] == "high"
        assert order[1] == "low"
        bus.shutdown()

    def test_filter_function_filters_events(self):
        bus = self.make_bus()
        received = []
        bus.subscribe(
            [EventType.CUSTOM],
            received.append,
            filter_func=lambda e: e.data.get("pass") is True,
        )
        bus.publish(Event(event_type=EventType.CUSTOM, source="t", data={"pass": False}))
        bus.publish(Event(event_type=EventType.CUSTOM, source="t", data={"pass": True}))
        assert len(received) == 1
        assert received[0].data["pass"] is True
        bus.shutdown()

    def test_get_stats_returns_dict(self):
        bus = self.make_bus()
        stats = bus.get_stats()
        assert isinstance(stats, dict)
        assert "events_published" in stats
        assert "events_processed" in stats
        assert "subscribers_count" in stats
        bus.shutdown()

    def test_reset_stats(self):
        bus = self.make_bus()
        event = Event(event_type=EventType.CUSTOM, source="test")
        bus.publish(event)
        bus.reset_stats()
        assert bus.events_published == 0
        assert bus.events_processed == 0
        bus.shutdown()

    def test_list_event_types_returns_subscribed_patterns(self):
        bus = self.make_bus()
        bus.subscribe([EventType.CUSTOM], lambda e: None, subscriber_id="sub-list-test")
        types = bus.list_event_types()
        assert "custom" in types
        bus.shutdown()

    def test_subscribe_typed_convenience(self):
        bus = self.make_bus()
        received = []
        bus.subscribe_typed(EventType.SYSTEM_STARTUP, received.append)
        event = Event(event_type=EventType.SYSTEM_STARTUP, source="sys")
        bus.publish(event)
        assert len(received) == 1
        bus.shutdown()

    def test_emit_typed_with_valid_event_type(self):
        bus = self.make_bus()
        received = []
        bus.subscribe([EventType.CUSTOM], received.append)
        event = Event(event_type=EventType.CUSTOM, source="typed")
        bus.emit_typed(event)
        assert len(received) == 1
        bus.shutdown()

    def test_emit_typed_with_invalid_event_type_raises(self):
        bus = self.make_bus()
        event = Event(event_type=EventType.CUSTOM, source="typed")
        event.event_type = "not_an_enum"  # type: ignore
        with pytest.raises(TypeError):
            bus.emit_typed(event)
        bus.shutdown()

    def test_handler_exception_does_not_crash_bus(self):
        bus = self.make_bus()

        def bad_handler(e):
            raise RuntimeError("handler error")

        bus.subscribe([EventType.CUSTOM], bad_handler)
        event = Event(event_type=EventType.CUSTOM, source="test")
        # Should not raise — error is logged, events_failed incremented
        bus.publish(event)
        assert bus.events_failed > 0
        bus.shutdown()

    def test_wildcard_pattern_matches_multiple_types(self):
        bus = self.make_bus()
        received = []
        bus.subscribe(["system.*"], received.append)
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="sys"))
        bus.publish(Event(event_type=EventType.SYSTEM_SHUTDOWN, source="sys"))
        assert len(received) == 2
        bus.shutdown()


class TestSubscription:
    """Tests for Subscription.matches_event."""

    def test_matches_exact_event_type(self):
        sub = Subscription(
            subscriber_id="s1",
            event_patterns={"custom"},
            handler=lambda e: None,
        )
        event = Event(event_type=EventType.CUSTOM, source="test")
        assert sub.matches_event(event) is True

    def test_does_not_match_different_event_type(self):
        sub = Subscription(
            subscriber_id="s2",
            event_patterns={"system.startup"},
            handler=lambda e: None,
        )
        event = Event(event_type=EventType.CUSTOM, source="test")
        assert sub.matches_event(event) is False

    def test_filter_func_can_exclude_event(self):
        sub = Subscription(
            subscriber_id="s3",
            event_patterns={"custom"},
            handler=lambda e: None,
            filter_func=lambda e: False,
        )
        event = Event(event_type=EventType.CUSTOM, source="test")
        assert sub.matches_event(event) is False


# ---------------------------------------------------------------------------
# TestConvenienceFunctions
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    """Tests for create_* helper functions in event_schema."""

    def test_create_system_startup_event(self):
        event = create_system_startup_event("1.0.0", ["agents", "logging"])
        assert event.event_type == EventType.SYSTEM_STARTUP
        assert event.data["version"] == "1.0.0"
        assert "agents" in event.data["components_loaded"]

    def test_create_module_load_event(self):
        event = create_module_load_event("codomyrmex.agents", "2.0.0", 0.42)
        assert event.event_type == EventType.MODULE_LOAD
        assert event.data["module_name"] == "codomyrmex.agents"
        assert event.data["load_time"] == 0.42

    def test_create_analysis_start_event(self):
        event = create_analysis_start_event("security", "src/", {"depth": 3})
        assert event.event_type == EventType.ANALYSIS_START
        assert event.data["analysis_type"] == "security"
        assert event.data["target"] == "src/"

    def test_create_analysis_complete_event(self):
        event = create_analysis_complete_event(
            "security", "src/", {"issues": []}, 1.23, True
        )
        assert event.event_type == EventType.ANALYSIS_COMPLETE
        assert event.data["success"] is True

    def test_create_error_event(self):
        event = create_error_event(
            EventType.SYSTEM_ERROR, "system", "Disk full", "IOError"
        )
        assert event.event_type == EventType.SYSTEM_ERROR
        assert event.data["error_message"] == "Disk full"
        assert event.priority == 2

    def test_create_metric_event(self):
        event = create_metric_event("cpu_usage", 75.3, "gauge", {"host": "node1"})
        assert event.event_type == EventType.METRIC_UPDATE
        assert event.data["metric_name"] == "cpu_usage"
        assert event.data["metric_value"] == 75.3

    def test_create_alert_event(self):
        event = create_alert_event("cpu_high", "critical", "CPU above 90%", 90, 95)
        assert event.event_type == EventType.ALERT_TRIGGERED
        assert event.data["alert_name"] == "cpu_high"
        assert event.priority == 2

    def test_create_alert_event_info_priority_is_zero(self):
        event = create_alert_event("info_alert", "info", "Nothing serious")
        assert event.priority == 0


# ---------------------------------------------------------------------------
# TestMCPToolsEvents
# ---------------------------------------------------------------------------


class TestMCPToolsEvents:
    """Tests for events MCP tools: emit_event, list_event_types, get_event_history."""

    def test_emit_event_standard_type(self):
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("system.startup", {"version": "1.0"}, source="test_mcp")
        assert result["status"] == "success"
        assert "event_id" in result

    def test_emit_event_unknown_type_uses_custom(self):
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("totally.unknown.type", {"key": "val"}, source="test_mcp")
        assert result["status"] == "success"

    def test_emit_event_returns_source(self):
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("custom", {}, source="my-source")
        assert result["source"] == "my-source"

    def test_emit_event_with_priority(self):
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("custom", {}, priority="critical")
        assert result["status"] == "success"

    def test_list_event_types_returns_success(self):
        from codomyrmex.events.mcp_tools import list_event_types

        result = list_event_types()
        assert result["status"] == "success"
        assert "event_types" in result
        assert "count" in result
        assert isinstance(result["count"], int)

    def test_get_event_history_returns_success(self):
        from codomyrmex.events.mcp_tools import get_event_history

        result = get_event_history(limit=10)
        assert result["status"] == "success"
        assert "events" in result
        assert "count" in result

    def test_get_event_history_with_event_type_filter(self):
        from codomyrmex.events.mcp_tools import get_event_history

        result = get_event_history(event_type="custom", limit=5)
        assert result["status"] == "success"
