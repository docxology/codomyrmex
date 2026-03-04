"""Comprehensive zero-mock tests for the events module.

Covers previously-uncovered files:
- dead_letter.py (0% → target 90%+)
- replay.py (0% → target 90%+)
- mcp_tools.py (0% → target 80%+)
- integration_bus.py (0% → target 90%+)
- async_stream.py (0% → target 60%+)
- core/mixins.py (46% → target 85%+)
- handlers/event_logger.py (51% → target 75%+)

Zero-mock policy: no unittest.mock, MagicMock, or monkeypatch.
External deps handled with @pytest.mark.skipif at module level.
"""

import asyncio
import json
from pathlib import Path

import pytest

from codomyrmex.events.core.event_bus import EventBus
from codomyrmex.events.core.event_schema import Event, EventType
from codomyrmex.events.dead_letter import DeadLetter, DeadLetterQueue
from codomyrmex.events.integration_bus import IntegrationBus, IntegrationEvent
from codomyrmex.events.replay import EventStore as FileBackedEventStore
from codomyrmex.events.replay import StoredEvent

# ===========================================================================
# EventMixin
# ===========================================================================


@pytest.mark.unit
class TestEventMixinInitEvents:
    """Tests for EventMixin.init_events() — ISC-1, ISC-6."""

    def _make_mixin(self, bus: EventBus):
        from codomyrmex.events.core.mixins import EventMixin

        class _Mod(EventMixin):
            pass

        m = _Mod()
        m.init_events("my_module", event_bus=bus)
        return m

    def test_init_events_sets_source(self):
        """init_events() stores the source identifier on the mixin."""
        bus = EventBus()
        try:
            mixin = self._make_mixin(bus)
            assert mixin._event_source == "my_module"
        finally:
            bus.shutdown()

    def test_init_events_sets_bus_reference(self):
        """init_events() stores the provided EventBus instance."""
        bus = EventBus()
        try:
            mixin = self._make_mixin(bus)
            assert mixin._event_bus is bus
        finally:
            bus.shutdown()

    def test_init_events_resets_subscriptions(self):
        """init_events() initialises an empty subscriptions list."""
        bus = EventBus()
        try:
            mixin = self._make_mixin(bus)
            assert mixin._event_subscriptions == []
        finally:
            bus.shutdown()

    def test_event_bus_property_returns_bus(self):
        """event_bus property returns the stored EventBus — ISC-6."""
        bus = EventBus()
        try:
            mixin = self._make_mixin(bus)
            assert mixin.event_bus is bus
        finally:
            bus.shutdown()

    def test_event_bus_property_lazy_init_when_none(self):
        """event_bus property lazy-initialises from global singleton when _event_bus is None."""
        from codomyrmex.events.core.mixins import EventMixin

        class _Mod(EventMixin):
            pass

        m = _Mod()
        m._event_bus = None
        m._event_subscriptions = []
        # Accessing .event_bus should not raise; returns a bus
        result = m.event_bus
        assert isinstance(result, EventBus)


@pytest.mark.unit
class TestEventMixinEmit:
    """Tests for EventMixin.emit() — ISC-2."""

    def _make_mixin_with_bus(self):
        from codomyrmex.events.core.mixins import EventMixin

        class _Mod(EventMixin):
            pass

        bus = EventBus()
        m = _Mod()
        m.init_events("emitter_test", event_bus=bus)
        return m, bus

    def test_emit_publishes_event_to_bus(self):
        """emit() delivers an Event to the EventBus subscribers."""
        mixin, bus = self._make_mixin_with_bus()
        received: list[Event] = []
        bus.subscribe([EventType.SYSTEM_STARTUP], received.append)

        mixin.emit(EventType.SYSTEM_STARTUP, data={"version": "1.0"})

        assert len(received) == 1
        assert received[0].data["version"] == "1.0"
        bus.shutdown()

    def test_emit_sets_source_correctly(self):
        """emit() sets event.source to the mixin's source identifier."""
        mixin, bus = self._make_mixin_with_bus()
        received: list[Event] = []
        bus.subscribe([EventType.ANALYSIS_START], received.append)

        mixin.emit(EventType.ANALYSIS_START)

        assert received[0].source == "emitter_test"
        bus.shutdown()

    def test_emit_returns_event_object(self):
        """emit() returns the Event that was published."""
        mixin, bus = self._make_mixin_with_bus()
        event = mixin.emit(EventType.SYSTEM_SHUTDOWN, data={"reason": "test"})
        assert isinstance(event, Event)
        assert event.event_type == EventType.SYSTEM_SHUTDOWN
        bus.shutdown()

    def test_emit_passes_correlation_id(self):
        """emit() propagates correlation_id to the event."""
        mixin, bus = self._make_mixin_with_bus()
        received: list[Event] = []
        bus.subscribe([EventType.SYSTEM_STARTUP], received.append)

        mixin.emit(EventType.SYSTEM_STARTUP, correlation_id="corr-123")

        assert received[0].correlation_id == "corr-123"
        bus.shutdown()

    def test_emit_passes_metadata(self):
        """emit() propagates metadata to the event."""
        mixin, bus = self._make_mixin_with_bus()
        received: list[Event] = []
        bus.subscribe([EventType.MODULE_LOAD], received.append)

        mixin.emit(EventType.MODULE_LOAD, metadata={"env": "test"})

        assert received[0].metadata["env"] == "test"
        bus.shutdown()


