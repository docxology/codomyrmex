"""Inter-agent communication system.

This module provides a publish-subscribe message bus for inter-agent
communication within the Codomyrmex framework. Agents can publish messages
and subscribe to specific message types or wildcard patterns.

Architecture:
    - Message: Dataclass representing a single message with sender, recipient, type, content
    - MessageBus: Core message routing system with subscription management

Usage::

    bus = MessageBus()


    # Subscribe to specific message type
    def handle_task(msg: Message):
        print(f"Received task: {msg.content}")


    bus.subscribe("task", handle_task)

    # Publish a message
    bus.send(
        sender="agent1", recipient="agent2", message_type="task", content="process data"
    )

    # Broadcast to all subscribers
    bus.broadcast(sender="agent1", message_type="alert", content="system status update")

Thread Safety: This implementation is NOT thread-safe. For concurrent access,
wrap all operations with appropriate locks or use a threaded variant.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """Message structure for inter-agent communication.

    Attributes:
        id: Unique message identifier (auto-generated UUID).
        sender: Identifier of the sending agent.
        recipient: Identifier of the receiving agent (None for broadcast).
        message_type: Type/category of message for routing.
        content: The message payload (any serializable content).
        metadata: Additional metadata (priority, tags, correlation IDs).
        timestamp: Unix timestamp when message was created.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    sender: str = ""
    recipient: str | None = None
    message_type: str = ""
    content: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: __import__("time").time())

    def is_broadcast(self) -> bool:
        """Check if this message is a broadcast (no specific recipient)."""
        return self.recipient is None

    def has_priority(self) -> bool:
        """Check if message has elevated priority."""
        return self.metadata.get("priority", 0) > 0

    def get_correlation_id(self) -> str | None:
        """Get correlation ID for message chaining."""
        return self.metadata.get("correlation_id")


