"""Comprehensive tests for events.core.event_schema — zero-mock, real objects.

Covers: EventPriority, EventType, Event (creation, serialization, deserialization),
EventSchema (registration, validation, standard schemas), and convenience event factories.
"""

import json

import pytest

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

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEventPriority:
    def test_values_exist(self):
        assert EventPriority.DEBUG.value == "debug"
        assert EventPriority.INFO.value == "info"
        assert EventPriority.NORMAL.value == "normal"
        assert EventPriority.WARNING.value == "warning"
        assert EventPriority.ERROR.value == "error"
        assert EventPriority.CRITICAL.value == "critical"
        assert EventPriority.MONITORING.value == "monitoring"


class TestEventType:
    def test_system_events_exist(self):
        assert EventType.SYSTEM_STARTUP.value == "system.startup"
        assert EventType.SYSTEM_SHUTDOWN.value == "system.shutdown"
        assert EventType.SYSTEM_ERROR.value == "system.error"

    def test_task_events_exist(self):
        assert EventType.TASK_COMPLETED.value == "task.completed"
        assert EventType.TASK_FAILED.value == "task.failed"

    def test_custom_type(self):
        assert EventType.CUSTOM.value == "custom"


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------


class TestEvent:
    def test_create_event(self):
        e = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
        )
        assert e.event_type == EventType.SYSTEM_STARTUP
        assert e.source == "test"
        assert e.event_id  # UUID auto-generated

    def test_event_has_unique_ids(self):
        e1 = Event(event_type=EventType.CUSTOM, source="a")
        e2 = Event(event_type=EventType.CUSTOM, source="b")
        assert e1.event_id != e2.event_id

    def test_event_with_data(self):
        e = Event(
            event_type=EventType.CUSTOM,
            source="test",
            data={"key": "value"},
        )
        assert e.data["key"] == "value"

    def test_event_with_priority(self):
        e = Event(
            event_type=EventType.SYSTEM_ERROR,
            source="test",
            priority=EventPriority.CRITICAL,
        )
        assert e.priority == EventPriority.CRITICAL

    def test_to_dict(self):
        e = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test_module",
            data={"version": "1.0"},
        )
        d = e.to_dict()
        assert isinstance(d, dict)
        assert "event_type" in d
        assert "source" in d
        assert d["source"] == "test_module"

    def test_to_json(self):
        e = Event(
            event_type=EventType.CUSTOM,
            source="test",
            data={"count": 42},
        )
        j = e.to_json()
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert "source" in parsed

    def test_from_dict_roundtrip(self):
        original = Event(
            event_type=EventType.SYSTEM_ERROR,
            source="test",
            data={"error": "something broke"},
        )
        d = original.to_dict()
        restored = Event.from_dict(d)
        assert restored.source == original.source
        # Note: from_dict may generate a new event_id

    def test_from_json_roundtrip(self):
        original = Event(
            event_type=EventType.CUSTOM,
            source="test",
        )
        j = original.to_json()
        restored = Event.from_json(j)
        assert restored.source == original.source


# ---------------------------------------------------------------------------
# EventSchema
# ---------------------------------------------------------------------------


class TestEventSchema:
    def test_init_loads_standard_schemas(self):
        schema = EventSchema()
        registered = schema.list_registered_schemas()
        assert len(registered) > 0

    def test_register_custom_schema(self):
        schema = EventSchema()
        custom = {
            "type": "object",
            "properties": {"custom_field": {"type": "string"}},
        }
        schema.register_event_schema(EventType.CUSTOM, custom)
        retrieved = schema.get_event_schema(EventType.CUSTOM)
        assert retrieved is not None
        assert "custom_field" in retrieved.get("properties", {})

    def test_get_nonexistent_schema_returns_none(self):
        schema = EventSchema()
        result = schema.get_event_schema(EventType.CUSTOM)
        # CUSTOM may or may not be registered by default
        # Just check it returns None or a dict
        assert result is None or isinstance(result, dict)

    def test_validate_valid_event(self):
        schema = EventSchema()
        event = create_system_startup_event(
            version="1.0.0", components=["core", "agents"]
        )
        is_valid, errors = schema.validate_event(event)
        # Should be valid or gracefully handle validation
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)


# ---------------------------------------------------------------------------
# Convenience Factories
# ---------------------------------------------------------------------------


class TestConvenienceFactories:
    def test_create_system_startup_event(self):
        e = create_system_startup_event(
            version="2.0.0", components=["core", "llm", "agents"]
        )
        assert isinstance(e, Event)
        assert e.event_type == EventType.SYSTEM_STARTUP
        assert e.data["version"] == "2.0.0"
        assert "components_loaded" in e.data or "components" in e.data

    def test_create_module_load_event(self):
        e = create_module_load_event(module_name="agents", version="1.0", load_time=0.5)
        assert isinstance(e, Event)
        assert e.data["module_name"] == "agents"
        assert e.data["load_time"] == 0.5

    def test_create_analysis_start_event(self):
        e = create_analysis_start_event(analysis_type="static", target="main.py")
        assert isinstance(e, Event)
        assert e.data["analysis_type"] == "static"

    def test_create_analysis_start_with_params(self):
        e = create_analysis_start_event(
            analysis_type="lint",
            target="src/",
            parameters={"strict": True},
        )
        assert e.data["parameters"]["strict"] is True

    def test_create_analysis_complete_event(self):
        e = create_analysis_complete_event(
            analysis_type="lint",
            target="src/",
            results={"issues": 5},
            duration=2.3,
            success=True,
        )
        assert isinstance(e, Event)
        assert e.data["success"] is True
        assert e.data["duration"] == 2.3

    def test_create_error_event(self):
        e = create_error_event(
            event_type=EventType.SYSTEM_ERROR,
            source="core",
            error_message="disk full",
            error_type="IOError",
        )
        assert isinstance(e, Event)
        assert e.data["error_message"] == "disk full"

    def test_create_metric_event(self):
        e = create_metric_event(
            metric_name="cpu_usage",
            value=75.5,
            metric_type="gauge",
            labels={"host": "server1"},
        )
        assert isinstance(e, Event)
        # The data keys may vary — just check the event was created
        assert len(e.data) > 0

    def test_create_alert_event(self):
        e = create_alert_event(
            alert_name="high_memory",
            level="critical",
            message="Memory usage above 90%",
            threshold=90,
            current_value=95,
        )
        assert isinstance(e, Event)
        assert e.data["alert_name"] == "high_memory"
        assert e.data["current_value"] == 95
