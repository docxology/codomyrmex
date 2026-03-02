"""
Broadcast messaging for one-to-many communication.

Provides topic-based pub/sub patterns for agent swarms.
"""

import asyncio
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import ChannelError
from ..protocols import AgentMessage, MessageType

logger = get_logger(__name__)


@dataclass
class Subscription:
    """A subscription to a topic."""
    subscription_id: str
    topic: str
    subscriber_id: str
    handler: Callable[[AgentMessage], None]
    created_at: datetime = field(default_factory=datetime.now)
    filter_fn: Callable[[AgentMessage], bool] | None = None


@dataclass
class TopicInfo:
    """Information about a topic."""
    topic: str
    subscriber_count: int
    message_count: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "topic": self.topic,
            "subscriber_count": self.subscriber_count,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
        }


class Broadcaster:
    """
    Broadcast messenger for one-to-many communication.

    Implements a topic-based publish/subscribe pattern where agents
    can subscribe to topics and receive all messages published to them.

    Attributes:
        retention_count: Number of messages to retain per topic for replay.
    """

    def __init__(self, retention_count: int = 100):
        self._topics: dict[str, set[str]] = {}  # topic -> subscription_ids
        self._subscriptions: dict[str, Subscription] = {}  # subscription_id -> Subscription
        self._topic_created_at: dict[str, datetime] = {}
        self._message_counts: dict[str, int] = {}
        self._retention_count = retention_count
        self._retained_messages: dict[str, list[AgentMessage]] = {}

    def create_topic(self, topic: str) -> None:
        """Create a new topic."""
        if topic not in self._topics:
            self._topics[topic] = set()
            self._topic_created_at[topic] = datetime.now()
            self._message_counts[topic] = 0
            self._retained_messages[topic] = []
            logger.info(f"Created topic: {topic}")

    def delete_topic(self, topic: str) -> bool:
        """Delete a topic and all its subscriptions."""
        if topic not in self._topics:
            return False

        # Remove all subscriptions
        for sub_id in list(self._topics[topic]):
            self._unsubscribe(sub_id)

        del self._topics[topic]
        del self._topic_created_at[topic]
        del self._message_counts[topic]
        del self._retained_messages[topic]
        logger.info(f"Deleted topic: {topic}")
        return True

    def subscribe(
        self,
        topic: str,
        subscriber_id: str,
        handler: Callable[[AgentMessage], None],
        filter_fn: Callable[[AgentMessage], bool] | None = None,
        replay_retained: bool = False,
    ) -> str:
        """
        Subscribe to a topic.

        Args:
            topic: Topic to subscribe to.
            subscriber_id: ID of the subscribing agent.
            handler: Callback function for received messages.
            filter_fn: Optional filter function to filter messages.
            replay_retained: Whether to replay retained messages.

        Returns:
            Subscription ID.
        """
        # Create topic if it doesn't exist
        if topic not in self._topics:
            self.create_topic(topic)

        subscription_id = str(uuid.uuid4())
        subscription = Subscription(
            subscription_id=subscription_id,
            topic=topic,
            subscriber_id=subscriber_id,
            handler=handler,
            filter_fn=filter_fn,
        )

        self._subscriptions[subscription_id] = subscription
        self._topics[topic].add(subscription_id)

        logger.info(f"Agent {subscriber_id} subscribed to {topic}")

        # Replay retained messages if requested
        if replay_retained and topic in self._retained_messages:
            for message in self._retained_messages[topic]:
                if filter_fn is None or filter_fn(message):
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            asyncio.create_task(handler(message))
                        else:
                            handler(message)
                    except Exception as e:
                        logger.error(f"Error replaying message: {e}")

        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        return self._unsubscribe(subscription_id)

    def _unsubscribe(self, subscription_id: str) -> bool:
        """Internal unsubscribe implementation."""
        if subscription_id not in self._subscriptions:
            return False

        subscription = self._subscriptions[subscription_id]
        if subscription.topic in self._topics:
            self._topics[subscription.topic].discard(subscription_id)

        del self._subscriptions[subscription_id]
        logger.info(f"Agent {subscription.subscriber_id} unsubscribed from {subscription.topic}")
        return True

    def unsubscribe_all(self, subscriber_id: str) -> int:
        """Unsubscribe an agent from all topics."""
        count = 0
        for sub_id, sub in list(self._subscriptions.items()):
            if sub.subscriber_id == subscriber_id:
                self._unsubscribe(sub_id)
                count += 1
        return count

    async def publish(self, topic: str, message: AgentMessage) -> int:
        """
        Publish a message to a topic.

        Args:
            topic: Topic to publish to.
            message: Message to publish.

        Returns:
            Number of subscribers that received the message.
        """
        if topic not in self._topics:
            raise ChannelError(topic, "Topic does not exist")

        message.message_type = MessageType.BROADCAST
        self._message_counts[topic] += 1

        # Retain message
        self._retained_messages[topic].append(message)
        if len(self._retained_messages[topic]) > self._retention_count:
            self._retained_messages[topic].pop(0)

        delivered = 0
        for sub_id in self._topics[topic]:
            subscription = self._subscriptions.get(sub_id)
            if subscription:
                # Apply filter
                if subscription.filter_fn and not subscription.filter_fn(message):
                    continue

                try:
                    if asyncio.iscoroutinefunction(subscription.handler):
                        await subscription.handler(message)
                    else:
                        subscription.handler(message)
                    delivered += 1
                except Exception as e:
                    logger.error(f"Error delivering to {subscription.subscriber_id}: {e}")

        logger.debug(f"Published to {topic}: {delivered} subscribers received")
        return delivered

    def publish_sync(self, topic: str, message: AgentMessage) -> int:
        """Synchronous publish (creates task for async handlers)."""
        if topic not in self._topics:
            raise ChannelError(topic, "Topic does not exist")

        message.message_type = MessageType.BROADCAST
        self._message_counts[topic] += 1

        # Retain message
        self._retained_messages[topic].append(message)
        if len(self._retained_messages[topic]) > self._retention_count:
            self._retained_messages[topic].pop(0)

        delivered = 0
        for sub_id in self._topics[topic]:
            subscription = self._subscriptions.get(sub_id)
            if subscription:
                if subscription.filter_fn and not subscription.filter_fn(message):
                    continue

                try:
                    if asyncio.iscoroutinefunction(subscription.handler):
                        asyncio.create_task(subscription.handler(message))
                    else:
                        subscription.handler(message)
                    delivered += 1
                except Exception as e:
                    logger.error(f"Error delivering to {subscription.subscriber_id}: {e}")

        return delivered

    def get_topic_info(self, topic: str) -> TopicInfo | None:
        """Get information about a topic."""
        if topic not in self._topics:
            return None

        return TopicInfo(
            topic=topic,
            subscriber_count=len(self._topics[topic]),
            message_count=self._message_counts.get(topic, 0),
            created_at=self._topic_created_at.get(topic, datetime.now()),
        )

    def list_topics(self) -> list[TopicInfo]:
        """List all topics."""
        return [self.get_topic_info(t) for t in self._topics.keys() if self.get_topic_info(t)]

    def get_subscriber_topics(self, subscriber_id: str) -> list[str]:
        """Get all topics a subscriber is subscribed to."""
        topics = []
        for sub in self._subscriptions.values():
            if sub.subscriber_id == subscriber_id:
                topics.append(sub.topic)
        return topics


__all__ = [
    "Subscription",
    "TopicInfo",
    "Broadcaster",
]
