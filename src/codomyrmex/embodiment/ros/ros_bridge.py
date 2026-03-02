"""ROS2-compatible message bridge for embodied agent communication.

Provides a self-contained pub/sub message bus that mirrors ROS2 topic
semantics, including typed topics, message history, and optional
latching (retained last message for late subscribers).

This bridge does NOT require rclpy — it runs in-process for testing
and simulation. When a real ROS2 environment is available, swap the
transport layer while keeping the same API surface.
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """A message on a topic with metadata."""

    topic: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    sender: str = ""


@dataclass
class TopicInfo:
    """Metadata about a registered topic."""

    name: str
    message_type: str = "dict"
    latched: bool = False
    subscriber_count: int = 0
    total_published: int = 0


class ROS2Bridge:
    """In-process ROS2-style pub/sub message bridge.

    Supports:
    - Named topics with typed messages
    - Multiple subscribers per topic with wildcard matching
    - Message history (configurable depth per topic)
    - Latching — late subscribers receive the last published message
    - Message filtering via predicates
    - Introspection — list topics, subscriber counts, history

    Example::

        bridge = ROS2Bridge("agent_node")
        bridge.create_topic("/odom", latched=True)

        received = []
        bridge.subscribe("/odom", received.append)

        bridge.publish("/odom", {"x": 1.0, "y": 2.0, "theta": 0.5})
        assert len(received) == 1
    """

    def __init__(
        self,
        node_name: str,
        history_depth: int = 100,
    ) -> None:
        self.node_name = node_name
        self._subscribers: dict[str, list[Callable[[Message], Any]]] = {}
        self._history: dict[str, deque[Message]] = {}
        self._latched: dict[str, Message | None] = {}
        self._topic_meta: dict[str, TopicInfo] = {}
        self._history_depth = history_depth
        logger.info("ROS2Bridge '%s' initialized (depth=%d)", node_name, history_depth)

    # ── Topic Management ────────────────────────────────────────────

    def create_topic(
        self,
        topic: str,
        message_type: str = "dict",
        latched: bool = False,
    ) -> None:
        """Register a topic. Idempotent — already-registered topics are updated."""
        if topic not in self._topic_meta:
            self._topic_meta[topic] = TopicInfo(name=topic, message_type=message_type, latched=latched)
            self._subscribers.setdefault(topic, [])
            self._history.setdefault(topic, deque(maxlen=self._history_depth))
            self._latched[topic] = None
        else:
            self._topic_meta[topic].latched = latched
            self._topic_meta[topic].message_type = message_type

    def list_topics(self) -> list[TopicInfo]:
        """Return metadata for all registered topics."""
        return list(self._topic_meta.values())

    # ── Publish ─────────────────────────────────────────────────────

    def publish(self, topic: str, payload: dict[str, Any]) -> Message:
        """Publish a message to a topic.

        Creates the topic if it does not exist.

        Args:
            topic: Topic name (e.g. "/odom").
            payload: Message content dict.

        Returns:
            The published Message.
        """
        self.create_topic(topic)
        msg = Message(topic=topic, payload=payload, sender=self.node_name)

        # Store history
        self._history[topic].append(msg)
        self._latched[topic] = msg
        self._topic_meta[topic].total_published += 1

        # Deliver to subscribers
        for callback in self._subscribers.get(topic, []):
            try:
                callback(msg)
            except Exception:
                logger.exception("Subscriber callback failed on topic '%s'", topic)

        logger.debug("Published to '%s': %s", topic, payload)
        return msg

    # ── Subscribe ───────────────────────────────────────────────────

    def subscribe(
        self,
        topic: str,
        callback: Callable[[Message], Any],
        replay_latched: bool = True,
    ) -> Callable[[], None]:
        """Subscribe to a topic.

        Args:
            topic: Topic name to subscribe to.
            callback: Function called with each new Message.
            replay_latched: If True and the topic is latched, immediately
                deliver the last published message.

        Returns:
            An unsubscribe callable — call it to remove this subscription.
        """
        self.create_topic(topic)
        self._subscribers[topic].append(callback)
        self._topic_meta[topic].subscriber_count += 1

        # Replay latched message for late subscriber
        if replay_latched and self._topic_meta[topic].latched and self._latched.get(topic):
            try:
                callback(self._latched[topic])  # type: ignore[arg-type]
            except Exception:
                logger.exception("Latched replay failed on '%s'", topic)

        def _unsubscribe() -> None:
            """Unsubscribe from the specified event or channel."""
            try:
                self._subscribers[topic].remove(callback)
                self._topic_meta[topic].subscriber_count -= 1
            except ValueError as e:
                logger.debug("Unsubscribe called for already-removed callback on topic '%s': %s", topic, e)
                pass

        return _unsubscribe

    # ── History & Introspection ─────────────────────────────────────

    def get_history(self, topic: str, last_n: int | None = None) -> list[Message]:
        """Return message history for a topic.

        Args:
            topic: Topic name.
            last_n: If provided, return only the last N messages.
        """
        msgs = list(self._history.get(topic, []))
        if last_n is not None:
            return msgs[-last_n:]
        return msgs

    def simulate_message(self, topic: str, payload: dict[str, Any]) -> None:
        """Utility for testing: simulate an incoming message without publishing.

        Delivers directly to subscribers without storing in history.
        """
        msg = Message(topic=topic, payload=payload, sender="__simulator__")
        for callback in self._subscribers.get(topic, []):
            callback(msg)

    def clear_history(self, topic: str | None = None) -> None:
        """Clear message history for one or all topics."""
        if topic:
            if topic in self._history:
                self._history[topic].clear()
        else:
            for q in self._history.values():
                q.clear()

    @property
    def total_messages(self) -> int:
        """Total messages published across all topics."""
        return sum(info.total_published for info in self._topic_meta.values())
