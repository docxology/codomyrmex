"""Tests for EventLoggingBridge (Stream 6).

Verifies:
- Bridge subscribes to EventBus events
- Structured JSON output captured
- Correlation ID threading
- Scheduler event types from Stream 5
- Start/stop lifecycle
"""

from __future__ import annotations

import logging
from unittest.mock import ANY

import pytest

from codomyrmex.events.core.event_bus import EventBus
from codomyrmex.events.core.event_schema import Event, EventType
from codomyrmex.logging_monitoring.handlers.event_bridge import EventLoggingBridge


# ── Helpers ───────────────────────────────────────────────────────────


def _make_event(event_type: EventType, source: str = "test", **data) -> Event:
    return Event(event_type=event_type, source=source, data=data)


# ── Basic subscription ───────────────────────────────────────────────


class TestBasicSubscription:
    """Verify bridge subscribes to events and captures them."""

    def test_captures_workflow_event(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.WORKFLOW_STARTED])
        bridge.start()

        bus.publish(_make_event(EventType.WORKFLOW_STARTED, total_tasks=5))

        assert bridge.capture_count == 1
        entry = bridge.events_captured[0]
        assert entry["event_type"] == "workflow.started"
        assert entry["data"]["total_tasks"] == 5

    def test_captures_task_event(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.TASK_COMPLETED])
        bridge.start()

        bus.publish(_make_event(
            EventType.TASK_COMPLETED,
            task_name="build",
            execution_time=1.5,
            attempts=2,
        ))

        assert bridge.capture_count == 1
        entry = bridge.events_captured[0]
        assert entry["data"]["task_name"] == "build"

    def test_captures_multiple_event_types(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[
            EventType.TASK_STARTED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
        ])
        bridge.start()

        bus.publish(_make_event(EventType.TASK_STARTED, task="a"))
        bus.publish(_make_event(EventType.TASK_COMPLETED, task="a"))
        bus.publish(_make_event(EventType.TASK_FAILED, task="b"))

        assert bridge.capture_count == 3


# ── Structured output ────────────────────────────────────────────────


class TestStructuredOutput:
    """Verify structured dict format."""

    def test_event_contains_required_fields(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.SYSTEM_STARTUP])
        bridge.start()

        bus.publish(_make_event(EventType.SYSTEM_STARTUP))

        entry = bridge.events_captured[0]
        assert "event_type" in entry
        assert "source" in entry
        assert "timestamp" in entry
        assert "data" in entry

    def test_event_type_is_string_value(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.WORKFLOW_FAILED])
        bridge.start()

        bus.publish(_make_event(EventType.WORKFLOW_FAILED, error="crash"))

        assert bridge.events_captured[0]["event_type"] == "workflow.failed"


# ── Correlation ID ────────────────────────────────────────────────────


class TestCorrelationId:
    """Verify correlation_id threading."""

    def test_correlation_id_extracted_from_data(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.TASK_COMPLETED])
        bridge.start()

        bus.publish(_make_event(
            EventType.TASK_COMPLETED,
            task="build",
            correlation_id="req-abc-123",
        ))

        entry = bridge.events_captured[0]
        assert entry["correlation_id"] == "req-abc-123"

    def test_no_correlation_id_when_absent(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.TASK_STARTED])
        bridge.start()

        bus.publish(_make_event(EventType.TASK_STARTED, task="deploy"))

        entry = bridge.events_captured[0]
        assert "correlation_id" not in entry


# ── Scheduler event types (Stream 5) ─────────────────────────────────


class TestSchedulerEvents:
    """Verify bridge captures Stream 5 scheduler events."""

    def test_captures_job_scheduled(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.JOB_SCHEDULED])
        bridge.start()

        bus.publish(_make_event(EventType.JOB_SCHEDULED, job_id="j1", job_name="backup"))

        assert bridge.capture_count == 1
        assert bridge.events_captured[0]["event_type"] == "job.scheduled"

    def test_captures_job_completed_and_failed(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[
            EventType.JOB_COMPLETED,
            EventType.JOB_FAILED,
        ])
        bridge.start()

        bus.publish(_make_event(EventType.JOB_COMPLETED, job_id="j1"))
        bus.publish(_make_event(EventType.JOB_FAILED, job_id="j2", error="crash"))

        assert bridge.capture_count == 2
        types = [e["event_type"] for e in bridge.events_captured]
        assert "job.completed" in types
        assert "job.failed" in types


# ── Start/stop lifecycle ──────────────────────────────────────────────


class TestLifecycle:
    """Verify start/stop behavior."""

    def test_stop_unsubscribes(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.SYSTEM_STARTUP])
        bridge.start()
        bridge.stop()

        bus.publish(_make_event(EventType.SYSTEM_STARTUP))
        assert bridge.capture_count == 0  # Not captured after stop

    def test_is_active_property(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus)
        assert not bridge.is_active
        bridge.start()
        assert bridge.is_active
        bridge.stop()
        assert not bridge.is_active

    def test_double_start_is_idempotent(self) -> None:
        bus = EventBus()
        bridge = EventLoggingBridge(bus, event_types=[EventType.SYSTEM_STARTUP])
        bridge.start()
        bridge.start()  # No error

        bus.publish(_make_event(EventType.SYSTEM_STARTUP))
        assert bridge.capture_count == 1  # Only 1, not 2
