"""Tests for EventBus ↔ Orchestrator integration.

Covers emit_typed/subscribe_typed, Workflow lifecycle events, and
orchestrator_events factory functions.  All tests use real objects — zero mocks.
"""

import asyncio

import pytest

from codomyrmex.events.core.event_bus import EventBus
from codomyrmex.events.core.event_schema import Event, EventType
from codomyrmex.orchestrator.observability.orchestrator_events import (
    task_completed,
    task_failed,
    task_retrying,
    task_started,
    workflow_completed,
    workflow_failed,
    workflow_started,
)
from codomyrmex.orchestrator.workflow import Task, Workflow


# ── EventBus.emit_typed / subscribe_typed ─────────────────────────────


class TestEventBusTyped:
    """Test suite for EventBusTyped."""

    def test_emit_typed_dispatches(self):
        """Test functionality: emit typed dispatches."""
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe_typed(EventType.TASK_STARTED, received.append)

        event = Event(event_type=EventType.TASK_STARTED, source="test", data={})
        bus.emit_typed(event)
        assert len(received) == 1
        assert received[0].event_type is EventType.TASK_STARTED

    def test_emit_typed_rejects_invalid_type(self):
        """Test functionality: emit typed rejects invalid type."""
        bus = EventBus()
        bad_event = Event.__new__(Event)
        bad_event.event_type = "not_an_enum"
        bad_event.source = "test"
        bad_event.data = {}
        with pytest.raises(TypeError, match="EventType"):
            bus.emit_typed(bad_event)

    def test_subscribe_typed_single_event(self):
        """Test functionality: subscribe typed single event."""
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe_typed(EventType.TASK_COMPLETED, received.append)

        # Should receive TASK_COMPLETED but not TASK_STARTED
        bus.publish(Event(event_type=EventType.TASK_COMPLETED, source="t", data={}))
        bus.publish(Event(event_type=EventType.TASK_STARTED, source="t", data={}))
        assert len(received) == 1

    def test_subscribe_typed_returns_subscriber_id(self):
        """Test functionality: subscribe typed returns subscriber id."""
        bus = EventBus()
        sid = bus.subscribe_typed(EventType.TASK_FAILED, lambda e: None, subscriber_id="my_sub")
        assert sid == "my_sub"

    def test_emit_typed_multiple_subscribers(self):
        """Test functionality: emit typed multiple subscribers."""
        bus = EventBus()
        a: list[Event] = []
        b: list[Event] = []
        bus.subscribe_typed(EventType.WORKFLOW_STARTED, a.append)
        bus.subscribe_typed(EventType.WORKFLOW_STARTED, b.append)

        event = Event(event_type=EventType.WORKFLOW_STARTED, source="t", data={})
        bus.emit_typed(event)
        assert len(a) == 1
        assert len(b) == 1


# ── Orchestrator event factory functions ──────────────────────────────


class TestOrchestratorEventFactories:
    """Test suite for OrchestratorEventFactories."""

    def test_workflow_started(self):
        """Test functionality: workflow started."""
        e = workflow_started("build", 5)
        assert e.event_type is EventType.WORKFLOW_STARTED
        assert e.data["total_tasks"] == 5

    def test_workflow_completed(self):
        """Test functionality: workflow completed."""
        e = workflow_completed("build", completed=4, failed=1, skipped=0, elapsed=2.5)
        assert e.event_type is EventType.WORKFLOW_COMPLETED
        assert e.data["success"] is False

    def test_workflow_failed(self):
        """Test functionality: workflow failed."""
        e = workflow_failed("build", "kaboom")
        assert e.event_type is EventType.WORKFLOW_FAILED
        assert e.data["error_message"] == "kaboom"

    def test_task_started(self):
        """Test functionality: task started."""
        e = task_started("build", "compile")
        assert e.data["task_name"] == "compile"

    def test_task_completed(self):
        """Test functionality: task completed."""
        e = task_completed("build", "compile", execution_time=1.2, attempts=1)
        assert e.event_type is EventType.TASK_COMPLETED
        assert e.data["execution_time"] == 1.2

    def test_task_failed(self):
        """Test functionality: task failed."""
        e = task_failed("build", "compile", "syntax error")
        assert e.data["error_message"] == "syntax error"

    def test_task_retrying(self):
        """Test functionality: task retrying."""
        e = task_retrying("build", "compile", attempt=2, delay=1.0, error="timeout")
        assert e.event_type is EventType.TASK_RETRYING
        assert e.data["attempt"] == 2


# ── Workflow.run() event emission (async) ─────────────────────────────


class TestWorkflowEventEmission:
    """Test suite for WorkflowEventEmission."""

    @pytest.mark.asyncio
    async def test_workflow_emits_lifecycle_events(self):
        """Workflow.run() publishes events to EventBus when one is wired."""
        bus = EventBus()
        received: list[Event] = []

        bus.subscribe([EventType.WORKFLOW_STARTED], received.append)
        bus.subscribe([EventType.TASK_STARTED], received.append)
        bus.subscribe([EventType.TASK_COMPLETED], received.append)
        bus.subscribe([EventType.WORKFLOW_COMPLETED], received.append)

        wf = Workflow("test_wf", event_bus=bus)
        wf.add_task("step_a", lambda: "a_result")
        wf.add_task("step_b", lambda: "b_result", dependencies=["step_a"])
        await wf.run()

        event_types = [e.event_type for e in received]
        assert EventType.WORKFLOW_STARTED in event_types
        assert EventType.TASK_STARTED in event_types
        assert EventType.TASK_COMPLETED in event_types
        assert EventType.WORKFLOW_COMPLETED in event_types

    @pytest.mark.asyncio
    async def test_workflow_emits_failure_event(self):
        """When a task fails, a TASK_FAILED event is emitted."""
        bus = EventBus()
        received: list[Event] = []
        bus.subscribe([EventType.TASK_FAILED], received.append)

        def boom():
            raise RuntimeError("intentional")

        wf = Workflow("fail_wf", event_bus=bus, fail_fast=True)
        wf.add_task("bad_step", boom)

        try:
            await wf.run()
        except Exception:
            pass

        failed_events = [e for e in received if e.event_type is EventType.TASK_FAILED]
        assert len(failed_events) >= 1

    @pytest.mark.asyncio
    async def test_workflow_without_event_bus_succeeds(self):
        """Workflow still works fine without an event bus (backward compat)."""
        wf = Workflow("no_bus_wf")
        wf.add_task("ok", lambda: 42)
        results = await wf.run()
        # Workflow.run() returns dict[str, TaskResult] — the task returned 42
        ok_result = results["ok"]
        # TaskResult wraps the value; if it's a TaskResult check .success,
        # otherwise the workflow returns the raw value.
        if hasattr(ok_result, "success"):
            assert ok_result.success is True
        else:
            assert ok_result == 42