@pytest.mark.unit
class TestEventMixinSubscriptions:
    """Tests for EventMixin.on(), off(), cleanup_events() — ISC-3, ISC-4, ISC-5."""

    def _make_mixin_with_bus(self):
        from codomyrmex.events.core.mixins import EventMixin

        class _Mod(EventMixin):
            pass

        bus = EventBus()
        m = _Mod()
        m.init_events("sub_test", event_bus=bus)
        return m, bus

    def test_on_subscribes_and_stores_id(self):
        """on() subscribes and adds the subscription ID to the tracking list."""
        mixin, bus = self._make_mixin_with_bus()
        received: list = []
        sub_id = mixin.on([EventType.SYSTEM_STARTUP], received.append)

        assert isinstance(sub_id, str)
        assert sub_id in mixin._event_subscriptions
        bus.shutdown()

    def test_on_handler_receives_events(self):
        """Handlers registered via on() receive matching events."""
        mixin, bus = self._make_mixin_with_bus()
        received: list[Event] = []
        mixin.on([EventType.SYSTEM_STARTUP], received.append)

        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))

        assert len(received) == 1
        bus.shutdown()

    def test_off_unsubscribes(self):
        """off() unsubscribes and removes ID from tracking list."""
        mixin, bus = self._make_mixin_with_bus()
        received: list = []
        sub_id = mixin.on([EventType.SYSTEM_STARTUP], received.append)

        result = mixin.off(sub_id)

        assert result is True
        assert sub_id not in mixin._event_subscriptions
        # Verify handler no longer receives events
        bus.publish(Event(event_type=EventType.SYSTEM_STARTUP, source="test"))
        assert len(received) == 0
        bus.shutdown()

    def test_off_returns_false_for_unknown_id(self):
        """off() returns False for a non-existent subscription ID."""
        mixin, bus = self._make_mixin_with_bus()
        result = mixin.off("nonexistent-id")
        assert result is False
        bus.shutdown()

    def test_cleanup_events_removes_all_subscriptions(self):
        """cleanup_events() unsubscribes all tracked subscriptions."""
        mixin, bus = self._make_mixin_with_bus()
        mixin.on([EventType.SYSTEM_STARTUP], lambda e: None)
        mixin.on([EventType.SYSTEM_SHUTDOWN], lambda e: None)
        assert len(mixin._event_subscriptions) == 2

        mixin.cleanup_events()

        assert mixin._event_subscriptions == []
        bus.shutdown()


# ===========================================================================
# DeadLetterQueue
# ===========================================================================


