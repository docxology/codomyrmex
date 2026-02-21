"""Tests for Sprint 33: Event Streaming & Replay.

Covers EventStore (append, range queries, topic index, compaction),
EventReplayer (deterministic replay, diff), and StreamProjection
(counter, latest-per-key, fold, running aggregate).
"""

import time
import pytest

from codomyrmex.events.event_store import EventStore, StreamEvent
from codomyrmex.events.replayer import EventReplayer, ReplayResult
from codomyrmex.events.projections import StreamProjection


# ─── EventStore ───────────────────────────────────────────────────────

class TestEventStore:

    def test_append_and_read(self):
        store = EventStore()
        seq = store.append(StreamEvent(topic="agent", event_type="started"))
        assert seq == 1
        assert store.count == 1
        events = store.read()
        assert len(events) == 1

    def test_sequence_numbers(self):
        store = EventStore()
        s1 = store.append(StreamEvent(topic="a"))
        s2 = store.append(StreamEvent(topic="b"))
        assert s2 == s1 + 1

    def test_read_range(self):
        store = EventStore()
        store.append(StreamEvent(topic="a"))
        store.append(StreamEvent(topic="b"))
        store.append(StreamEvent(topic="c"))
        events = store.read(from_seq=2, to_seq=3)
        assert len(events) == 2

    def test_read_by_topic(self):
        store = EventStore()
        store.append(StreamEvent(topic="agent"))
        store.append(StreamEvent(topic="task"))
        store.append(StreamEvent(topic="agent"))
        agent_events = store.read_by_topic("agent")
        assert len(agent_events) == 2

    def test_compaction(self):
        store = EventStore()
        store.append(StreamEvent(topic="a"))
        store.append(StreamEvent(topic="b"))
        store.append(StreamEvent(topic="c"))
        removed = store.compact(before_seq=3)
        assert removed == 2
        assert store.count == 1

    def test_topics(self):
        store = EventStore()
        store.append(StreamEvent(topic="z"))
        store.append(StreamEvent(topic="a"))
        assert store.topics() == ["a", "z"]


# ─── EventReplayer ───────────────────────────────────────────────────

class TestEventReplayer:

    def test_replay_all(self):
        store = EventStore()
        store.append(StreamEvent(topic="agent", data={"n": 1}))
        store.append(StreamEvent(topic="agent", data={"n": 2}))

        replayer = EventReplayer(store)
        result = replayer.replay(
            handlers={"agent": lambda e: e.data["n"] * 10},
        )
        assert result.events_replayed == 2
        assert result.handler_outputs == [10, 20]

    def test_deterministic_replay(self):
        """Same input → same output."""
        store = EventStore()
        store.append(StreamEvent(topic="a", data={"v": 42}))

        replayer = EventReplayer(store)
        r1 = replayer.replay(handlers={"a": lambda e: e.data["v"]})
        r2 = replayer.replay(handlers={"a": lambda e: e.data["v"]})
        assert r1.handler_outputs == r2.handler_outputs

    def test_diff_deterministic(self):
        store = EventStore()
        store.append(StreamEvent(topic="a", data={"v": 1}))
        replayer = EventReplayer(store)
        r1 = replayer.replay(handlers={"a": lambda e: e.data["v"]})
        r2 = replayer.replay(handlers={"a": lambda e: e.data["v"]})
        diff = replayer.diff(r1, r2)
        assert diff["deterministic"] is True


# ─── StreamProjection ───────────────────────────────────────────────

class TestStreamProjection:

    def test_counter(self):
        store = EventStore()
        store.append(StreamEvent(topic="a"))
        store.append(StreamEvent(topic="a"))
        store.append(StreamEvent(topic="b"))
        proj = StreamProjection(store)
        assert proj.counter("a") == 2
        assert proj.counter() == 3

    def test_latest_per_key(self):
        store = EventStore()
        store.append(StreamEvent(topic="agent", source="a1", data={"v": 1}))
        store.append(StreamEvent(topic="agent", source="a2", data={"v": 2}))
        store.append(StreamEvent(topic="agent", source="a1", data={"v": 3}))
        proj = StreamProjection(store)
        latest = proj.latest_per_key("agent", key_fn=lambda e: e.source)
        assert latest["a1"].data["v"] == 3
        assert latest["a2"].data["v"] == 2

    def test_fold(self):
        store = EventStore()
        store.append(StreamEvent(topic="counter", data={"n": 5}))
        store.append(StreamEvent(topic="counter", data={"n": 3}))
        proj = StreamProjection(store)
        total = proj.fold("counter", lambda acc, e: acc + e.data["n"], init=0)
        assert total == 8

    def test_running_aggregate(self):
        store = EventStore()
        store.append(StreamEvent(topic="m", data={"v": 10}))
        store.append(StreamEvent(topic="m", data={"v": 20}))
        store.append(StreamEvent(topic="m", data={"v": 30}))
        proj = StreamProjection(store)
        cum = proj.running_aggregate("m", lambda e: e.data["v"])
        assert cum == [10, 30, 60]
