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
        # Per-agent mailboxes for P2P direct messaging
        self._mailboxes: dict[str, list[dict[str, Any]]] = defaultdict(list)

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

    # ── P2P agent mailbox ───────────────────────────────────────────

    def send_to_agent(
        self,
        agent_id: str,
        message: dict[str, Any],
        *,
        source: str = "",
    ) -> str:
        """Post a direct message to an agent's inbox.

        The message is appended to the in-memory mailbox for *agent_id* and
        also emitted as an integration event (topic ``agent.inbox.<agent_id>``)
        so any subscribers can react.

        Args:
            agent_id: Destination agent identifier.
            message: Arbitrary message payload dict.
            source: Sender identifier.

        Returns:
            The ``event_id`` of the emitted integration event.
        """
        envelope: dict[str, Any] = {
            "agent_id": agent_id,
            "message": message,
            "source": source,
            "timestamp": time.time(),
        }
        self._mailboxes[agent_id].append(envelope)
        event = self.emit(
            f"agent.inbox.{agent_id}",
            source=source,
            payload=envelope,
        )
        logger.debug(
            "Sent message to agent '%s' (event_id=%s)", agent_id, event.event_id
        )
        return event.event_id

    def receive(self, agent_id: str, timeout: float = 0.0) -> dict[str, Any] | None:
        """Return the oldest unread message from *agent_id*'s mailbox.

        If the mailbox is empty, polls every 50 ms up to *timeout* seconds
        before returning ``None``.

        Args:
            agent_id: Recipient agent identifier.
            timeout: Maximum seconds to wait for a message (0 = no wait).

        Returns:
            The oldest message envelope, or ``None`` if the mailbox is empty
            after *timeout*.
        """
        import time as _time

        deadline = _time.time() + timeout
        while True:
            if self._mailboxes[agent_id]:
                return self._mailboxes[agent_id].pop(0)
            if _time.time() >= deadline:
                return None
            _time.sleep(0.05)  # 50 ms poll interval

    def drain_inbox(self, agent_id: str) -> list[dict[str, Any]]:
        """Return **all** pending messages for *agent_id* atomically.

        Args:
            agent_id: Recipient agent identifier.

        Returns:
            List of message envelopes (may be empty).
        """
        messages = list(self._mailboxes[agent_id])
        self._mailboxes[agent_id].clear()
        return messages

    @property
    def mailbox_size(self) -> int:
        """Total messages across all agent mailboxes."""
        return sum(len(msgs) for msgs in self._mailboxes.values())


__all__ = ["IntegrationBus", "IntegrationEvent"]
