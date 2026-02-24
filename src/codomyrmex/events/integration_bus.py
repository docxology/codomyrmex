"""Cross-module event routing with type-safe payloads.

Routes events between modules with topic-based subscriptions.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring import get_logger

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
        """Execute   Post Init   operations natively."""
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
        """Execute   Init   operations natively."""
        self._handlers: dict[str, list[Callable[[IntegrationEvent], None]]] = defaultdict(list)
        self._history: list[IntegrationEvent] = []

    def subscribe(self, topic: str, handler: Callable[[IntegrationEvent], None]) -> None:
        """Execute Subscribe operations natively."""
        self._handlers[topic].append(handler)

    def emit(self, topic: str, source: str = "", payload: dict[str, Any] | None = None) -> IntegrationEvent:
        """Execute Emit operations natively."""
        event = IntegrationEvent(topic=topic, source=source, payload=payload or {})
        self._history.append(event)

        for handler in self._handlers.get(topic, []):
            try:
                handler(event)
            except Exception as exc:
                logger.warning("Handler error", extra={"topic": topic, "error": str(exc)[:80]})

        # Wildcard subscribers
        for handler in self._handlers.get("*", []):
            try:
                handler(event)
            except Exception:
                pass

        return event

    @property
    def topic_count(self) -> int:
        """Execute Topic Count operations natively."""
        return len(self._handlers)

    @property
    def history_size(self) -> int:
        """Execute History Size operations natively."""
        return len(self._history)

    def history_by_topic(self, topic: str) -> list[IntegrationEvent]:
        """Execute History By Topic operations natively."""
        return [e for e in self._history if e.topic == topic]

    def clear_history(self) -> None:
        """Execute Clear History operations natively."""
        self._history.clear()


__all__ = ["IntegrationBus", "IntegrationEvent"]
