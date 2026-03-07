"""Cross-module event routing with type-safe payloads.

Routes events between modules with topic-based subscriptions.
"""

from __future__ import annotations

import fnmatch
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


@dataclass
class IntegrationEvent:
    """An event routed through the bus.

    Attributes:
        topic: Event topic.
        source: Source module.
        payload: Event data.
        timestamp: When emitted.
        event_id: Unique ID.
    """

    topic: str
    source: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    event_id: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.event_id:
            self.event_id = f"evt-{int(self.timestamp * 1000) % 100000}"


class IntegrationBus:
    """Cross-module event bus.

    Usage::

        bus = IntegrationBus()
        bus.subscribe("build.complete", my_handler)
        bus.emit("build.complete", "ci_module", {"status": "ok"})
    """

    def __init__(self) -> None:
        self._handlers: dict[
            str, list[tuple[Callable[[IntegrationEvent], None], int]]
        ] = defaultdict(list)
        self._history: list[IntegrationEvent] = []

    def subscribe(
        self,
        topic: str,
        handler: Callable[[IntegrationEvent], None],
        priority: int = 0,
    ) -> None:
        """Subscribe to the specified event or channel.

        Args:
            topic: Topic name or pattern (glob).
            handler: Callback function.
            priority: Handler priority (higher = called first).
        """
        self._handlers[topic].append((handler, priority))
        # Keep handlers sorted by priority
        self._handlers[topic].sort(key=lambda x: x[1], reverse=True)

    def unsubscribe(
        self, topic: str, handler: Callable[[IntegrationEvent], None]
    ) -> bool:
        """Unsubscribe a handler from a topic.

        Returns:
            True if handler was found and removed.
        """
        if topic not in self._handlers:
            return False

        original_len = len(self._handlers[topic])
        self._handlers[topic] = [h for h in self._handlers[topic] if h[0] != handler]
        return len(self._handlers[topic]) < original_len

    def emit(
        self, topic: str, source: str = "", payload: dict[str, Any] | None = None
    ) -> IntegrationEvent:
        """Emit an event to registered listeners."""
        event = IntegrationEvent(topic=topic, source=source, payload=payload or {})
        self._history.append(event)

        # Collect all matching handlers
        matching_handlers: list[tuple[Callable[[IntegrationEvent], None], int]] = []

        for pattern, handlers in self._handlers.items():
            if pattern == topic or fnmatch.fnmatch(topic, pattern):
                matching_handlers.extend(handlers)

        # Sort all matching handlers by priority
        # Note: if a handler is subscribed to multiple matching patterns,
        # it will be called multiple times. This is consistent with EventBus.
        matching_handlers.sort(key=lambda x: x[1], reverse=True)

        for handler, _priority in matching_handlers:
            try:
                handler(event)
            except Exception as exc:
                logger.warning(
                    "Handler error for topic '%s'",
                    topic,
                    extra={"topic": topic, "error": str(exc)[:80]},
                    exc_info=True,
                )

        return event

    @property
    def topic_count(self) -> int:
        return len(self._handlers)

    @property
    def history_size(self) -> int:
        return len(self._history)

    def history_by_topic(self, topic: str) -> list[IntegrationEvent]:
        return [e for e in self._history if e.topic == topic]

    def clear_history(self) -> None:
        self._history.clear()


__all__ = ["IntegrationBus", "IntegrationEvent"]
