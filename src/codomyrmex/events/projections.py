"""Stream projections — materialized views from event streams.

Folds event streams into counters, running aggregates, and
latest-per-key views.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from codomyrmex.events.event_store import EventStore, StreamEvent


class StreamProjection:
    """Fold event streams into materialized views.

    Example::

        projection = StreamProjection(store)
        count = projection.counter("agent")
        latest = projection.latest_per_key("agent", key_fn=lambda e: e.source)
    """

    def __init__(self, store: EventStore) -> None:
        self._store = store

    def counter(self, topic: str = "") -> int:
        """Count events, optionally filtered by topic.

        Args:
            topic: Topic to filter (empty = all events).

        Returns:
            Event count.
        """
        if topic:
            return len(self._store.read_by_topic(topic))
        return self._store.count

    def latest_per_key(
        self,
        topic: str,
        key_fn: Callable[[StreamEvent], str],
    ) -> dict[str, StreamEvent]:
        """Get the latest event per key.

        Args:
            topic: Topic to read from.
            key_fn: Function to extract key from event.

        Returns:
            Dict of key → latest event.
        """
        events = self._store.read_by_topic(topic)
        latest: dict[str, StreamEvent] = {}
        for event in events:
            key = key_fn(event)
            latest[key] = event
        return latest

    def fold(
        self,
        topic: str,
        reducer: Callable[[Any, StreamEvent], Any],
        init: Any = None,
    ) -> Any:
        """Generic fold over events in a topic.

        Args:
            topic: Topic to fold over.
            reducer: (accumulator, event) → new_accumulator.
            init: Initial accumulator value.

        Returns:
            Final accumulated value.
        """
        events = self._store.read_by_topic(topic)
        acc = init
        for event in events:
            acc = reducer(acc, event)
        return acc

    def group_by(
        self,
        topic: str,
        key_fn: Callable[[StreamEvent], str],
    ) -> dict[str, list[StreamEvent]]:
        """Group events by key.

        Args:
            topic: Topic to filter.
            key_fn: Key extraction function.

        Returns:
            Dict of key → list of events.
        """
        events = self._store.read_by_topic(topic)
        groups: dict[str, list[StreamEvent]] = defaultdict(list)
        for event in events:
            groups[key_fn(event)].append(event)
        return dict(groups)

    def running_aggregate(
        self,
        topic: str,
        value_fn: Callable[[StreamEvent], float],
    ) -> list[float]:
        """Compute running aggregate (cumulative sum).

        Args:
            topic: Topic to aggregate.
            value_fn: Extract numeric value from event.

        Returns:
            List of cumulative sums.
        """
        events = self._store.read_by_topic(topic)
        cumulative: list[float] = []
        total = 0.0
        for event in events:
            total += value_fn(event)
            cumulative.append(total)
        return cumulative


__all__ = ["StreamProjection"]
