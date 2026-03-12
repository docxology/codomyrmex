"""WebSocket live feed data provider.

Provides structured event data for real-time dashboard streaming
of logs, metrics, and agent status updates.

Example::

    provider = LiveFeedProvider()
    events = provider.get_recent_events(limit=10)
    snapshot = provider.get_snapshot()
"""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FeedEvent:
    """A single live feed event.

    Attributes:
        event_type: Category (``"log"``, ``"metric"``, ``"agent_status"``, ``"alert"``).
        source: Module or agent that emitted the event.
        data: Event payload.
        timestamp: Unix timestamp.
        severity: Log level or priority.
    """

    event_type: str
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    severity: str = "info"

    def to_json(self) -> str:
        """Serialize to JSON for WebSocket transmission."""
        return json.dumps(asdict(self), default=str)


class LiveFeedProvider:
    """Provides structured event data for WebSocket streaming.

    Maintains a bounded buffer of recent events for client catch-up
    and provides a snapshot of current system state.

    Args:
        max_events: Maximum events to retain in the rolling buffer.

    Example::

        provider = LiveFeedProvider()
        provider.emit("metric", "telemetry", {"cpu": 45.2})
        provider.emit("log", "hermes", {"message": "Task completed"})
        events = provider.get_recent_events(limit=5)
    """

    def __init__(self, max_events: int = 1000) -> None:
        self._events: deque[FeedEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._subscribers: list[Any] = []

    def emit(
        self,
        event_type: str,
        source: str,
        data: dict[str, Any] | None = None,
        severity: str = "info",
    ) -> FeedEvent:
        """Emit a new live feed event.

        Args:
            event_type: Category (log, metric, agent_status, alert).
            source: Emitting module or agent.
            data: Event payload.
            severity: Event severity level.

        Returns:
            The emitted :class:`FeedEvent`.
        """
        event = FeedEvent(
            event_type=event_type,
            source=source,
            data=data or {},
            severity=severity,
        )
        with self._lock:
            self._events.append(event)
        return event

    def get_recent_events(
        self,
        limit: int = 50,
        event_type: str = "",
        source: str = "",
    ) -> list[FeedEvent]:
        """Get recent events from the buffer.

        Args:
            limit: Maximum events to return.
            event_type: Optional type filter.
            source: Optional source filter.

        Returns:
            List of recent events, newest first.
        """
        with self._lock:
            events = list(self._events)

        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if source:
            events = [e for e in events if e.source == source]

        return list(reversed(events[-limit:]))

    def get_snapshot(self) -> dict[str, Any]:
        """Get a snapshot of current system state.

        Returns:
            Dict with ``total_events``, ``event_types``, ``sources``,
            and ``recent`` events.
        """
        with self._lock:
            events = list(self._events)

        types: dict[str, int] = {}
        sources: dict[str, int] = {}
        for e in events:
            types[e.event_type] = types.get(e.event_type, 0) + 1
            sources[e.source] = sources.get(e.source, 0) + 1

        return {
            "total_events": len(events),
            "event_types": types,
            "sources": sources,
            "recent": [asdict(e) for e in list(reversed(events[-10:]))],
        }

    def clear(self) -> None:
        """Clear the event buffer."""
        with self._lock:
            self._events.clear()

    def get_events_since(self, since: float) -> list[FeedEvent]:
        """Get all events since a timestamp.

        Args:
            since: Unix timestamp to filter from.

        Returns:
            List of events since the given timestamp.
        """
        with self._lock:
            return [e for e in self._events if e.timestamp >= since]


_singleton: LiveFeedProvider | None = None


def get_live_feed() -> LiveFeedProvider:
    """Get the global live feed provider singleton."""
    global _singleton
    if _singleton is None:
        _singleton = LiveFeedProvider()
    return _singleton


__all__ = [
    "FeedEvent",
    "LiveFeedProvider",
    "get_live_feed",
]
