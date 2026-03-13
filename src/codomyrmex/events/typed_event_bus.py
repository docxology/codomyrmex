"""Typed event bus with subscription filtering and async emission.

Production-grade pub/sub system with typed events, priority ordering,
wildcard subscriptions, and emission history.

Example::

    bus = TypedEventBus()
    bus.subscribe("module.loaded", lambda e: print(e.data))
    bus.emit(Event(type="module.loaded", data={"name": "agents"}))
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """A typed event for the event bus.

    Attributes:
        type: Dot-separated event type (e.g., ``"module.loaded"``).
        data: Event payload.
        source: Emitting module/component name.
        timestamp: Event timestamp (auto-set).
        event_id: Unique event ID (auto-set).
        priority: Event priority (higher = processed first).
    """

    type: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: float = field(default_factory=time.monotonic)
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    priority: int = 0


@dataclass
class Subscription:
    """An event subscription.

    Attributes:
        pattern: Event type pattern (supports ``*`` wildcard).
        callback: Handler function.
        sub_id: Unique subscription ID.
        priority: Handler priority (higher = called first).
    """

    pattern: str
    callback: Callable[[Event], None]
    sub_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    priority: int = 0

    def matches(self, event_type: str) -> bool:
        """Check if this subscription matches an event type.

        Supports:
        - Exact match: ``"module.loaded"``
        - Prefix wildcard: ``"module.*"``
        - Full wildcard: ``"*"``
        """
        if self.pattern == "*":
            return True
        if self.pattern.endswith(".*"):
            prefix = self.pattern[:-2]
            return event_type.startswith(prefix + ".") or event_type == prefix
        return self.pattern == event_type


class TypedEventBus:
    """Typed event bus with subscription filtering and history.

    Args:
        max_history: Maximum events to retain.

    Example::

        bus = TypedEventBus()
        received = []
        bus.subscribe("test.*", lambda e: received.append(e))
        bus.emit(Event(type="test.ping", data={"ok": True}))
        assert len(received) == 1
    """

    def __init__(self, max_history: int = 1000) -> None:
        self._subscriptions: list[Subscription] = []
        self._history: list[Event] = []
        self._max_history = max_history
        self._emit_count = 0

    def subscribe(
        self,
        pattern: str,
        callback: Callable[[Event], None],
        priority: int = 0,
    ) -> str:
        """Subscribe to events matching a pattern.

        Args:
            pattern: Event type pattern (supports ``*`` and ``prefix.*``).
            callback: Handler function receiving :class:`Event`.
            priority: Handler priority (higher = called first).

        Returns:
            Subscription ID for unsubscribing.
        """
        sub = Subscription(pattern=pattern, callback=callback, priority=priority)
        self._subscriptions.append(sub)
        self._subscriptions.sort(key=lambda s: s.priority, reverse=True)
        logger.debug("Subscribed %s to pattern '%s'", sub.sub_id, pattern)
        return sub.sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        """Remove a subscription by ID.

        Args:
            sub_id: Subscription ID returned by :meth:`subscribe`.

        Returns:
            True if subscription was found and removed.
        """
        before = len(self._subscriptions)
        self._subscriptions = [s for s in self._subscriptions if s.sub_id != sub_id]
        return len(self._subscriptions) < before

    def emit(self, event: Event) -> int:
        """Emit an event to all matching subscribers.

        Args:
            event: Event to emit.

        Returns:
            Number of handlers that received the event.
        """
        self._emit_count += 1
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        handler_count = 0
        for sub in self._subscriptions:
            if sub.matches(event.type):
                try:
                    sub.callback(event)
                    handler_count += 1
                except Exception:
                    logger.exception(
                        "Handler %s failed for event %s",
                        sub.sub_id,
                        event.type,
                    )

        return handler_count

    def get_history(self, event_type: str = "", limit: int = 50) -> list[Event]:
        """Get recent event history.

        Args:
            event_type: Optional filter by event type.
            limit: Maximum events to return.

        Returns:
            List of recent events (newest first).
        """
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return list(reversed(events[-limit:]))

    @property
    def stats(self) -> dict[str, int]:
        """Bus statistics."""
        return {
            "subscriptions": len(self._subscriptions),
            "total_emitted": self._emit_count,
            "history_size": len(self._history),
        }

    def clear(self) -> None:
        """Clear all subscriptions and history."""
        self._subscriptions.clear()
        self._history.clear()
        self._emit_count = 0


__all__ = [
    "Event",
    "Subscription",
    "TypedEventBus",
]