class MessageBus:
    """Message bus for inter-agent communication.

    Implements a publish-subscribe pattern where agents can:
    - Subscribe to specific message types
    - Subscribe to wildcard patterns ("*") for all messages
    - Send direct messages to specific recipients
    - Broadcast messages to all subscribers

    Attributes:
        subscribers: Dict mapping message_type to list of handler callbacks.
        message_history: List of all published messages (for auditing/replay).

    Example::

        bus = MessageBus()


        # Agent subscribes to task messages
        def on_task(msg: Message):
            print(f"Agent received: {msg.content}")


        bus.subscribe("task", on_task)

        # Another agent sends a task
        bus.send(
            sender="planner",
            recipient="worker",
            message_type="task",
            content="analyze data",
        )
    """

    def __init__(self, max_history: int = 1000):
        """Initialize message bus.

        Args:
            max_history: Maximum number of messages to retain in history.
        """
        self.subscribers: dict[str, list[Callable[[Message], None]]] = {}
        self.message_history: list[Message] = []
        self.max_history = max_history
        self.logger = get_logger(__name__)

    def subscribe(
        self,
        message_type: str,
        handler: Callable[[Message], None],
        priority: int = 0,
    ) -> None:
        """Subscribe to messages of a specific type.

        Args:
            message_type: Type of messages to subscribe to.
            handler: Callback function to handle messages.
            priority: Handler priority (higher = called first, default 0).
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []

        # Insert handler based on priority (higher priority = earlier in list)
        inserted = False
        for i, existing in enumerate(self.subscribers[message_type]):
            existing_priority = getattr(existing, "_priority", 0)
            if priority > existing_priority:
                self.subscribers[message_type].insert(i, handler)
                inserted = True
                break

        if not inserted:
            self.subscribers[message_type].append(handler)

        # Attach priority to handler for re-sorting
        handler._priority = priority  # type: ignore[attr-defined]
        self.logger.debug(
            "Subscribed handler to message type: %s (priority=%d)",
            message_type,
            priority,
        )

    def unsubscribe(
        self,
        message_type: str,
        handler: Callable[[Message], None],
    ) -> bool:
        """Unsubscribe from messages of a specific type.

        Args:
            message_type: Type of messages to unsubscribe from.
            handler: Callback function to remove.

        Returns:
            True if handler was found and removed, False otherwise.
        """
        if message_type in self.subscribers:
            if handler in self.subscribers[message_type]:
                self.subscribers[message_type].remove(handler)
                self.logger.debug(
                    "Unsubscribed handler from message type: %s", message_type
                )
                return True

            # Also check for handlers with matching priority removal
            self._cleanup_empty_subscriptions()
        return False

    def _cleanup_empty_subscriptions(self) -> None:
        """Remove empty subscription lists to conserve memory."""
        empty_types = [t for t, handlers in self.subscribers.items() if not handlers]
        for t in empty_types:
            del self.subscribers[t]

    def publish(self, message: Message) -> int:
        """Publish a message to all subscribers.

        Args:
            message: Message to publish.

        Returns:
            Number of subscribers that received the message.
        """
        # Add to history with size limit
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history :]

        delivery_count = 0

        # Publish to specific type subscribers
        if message.message_type in self.subscribers:
            for handler in self.subscribers[message.message_type]:
                try:
                    handler(message)
                    delivery_count += 1
                except (
                    ValueError,
                    RuntimeError,
                    AttributeError,
                    OSError,
                    TypeError,
                ) as e:
                    self.logger.error("Error in message handler: %s", e, exc_info=True)

        # Publish to wildcard subscribers
        if "*" in self.subscribers:
            for handler in self.subscribers["*"]:
                try:
                    handler(message)
                    delivery_count += 1
                except (
                    ValueError,
                    RuntimeError,
                    AttributeError,
                    OSError,
                    TypeError,
                ) as e:
                    self.logger.error(
                        "Error in wildcard message handler: %s", e, exc_info=True
                    )

        self.logger.debug(
            "Published message %s of type %s to %d subscribers",
            message.id,
            message.message_type,
            delivery_count,
        )
        return delivery_count

    def send(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> Message:
        """Send a message to a specific recipient.

        Args:
            sender: Sender identifier.
            recipient: Recipient identifier.
            message_type: Type of message.
            content: Message content.
            metadata: Optional metadata dict.
            correlation_id: Optional ID for message chaining.

        Returns:
            Created message.
        """
        # Build metadata with optional correlation_id
        msg_metadata = metadata or {}
        if correlation_id:
            msg_metadata["correlation_id"] = correlation_id

        message = Message(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            metadata=msg_metadata,
        )

        self.publish(message)
        return message

    def broadcast(
        self,
        sender: str,
        message_type: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
        priority: int = 0,
    ) -> Message:
        """Broadcast a message to all subscribers.

        Broadcast messages have no specific recipient and are delivered
        to all subscribers of the message type (and wildcard subscribers).

        Args:
            sender: Sender identifier.
            message_type: Type of message.
            content: Message content.
            metadata: Optional metadata dict.
            priority: Message priority (affects delivery order).

        Returns:
            Created message.
        """
        msg_metadata = metadata or {}
        msg_metadata["priority"] = priority
        msg_metadata["is_broadcast"] = True

        message = Message(
            sender=sender,
            recipient=None,
            message_type=message_type,
            content=content,
            metadata=msg_metadata,
        )

        self.publish(message)
        return message

    def get_message_history(
        self,
        message_type: str | None = None,
        sender: str | None = None,
        recipient: str | None = None,
        limit: int | None = None,
    ) -> list[Message]:
        """Get message history with filtering options.

        Args:
            message_type: Filter by message type (optional).
            sender: Filter by sender (optional).
            recipient: Filter by recipient (optional).
            limit: Limit number of messages (optional, returns most recent).

        Returns:
            List of matching messages, most recent last.
        """
        messages = self.message_history

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        if sender:
            messages = [m for m in messages if m.sender == sender]

        if recipient:
            messages = [m for m in messages if m.recipient == recipient]

        if limit:
            messages = messages[-limit:]

        return messages

    def get_subscriber_count(self, message_type: str | None = None) -> int:
        """Get total number of subscribers.

        Args:
            message_type: If provided, only count subscribers for this type.

        Returns:
            Total subscriber count.
        """
        if message_type:
            return len(self.subscribers.get(message_type, []))
        return sum(len(handlers) for handlers in self.subscribers.values())

    def clear_history(self) -> int:
        """Clear message history.

        Returns:
            Number of messages that were cleared.
        """
        count = len(self.message_history)
        self.message_history.clear()
        self.logger.info("Cleared %d messages from history", count)
        return count


__all__ = ["Message", "MessageBus"]
