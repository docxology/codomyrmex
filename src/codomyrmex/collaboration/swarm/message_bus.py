"""Topic-routed in-process message bus for swarm communication.

Provides pub/sub messaging with topic filtering for inter-agent
communication within a swarm.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.collaboration.swarm.protocol import SwarmMessage
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


MessageHandler = Callable[[SwarmMessage], None]


@dataclass
class Subscription:
    """A topic subscription.

    Attributes:
        subscriber_id: ID of the subscribing agent.
        topic: Topic pattern to match.
        handler: Callback for received messages.
    """

    subscriber_id: str
    topic: str
    handler: MessageHandler


class MessageBus:
    """Topic-routed in-process pub/sub message bus.

    Supports wildcard topics with ``*`` matching any single segment.

    Usage::

        bus = MessageBus()
        received = []
        bus.subscribe("alice", "task.*", lambda m: received.append(m))
        bus.publish("task.assigned", SwarmMessage(...))
        assert len(received) == 1
    """

    def __init__(self) -> None:
        """Execute   Init   operations natively."""
        self._subscriptions: list[Subscription] = []
        self._history: list[SwarmMessage] = []
        self._history_limit: int = 1000

    def subscribe(
        self,
        subscriber_id: str,
        topic: str,
        handler: MessageHandler,
    ) -> None:
        """Subscribe to a topic with a handler.

        Args:
            subscriber_id: ID of the subscribing agent.
            topic: Topic pattern (use ``*`` for wildcard).
            handler: Callback invoked with matching messages.
        """
        self._subscriptions.append(Subscription(
            subscriber_id=subscriber_id,
            topic=topic,
            handler=handler,
        ))
        logger.info(
            "Subscription added",
            extra={"subscriber": subscriber_id, "topic": topic},
        )

    def unsubscribe(self, subscriber_id: str, topic: str | None = None) -> int:
        """Remove subscriptions for a subscriber.

        Args:
            subscriber_id: ID to unsubscribe.
            topic: Optional topic to match (None = all topics).

        Returns:
            Number of subscriptions removed.
        """
        before = len(self._subscriptions)
        self._subscriptions = [
            s for s in self._subscriptions
            if not (
                s.subscriber_id == subscriber_id
                and (topic is None or s.topic == topic)
            )
        ]
        removed = before - len(self._subscriptions)
        return removed

    def publish(self, topic: str, message: SwarmMessage) -> int:
        """Publish a message to a topic.

        All subscribers whose topic pattern matches will receive the message.

        Args:
            topic: The topic to publish to.
            message: The message to send.

        Returns:
            Number of handlers invoked.
        """
        # Record in history
        if len(self._history) >= self._history_limit:
            self._history = self._history[-self._history_limit // 2:]
        self._history.append(message)

        # Deliver to matching subscribers
        delivered = 0
        for sub in self._subscriptions:
            if self._topic_matches(sub.topic, topic):
                try:
                    sub.handler(message)
                    delivered += 1
                except Exception as exc:
                    logger.warning(
                        "Handler error",
                        extra={
                            "subscriber": sub.subscriber_id,
                            "error": str(exc),
                        },
                    )

        logger.info(
            "Message published",
            extra={"topic": topic, "delivered": delivered},
        )

        return delivered

    @property
    def subscription_count(self) -> int:
        """Execute Subscription Count operations natively."""
        return len(self._subscriptions)

    @property
    def history_size(self) -> int:
        """Execute History Size operations natively."""
        return len(self._history)

    def recent_messages(self, limit: int = 10) -> list[SwarmMessage]:
        """Get recent messages from history."""
        return list(self._history[-limit:])

    @staticmethod
    def _topic_matches(pattern: str, topic: str) -> bool:
        """Check if a topic matches a pattern.

        Supports ``*`` as single-segment wildcard and ``#`` as
        multi-segment wildcard.
        """
        pattern_parts = pattern.split(".")
        topic_parts = topic.split(".")

        if "#" in pattern_parts:
            # Multi-segment wildcard: matches any suffix
            idx = pattern_parts.index("#")
            return topic_parts[:idx] == pattern_parts[:idx]

        if len(pattern_parts) != len(topic_parts):
            return False

        for p, t in zip(pattern_parts, topic_parts):
            if p == "*":
                continue
            if p != t:
                return False

        return True


__all__ = [
    "MessageBus",
    "MessageHandler",
    "Subscription",
]