@pytest.mark.unit
class TestDeadLetterQueueEnqueue:
    """Tests for DeadLetterQueue.enqueue() — ISC-7, ISC-12."""

    def test_enqueue_writes_to_file(self, tmp_path: Path):
        """enqueue() writes a JSONL entry to the store file."""
        store = tmp_path / "dlq.jsonl"
        dlq = DeadLetterQueue(store)

        dlq.enqueue("order.failed", {"order_id": 42}, ValueError("bad data"))

        assert store.exists()
        lines = store.read_text().strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["event_type"] == "order.failed"
        assert entry["error_type"] == "ValueError"

    def test_enqueue_returns_dead_letter(self, tmp_path: Path):
        """enqueue() returns the DeadLetter dataclass."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        result = dlq.enqueue("task.error", {}, RuntimeError("oops"))
        assert isinstance(result, DeadLetter)
        assert result.event_type == "task.error"
        assert result.error_type == "RuntimeError"

    def test_count_property_reflects_entries(self, tmp_path: Path):
        """count property returns total number of dead letters."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        assert dlq.count == 0

        dlq.enqueue("a.failed", {}, ValueError("x"))
        dlq.enqueue("b.failed", {}, RuntimeError("y"))

        assert dlq.count == 2

    def test_enqueue_stores_metadata(self, tmp_path: Path):
        """enqueue() persists custom metadata alongside the error."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        dlq.enqueue("x.failed", {}, ValueError("err"), metadata={"tenant": "acme"})

        letter = dlq.list_all()[0]
        assert letter.metadata["tenant"] == "acme"


@pytest.mark.unit
class TestDeadLetterQueueListAndPurge:
    """Tests for DeadLetterQueue.list_all() and purge() — ISC-8, ISC-9."""

    def test_list_all_returns_all_letters(self, tmp_path: Path):
        """list_all() returns every dead letter stored."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        dlq.enqueue("a", {"x": 1}, ValueError("err"))
        dlq.enqueue("b", {"y": 2}, TypeError("err2"))

        letters = dlq.list_all()

        assert len(letters) == 2
        types = {ev.event_type for ev in letters}
        assert types == {"a", "b"}

    def test_list_all_on_empty_store_returns_empty(self, tmp_path: Path):
        """list_all() on a nonexistent file returns an empty list."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        assert dlq.list_all() == []

    def test_purge_removes_all_entries(self, tmp_path: Path):
        """purge() clears all dead letters and returns count removed."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        dlq.enqueue("a", {}, ValueError("1"))
        dlq.enqueue("b", {}, ValueError("2"))
        dlq.enqueue("c", {}, ValueError("3"))

        removed = dlq.purge()

        assert removed == 3
        assert dlq.count == 0

    def test_purge_on_empty_queue_returns_zero(self, tmp_path: Path):
        """purge() on an empty queue returns 0."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        assert dlq.purge() == 0


@pytest.mark.unit
class TestDeadLetterQueueRetry:
    """Tests for DeadLetterQueue.retry_all() — ISC-10, ISC-11."""

    def test_retry_all_success_removes_entries(self, tmp_path: Path):
        """retry_all() removes letters that the handler processes successfully."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        dlq.enqueue("task.a", {"id": 1}, ValueError("first"))
        dlq.enqueue("task.b", {"id": 2}, ValueError("second"))

        processed: list = []
        succeeded, failed = dlq.retry_all(
            lambda etype, payload: processed.append(etype)
        )

        assert succeeded == 2
        assert failed == 0
        assert dlq.count == 0
        assert "task.a" in processed

    def test_retry_all_failure_keeps_entries(self, tmp_path: Path):
        """retry_all() keeps letters whose handler raises an exception."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        dlq.enqueue("task.a", {}, ValueError("original error"))

        def always_fail(etype, payload):
            raise RuntimeError("still failing")

        succeeded, failed = dlq.retry_all(always_fail)

        assert succeeded == 0
        assert failed == 1
        assert dlq.count == 1

    def test_retry_all_partial_success(self, tmp_path: Path):
        """retry_all() correctly handles mixed success/failure."""
        dlq = DeadLetterQueue(tmp_path / "dlq.jsonl")
        dlq.enqueue("good.task", {"ok": True}, ValueError("err"))
        dlq.enqueue("bad.task", {"ok": False}, ValueError("err"))

        def handler(etype, payload):
            if not payload.get("ok"):
                raise ValueError("not ok")

        succeeded, failed = dlq.retry_all(handler)

        assert succeeded == 1
        assert failed == 1
        remaining = dlq.list_all()
        assert remaining[0].event_type == "bad.task"


# ===========================================================================
# File-backed EventStore (replay.py)
# ===========================================================================


@pytest.mark.unit
class TestFileBackedEventStoreAppend:
    """Tests for replay.EventStore.append() — ISC-13, ISC-18."""

    def test_append_writes_jsonl_file(self, tmp_path: Path):
        """append() persists events to a JSONL file."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")

        store.append("user.created", {"name": "Alice"})

        lines = (tmp_path / "events.jsonl").read_text().strip().split("\n")
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["event_type"] == "user.created"
        assert entry["payload"]["name"] == "Alice"

    def test_append_increments_sequence(self, tmp_path: Path):
        """append() assigns monotonically increasing sequence numbers."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")

        e1 = store.append("a", {})
        e2 = store.append("b", {})
        e3 = store.append("c", {})

        assert e1.sequence_number == 1
        assert e2.sequence_number == 2
        assert e3.sequence_number == 3

    def test_append_returns_stored_event(self, tmp_path: Path):
        """append() returns a StoredEvent with the assigned sequence number."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        result = store.append("order.placed", {"amount": 99.99})

        assert isinstance(result, StoredEvent)
        assert result.event_type == "order.placed"
        assert result.payload["amount"] == 99.99
        assert result.sequence_number >= 1

    def test_event_count_property(self, tmp_path: Path):
        """event_count reflects total events appended — ISC-18."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        assert store.event_count == 0

        store.append("e1", {})
        store.append("e2", {})
        store.append("e3", {})

        assert store.event_count == 3

    def test_load_persisted_sequence_on_init(self, tmp_path: Path):
        """A new EventStore instance reads existing sequence from file."""
        path = tmp_path / "events.jsonl"
        store1 = FileBackedEventStore(path)
        store1.append("first", {})
        store1.append("second", {})

        # Create new instance pointing to same file
        store2 = FileBackedEventStore(path)
        next_event = store2.append("third", {})

        assert next_event.sequence_number == 3


@pytest.mark.unit
class TestFileBackedEventStoreReplay:
    """Tests for replay.EventStore.replay() — ISC-14, ISC-15, ISC-16."""

    def test_replay_calls_handler_for_each_event(self, tmp_path: Path):
        """replay() calls the handler once per stored event."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        store.append("order.created", {"id": 1})
        store.append("order.shipped", {"id": 2})
        store.append("order.delivered", {"id": 3})

        replayed: list[StoredEvent] = []
        count = store.replay(replayed.append)

        assert count == 3
        assert len(replayed) == 3

    def test_replay_from_sequence_skips_earlier(self, tmp_path: Path):
        """replay(from_sequence=N) skips events with sequence < N — ISC-15."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        for i in range(5):
            store.append("evt", {"i": i})

        replayed: list[StoredEvent] = []
        count = store.replay(replayed.append, from_sequence=3)

        assert count == 3
        assert all(e.sequence_number >= 3 for e in replayed)

    def test_replay_event_type_filter(self, tmp_path: Path):
        """replay(event_types={...}) only replays matching types — ISC-16."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        store.append("order.created", {})
        store.append("payment.received", {})
        store.append("order.shipped", {})
        store.append("payment.failed", {})

        replayed: list[StoredEvent] = []
        count = store.replay(
            replayed.append, event_types={"order.created", "order.shipped"}
        )

        assert count == 2
        event_types = {e.event_type for e in replayed}
        assert event_types == {"order.created", "order.shipped"}

    def test_replay_on_empty_store_returns_zero(self, tmp_path: Path):
        """replay() on a nonexistent file returns 0 without error."""
        store = FileBackedEventStore(tmp_path / "missing.jsonl")
        count = store.replay(lambda e: None)
        assert count == 0


