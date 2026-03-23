"""Append-only event store with sequence numbers and topic indexing.

Persistent event stream supporting range queries, topic-based
access, and compaction of old events.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StreamEvent:
    """A single event in the stream.

    Attributes:
        sequence: Monotonically increasing sequence number.
        topic: Event topic/category.
        event_type: Specific event type.
        data: Event payload.
        timestamp: Event creation time.
        source: Event source identifier.
    """

    sequence: int = 0
    topic: str = ""
    event_type: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "topic": self.topic,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "source": self.source,
        }


class EventStore:
    """Append-only event store with sequence numbers.

    Supports topic indexing, range queries, and compaction.

    Example::

        store = EventStore()
        seq = store.append(StreamEvent(topic="agent", event_type="started"))
        events = store.read_by_topic("agent")
    """

    def __init__(self) -> None:
        self._events: list[StreamEvent] = []
        self._next_sequence = 1
        self._topic_index: dict[str, list[int]] = defaultdict(list)
        self._lock = threading.RLock()

    @property
    def count(self) -> int:
        """Total number of events in the store."""
        with self._lock:
            return len(self._events)

    @property
    def latest_sequence(self) -> int:
        """Latest sequence number."""
        with self._lock:
            return self._next_sequence - 1

    def append(self, event: StreamEvent) -> int:
        """Append an event and return its sequence number.

        Args:
            event: Event to store.

        Returns:
            Assigned sequence number.
        """
        with self._lock:
            event.sequence = self._next_sequence
            self._next_sequence += 1
            if not event.timestamp:
                event.timestamp = time.time()

            self._events.append(event)
            self._topic_index[event.topic].append(len(self._events) - 1)
            return event.sequence

    def read(self, from_seq: int = 1, to_seq: int = 0) -> list[StreamEvent]:
        """Read events in a sequence range.

        Args:
            from_seq: Start sequence (inclusive).
            to_seq: End sequence (inclusive). 0 = latest.

        Returns:
            list of events in the range.
        """
        with self._lock:
            if to_seq <= 0:
                to_seq = self.latest_sequence

            return [e for e in self._events if from_seq <= e.sequence <= to_seq]

    def read_by_topic(self, topic: str, limit: int = 0) -> list[StreamEvent]:
        """Read events by topic.

        Args:
            topic: Topic to filter by.
            limit: Maximum events to return (0 = all).

        Returns:
            Events matching the topic.
        """
        with self._lock:
            indices = self._topic_index.get(topic, [])
            events = [self._events[i] for i in indices]
            if limit > 0:
                events = events[-limit:]
            return events

    def read_by_time(self, from_time: float, to_time: float) -> list[StreamEvent]:
        """Read events in a time range.

        Args:
            from_time: Start timestamp (inclusive).
            to_time: End timestamp (inclusive).

        Returns:
            Events within the time range.
        """
        with self._lock:
            return [e for e in self._events if from_time <= e.timestamp <= to_time]

    def topics(self) -> list[str]:
        """list all known topics."""
        with self._lock:
            return sorted(self._topic_index.keys())

    def compact(self, before_seq: int) -> int:
        """Remove events before a sequence number.

        Args:
            before_seq: Remove events with sequence < this.

        Returns:
            Number of events removed.
        """
        with self._lock:
            original = len(self._events)
            self._events = [e for e in self._events if e.sequence >= before_seq]
            removed = original - len(self._events)

            # Rebuild topic index
            self._topic_index.clear()
            for i, e in enumerate(self._events):
                self._topic_index[e.topic].append(i)

            return removed

    def clear(self) -> None:
        """Clear all events and reset sequence."""
        with self._lock:
            self._events.clear()
            self._next_sequence = 1
            self._topic_index.clear()


_event_store = None
_store_lock = threading.Lock()


def get_event_store() -> EventStore:
    """Return the module-level singleton EventStore, creating it on first call."""
    global _event_store
    if _event_store is None:
        with _store_lock:
            if _event_store is None:
                _event_store = EventStore()
    return _event_store


__all__ = ["EventStore", "StreamEvent", "get_event_store"]