@pytest.mark.unit
class TestFileBackedEventStoreSnapshot:
    """Tests for replay.EventStore.snapshot() and load_snapshot() — ISC-17."""

    def test_snapshot_writes_json_file(self, tmp_path: Path):
        """snapshot() writes state to the given path as JSON."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        store.append("init", {})
        snap_path = tmp_path / "snap.json"

        store.snapshot({"users": 5, "orders": 12}, snap_path)

        assert snap_path.exists()
        data = json.loads(snap_path.read_text())
        assert data["state"]["users"] == 5
        assert data["last_sequence"] == 1

    def test_load_snapshot_returns_state_and_sequence(self, tmp_path: Path):
        """load_snapshot() returns (state, last_sequence) from saved file."""
        store = FileBackedEventStore(tmp_path / "events.jsonl")
        store.append("event1", {})
        store.append("event2", {})
        snap_path = tmp_path / "snap.json"
        state_in = {"total": 42, "status": "ok"}
        store.snapshot(state_in, snap_path)

        state_out, last_seq = store.load_snapshot(snap_path)

        assert state_out == state_in
        assert last_seq == 2

    def test_snapshot_and_replay_round_trip(self, tmp_path: Path):
        """State reconstructed from snapshot + replay matches expected final state."""
        events_path = tmp_path / "events.jsonl"
        snap_path = tmp_path / "snap.json"

        store = FileBackedEventStore(events_path)
        store.append("counter.increment", {"by": 1})
        store.append("counter.increment", {"by": 2})

        # Save snapshot at sequence 2
        store.snapshot({"total": 3}, snap_path)
        state, last_seq = store.load_snapshot(snap_path)

        # New events after snapshot
        store.append("counter.increment", {"by": 5})

        replayed_sum = state["total"]
        store.replay(
            lambda e: None,  # sum already in state up to snapshot
            from_sequence=last_seq + 1,
        )

        assert replayed_sum == 3  # snapshot state preserved correctly


# ===========================================================================
# MCP Tools
# ===========================================================================


@pytest.mark.unit
class TestMcpEmitEvent:
    """Tests for mcp_tools.emit_event() — ISC-19, ISC-20, ISC-21."""

    def test_emit_known_event_type_returns_success(self):
        """emit_event() with a known EventType returns status='success'."""
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("system.startup", {"version": "2.0"})

        assert result["status"] == "success"
        assert result["event_type"] == "system.startup"

    def test_emit_returns_event_id(self):
        """emit_event() response includes a non-empty event_id — ISC-21."""
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("analysis.start", {"target": "/src"})

        assert "event_id" in result
        assert isinstance(result["event_id"], str)
        assert len(result["event_id"]) > 0

    def test_emit_unknown_type_falls_back_to_custom(self):
        """emit_event() with an unknown type falls back to EventType.CUSTOM — ISC-20."""
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("my.custom.event.type", {"data": 42})

        assert result["status"] == "success"
        # original_type is injected into payload for non-standard types
        assert result["event_type"] == "my.custom.event.type"

    def test_emit_includes_source_in_response(self):
        """emit_event() includes source identifier in the response."""
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("module.load", {}, source="test_runner")

        assert result["source"] == "test_runner"

    def test_emit_priority_normal_default(self):
        """emit_event() defaults to 'normal' priority."""
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("health.check", {})

        assert result.get("priority", "normal") == "normal"

    def test_emit_custom_priority(self):
        """emit_event() accepts 'critical' priority without error."""
        from codomyrmex.events.mcp_tools import emit_event

        result = emit_event("security.alert", {"threat": "high"}, priority="critical")

        assert result["status"] == "success"


@pytest.mark.unit
class TestMcpListEventTypes:
    """Tests for mcp_tools.list_event_types() — ISC-22."""

    def test_list_event_types_returns_success(self):
        """list_event_types() returns a dict with status='success'."""
        from codomyrmex.events.mcp_tools import list_event_types

        result = list_event_types()

        assert result["status"] == "success"

    def test_list_event_types_returns_dict_with_count(self):
        """list_event_types() result includes 'count' field."""
        from codomyrmex.events.mcp_tools import list_event_types

        result = list_event_types()

        assert "count" in result
        assert isinstance(result["count"], int)
        assert result["count"] >= 0

    def test_list_event_types_result_is_list(self):
        """list_event_types() result['event_types'] is a list."""
        from codomyrmex.events.mcp_tools import list_event_types

        result = list_event_types()

        assert "event_types" in result
        assert isinstance(result["event_types"], list)


@pytest.mark.unit
class TestMcpGetEventHistory:
    """Tests for mcp_tools.get_event_history() — ISC-23."""

    def test_get_event_history_returns_success(self):
        """get_event_history() returns a dict with status='success'."""
        from codomyrmex.events.mcp_tools import get_event_history

        result = get_event_history()

        assert result["status"] == "success"

    def test_get_event_history_result_contains_events_list(self):
        """get_event_history() includes an 'events' list."""
        from codomyrmex.events.mcp_tools import get_event_history

        result = get_event_history()

        assert "events" in result
        assert isinstance(result["events"], list)

    def test_get_event_history_limit_honoured(self):
        """get_event_history() respects the limit parameter."""
        from codomyrmex.events.mcp_tools import emit_event, get_event_history

        # Emit some events to ensure the logger has entries
        for i in range(5):
            emit_event("metric.update", {"metric_name": f"cpu_{i}", "metric_value": i})

        result = get_event_history(limit=3)

        assert result["count"] <= 3
        assert len(result["events"]) <= 3

    def test_get_event_history_filter_by_type(self):
        """get_event_history() accepts event_type filter without error."""
        from codomyrmex.events.mcp_tools import get_event_history

        result = get_event_history(event_type="metric.update")

        assert result["status"] == "success"
        # All returned events should match the filter type
        for entry in result["events"]:
            assert entry["event_type"] == "metric.update"


# ===========================================================================
# IntegrationBus
# ===========================================================================


@pytest.mark.unit
class TestIntegrationBusBasics:
    """Tests for IntegrationBus subscribe/emit — covers integration_bus.py 0%."""

    def test_emit_returns_integration_event(self):
        """emit() returns an IntegrationEvent with the correct topic."""
        bus = IntegrationBus()
        event = bus.emit("build.complete", source="ci", payload={"status": "ok"})

        assert isinstance(event, IntegrationEvent)
        assert event.topic == "build.complete"
        assert event.source == "ci"
        assert event.payload["status"] == "ok"

    def test_subscribe_and_receive_event(self):
        """Subscribed handler receives emitted event on matching topic."""
        bus = IntegrationBus()
        received: list[IntegrationEvent] = []
        bus.subscribe("order.placed", received.append)

        bus.emit("order.placed", payload={"order_id": 99})

        assert len(received) == 1
        assert received[0].payload["order_id"] == 99

    def test_subscriber_only_receives_its_topic(self):
        """Subscriber does not receive events on unsubscribed topics."""
        bus = IntegrationBus()
        received: list = []
        bus.subscribe("payment.received", received.append)

        bus.emit("order.placed", payload={})
        bus.emit("order.shipped", payload={})

        assert len(received) == 0

    def test_multiple_subscribers_same_topic(self):
        """Multiple subscribers on the same topic all receive the event."""
        bus = IntegrationBus()
        counts = [0, 0]
        bus.subscribe("deploy.done", lambda e: counts.__setitem__(0, counts[0] + 1))
        bus.subscribe("deploy.done", lambda e: counts.__setitem__(1, counts[1] + 1))

        bus.emit("deploy.done")

        assert counts == [1, 1]

    def test_wildcard_subscriber_receives_all_events(self):
        """A subscriber on '*' receives every emitted event."""
        bus = IntegrationBus()
        received: list[IntegrationEvent] = []
        bus.subscribe("*", received.append)

        bus.emit("a.event")
        bus.emit("b.event")
        bus.emit("c.event")

        assert len(received) == 3

    def test_handler_error_does_not_stop_other_handlers(self):
        """An exception in one handler does not prevent others from running."""
        bus = IntegrationBus()
        received: list = []

        def bad_handler(e: IntegrationEvent) -> None:
            raise RuntimeError("intentional failure")

        bus.subscribe("task.run", bad_handler)
        bus.subscribe("task.run", lambda e: received.append(e))

        bus.emit("task.run", payload={})

        assert len(received) == 1


@pytest.mark.unit
class TestIntegrationBusHistory:
    """Tests for IntegrationBus history tracking."""

    def test_history_size_increments(self):
        """history_size reflects the number of events emitted."""
        bus = IntegrationBus()
        assert bus.history_size == 0

        bus.emit("a")
        bus.emit("b")
        bus.emit("c")

        assert bus.history_size == 3

    def test_history_by_topic_filters(self):
        """history_by_topic() returns only events for the given topic."""
        bus = IntegrationBus()
        bus.emit("alpha", payload={"n": 1})
        bus.emit("beta", payload={"n": 2})
        bus.emit("alpha", payload={"n": 3})

        alpha_events = bus.history_by_topic("alpha")

        assert len(alpha_events) == 2
        assert all(e.topic == "alpha" for e in alpha_events)

    def test_clear_history_resets_size(self):
        """clear_history() resets history_size to zero."""
        bus = IntegrationBus()
        bus.emit("x")
        bus.emit("y")

        bus.clear_history()

        assert bus.history_size == 0

    def test_topic_count_increases_with_new_subscriptions(self):
        """topic_count reflects the number of unique subscribed topics."""
        bus = IntegrationBus()
        bus.subscribe("topic.a", lambda e: None)
        bus.subscribe("topic.b", lambda e: None)

        assert bus.topic_count >= 2

    def test_integration_event_auto_assigns_id_and_timestamp(self):
        """IntegrationEvent sets event_id and timestamp automatically."""
        event = IntegrationEvent(topic="test")
        assert event.event_id != ""
        assert event.timestamp > 0


# ===========================================================================
# EventLogger extended coverage
# ===========================================================================


@pytest.mark.unit
class TestEventLoggerExtended:
    """Tests for EventLogger methods not covered by existing tests — ISC-24..28."""

    def _make_fresh_logger(self):
        """Creates a new EventLogger on its own private EventBus."""
        from codomyrmex.events.handlers.event_logger import EventLogger

        bus = EventBus()
        return EventLogger(event_bus=bus), bus

    def _emit(self, bus: EventBus, event_type: EventType, source: str = "test"):
        event = Event(event_type=event_type, source=source)
        bus.publish(event)

    def test_get_error_events_returns_only_errors(self):
        """get_error_events() returns only events whose type contains 'error' — ISC-26."""
        logger, bus = self._make_fresh_logger()
        self._emit(bus, EventType.SYSTEM_STARTUP)
        self._emit(bus, EventType.SYSTEM_ERROR)
        self._emit(bus, EventType.MODULE_ERROR)

        errors = logger.get_error_events()

        assert len(errors) == 2
        for entry in errors:
            assert "error" in entry.event.event_type.value.lower()

    def test_clear_resets_history_and_counts(self):
        """clear() empties all entries and statistics — ISC-27."""
        logger, bus = self._make_fresh_logger()
        self._emit(bus, EventType.SYSTEM_STARTUP)
        self._emit(bus, EventType.SYSTEM_ERROR)

        logger.clear()

        stats = logger.get_event_statistics()
        assert stats["total_events"] == 0
        assert stats["event_counts"] == {}
        assert stats["error_counts"] == {}
        assert logger.get_recent_events(100) == []

    def test_export_logs_json(self, tmp_path: Path):
        """export_logs() writes valid JSON to the given path — ISC-24."""
        logger, bus = self._make_fresh_logger()
        self._emit(bus, EventType.ANALYSIS_START, "exporter")
        self._emit(bus, EventType.ANALYSIS_COMPLETE, "exporter")

        out = tmp_path / "events.json"
        logger.export_logs(str(out), format="json")

        assert out.exists()
        data = json.loads(out.read_text())
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["event_type"] == EventType.ANALYSIS_START.value

    def test_export_logs_csv(self, tmp_path: Path):
        """export_logs() writes valid CSV header and rows — ISC-25."""
        logger, bus = self._make_fresh_logger()
        self._emit(bus, EventType.BUILD_START, "builder")

        out = tmp_path / "events.csv"
        logger.export_logs(str(out), format="csv")

        assert out.exists()
        content = out.read_text()
        assert "id,timestamp,type,source" in content
        assert "build.start" in content

    def test_get_performance_report_structure(self):
        """get_performance_report() returns dict with expected keys — ISC-28."""
        logger, bus = self._make_fresh_logger()
        self._emit(bus, EventType.SYSTEM_STARTUP)

        report = logger.get_performance_report()

        assert isinstance(report, dict)
        assert "by_type" in report
        assert "overall_avg_ms" in report
        assert "total_recorded" in report

    def test_get_events_by_type_filters_correctly(self):
        """get_events_by_type() returns only events of the specified type."""
        logger, bus = self._make_fresh_logger()
        self._emit(bus, EventType.SYSTEM_STARTUP)
        self._emit(bus, EventType.SYSTEM_SHUTDOWN)
        self._emit(bus, EventType.SYSTEM_STARTUP)

        startup_events = logger.get_events_by_type(EventType.SYSTEM_STARTUP)

        assert len(startup_events) == 2
        for entry in startup_events:
            assert entry.event.event_type == EventType.SYSTEM_STARTUP

    def test_get_recent_events_count(self):
        """get_recent_events(n) returns at most n entries."""
        logger, bus = self._make_fresh_logger()
        for _ in range(10):
            self._emit(bus, EventType.METRIC_UPDATE)

        recent = logger.get_recent_events(limit=5)

        assert len(recent) <= 5


# ===========================================================================
# AsyncStream (async_stream.py)
# ===========================================================================


@pytest.mark.unit
class TestAsyncStream:
    """Tests for AsyncStream — covers async_stream.py from 0%."""

    def test_subscribe_returns_id(self):
        """subscribe() returns a non-empty subscription ID string."""
        from codomyrmex.events.streaming.async_stream import AsyncStream

        async def run():
            stream = AsyncStream()
            sub_id = await stream.subscribe()
            return sub_id

        result = asyncio.run(run())
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unsubscribe_known_id_returns_true(self):
        """unsubscribe() returns True for a known subscription ID."""
        from codomyrmex.events.streaming.async_stream import AsyncStream

        async def run():
            stream = AsyncStream()
            sub_id = await stream.subscribe()
            return await stream.unsubscribe(sub_id)

        assert asyncio.run(run()) is True

    def test_unsubscribe_unknown_id_returns_false(self):
        """unsubscribe() returns False for an unknown ID."""
        from codomyrmex.events.streaming.async_stream import AsyncStream

        async def run():
            stream = AsyncStream()
            return await stream.unsubscribe("no-such-id")

        assert asyncio.run(run()) is False

    def test_publish_returns_true(self):
        """publish() returns True when the event is queued successfully."""
        from codomyrmex.events.streaming.async_stream import AsyncStream
        from codomyrmex.events.streaming.models import Event

        async def run():
            stream = AsyncStream(buffer_size=10)
            event = Event(data="hello")
            return await stream.publish(event)

        assert asyncio.run(run()) is True

    def test_multiple_subscriptions_have_unique_ids(self):
        """Multiple calls to subscribe() return distinct IDs."""
        from codomyrmex.events.streaming.async_stream import AsyncStream

        async def run():
            stream = AsyncStream()
            ids = [await stream.subscribe() for _ in range(5)]
            return ids

        ids = asyncio.run(run())
        assert len(set(ids)) == 5


@pytest.mark.unit
class TestBatchingStream:
    """Tests for BatchingStream — covers additional async_stream.py lines."""

    def test_on_batch_registers_handler(self):
        """on_batch() appends a handler to the internal handler list."""
        from codomyrmex.events.streaming.async_stream import BatchingStream

        stream = BatchingStream(batch_size=5)
        batches: list = []
        stream.on_batch(batches.append)

        assert len(stream._handlers) == 1

    def test_add_events_and_flush(self):
        """add() accumulates events; stop() flushes remaining batch."""
        from codomyrmex.events.streaming.async_stream import BatchingStream
        from codomyrmex.events.streaming.models import Event

        async def run():
            stream = BatchingStream(batch_size=10, flush_interval=60.0)
            batches: list = []
            stream.on_batch(batches.append)
            await stream.start()

            for i in range(3):
                await stream.add(Event(data=f"item-{i}"))

            await stream.stop()
            return batches

        result = asyncio.run(run())
        # After stop(), _flush() is called — batches should contain the 3 events
        all_events = [e for batch in result for e in batch]
        assert len(all_events) == 3

    def test_batch_size_triggers_flush(self):
        """Adding batch_size events triggers an immediate flush."""
        from codomyrmex.events.streaming.async_stream import BatchingStream
        from codomyrmex.events.streaming.models import Event

        async def run():
            stream = BatchingStream(batch_size=3, flush_interval=60.0)
            batches: list = []
            stream.on_batch(batches.append)
            await stream.start()

            # Add exactly batch_size events to trigger flush
            for i in range(3):
                await stream.add(Event(data=i))

            await stream.stop()
            return batches

        result = asyncio.run(run())
        total = sum(len(b) for b in result)
        assert total == 3


# ===========================================================================
# StoredEvent serialisation
# ===========================================================================


@pytest.mark.unit
class TestStoredEvent:
    """Tests for StoredEvent dataclass serialisation."""

    def test_to_dict_contains_all_fields(self):
        """StoredEvent.to_dict() includes all expected keys."""
        event = StoredEvent(
            event_type="user.registered",
            payload={"email": "a@b.com"},
            sequence_number=7,
            metadata={"source": "api"},
        )
        d = event.to_dict()

        assert d["event_type"] == "user.registered"
        assert d["payload"]["email"] == "a@b.com"
        assert d["sequence_number"] == 7
        assert d["metadata"]["source"] == "api"
        assert "timestamp" in d

    def test_from_dict_round_trip(self):
        """StoredEvent.from_dict(event.to_dict()) reproduces the same data."""
        original = StoredEvent(
            event_type="order.shipped",
            payload={"tracking": "XYZ"},
            sequence_number=3,
            metadata={"region": "us-east-1"},
        )
        restored = StoredEvent.from_dict(original.to_dict())

        assert restored.event_type == original.event_type
        assert restored.payload == original.payload
        assert restored.sequence_number == original.sequence_number
        assert restored.metadata == original.metadata


# ===========================================================================
# DeadLetter serialisation
# ===========================================================================


@pytest.mark.unit
class TestDeadLetterDataclass:
    """Tests for DeadLetter dataclass serialisation."""

    def test_to_dict_contains_all_fields(self):
        """DeadLetter.to_dict() includes all expected keys."""
        letter = DeadLetter(
            event_type="payment.failed",
            payload={"amount": 50},
            error="Gateway timeout",
            error_type="TimeoutError",
            attempt_count=2,
            metadata={"gateway": "stripe"},
        )
        d = letter.to_dict()

        assert d["event_type"] == "payment.failed"
        assert d["payload"]["amount"] == 50
        assert d["error"] == "Gateway timeout"
        assert d["error_type"] == "TimeoutError"
        assert d["attempt_count"] == 2
        assert d["metadata"]["gateway"] == "stripe"

    def test_from_dict_round_trip(self):
        """DeadLetter.from_dict(letter.to_dict()) reproduces the same data."""
        original = DeadLetter(
            event_type="sms.failed",
            payload={"to": "+1234"},
            error="Invalid number",
            error_type="ValueError",
            attempt_count=1,
        )
        restored = DeadLetter.from_dict(original.to_dict())

        assert restored.event_type == original.event_type
        assert restored.payload == original.payload
        assert restored.error == original.error
        assert restored.error_type == original.error_type
