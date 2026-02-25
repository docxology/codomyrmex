from dataclasses import dataclass, field
from typing import Any
from collections.abc import Callable
from uuid import uuid4

from codomyrmex.logging_monitoring import get_logger

"""Inter-agent communication system."""

logger = get_logger(__name__)


@dataclass
class Message:
    """Message structure for inter-agent communication."""

    id: str = field(default_factory=lambda: str(uuid4()))
    sender: str = ""
    recipient: str | None = None
    message_type: str = ""
    content: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class MessageBus:
    """Message bus for inter-agent communication."""

    def __init__(self):
        """Initialize message bus."""
        self.subscribers: dict[str, list[Callable[[Message], None]]] = {}
        self.message_history: list[Message] = []
        self.logger = get_logger(__name__)

    def subscribe(
        self, message_type: str, handler: Callable[[Message], None]
    ) -> None:
        """
        Subscribe to messages of a specific type.

        Args:
            message_type: Type of messages to subscribe to
            handler: Callback function to handle messages
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []

        self.subscribers[message_type].append(handler)
        self.logger.debug(
            f"Subscribed handler to message type: {message_type}"
        )

    def unsubscribe(
        self, message_type: str, handler: Callable[[Message], None]
    ) -> None:
        """
        Unsubscribe from messages of a specific type.

        Args:
            message_type: Type of messages to unsubscribe from
            handler: Callback function to remove
        """
        if message_type in self.subscribers:
            if handler in self.subscribers[message_type]:
                self.subscribers[message_type].remove(handler)
                self.logger.debug(
                    f"Unsubscribed handler from message type: {message_type}"
                )

    def publish(self, message: Message) -> None:
        """
        Publish a message to all subscribers.

        Args:
            message: Message to publish
        """
        self.message_history.append(message)

        # Publish to specific type subscribers
        if message.message_type in self.subscribers:
            for handler in self.subscribers[message.message_type]:
                try:
                    handler(message)
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    self.logger.error(
                        f"Error in message handler: {e}", exc_info=True
                    )

        # Publish to wildcard subscribers
        if "*" in self.subscribers:
            for handler in self.subscribers["*"]:
                try:
                    handler(message)
                except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                    self.logger.error(
                        f"Error in wildcard message handler: {e}", exc_info=True
                    )

        self.logger.debug(
            f"Published message {message.id} of type {message.message_type}"
        )

    def send(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """
        Send a message to a specific recipient.

        Args:
            sender: Sender identifier
            recipient: Recipient identifier
            message_type: Type of message
            content: Message content
            metadata: Optional metadata

        Returns:
            Created message
        """
        message = Message(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
        )

        self.publish(message)
        return message

    def broadcast(
        self,
        sender: str,
        message_type: str,
        content: Any,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """
        Broadcast a message to all subscribers.

        Args:
            sender: Sender identifier
            message_type: Type of message
            content: Message content
            metadata: Optional metadata

        Returns:
            Created message
        """
        message = Message(
            sender=sender,
            recipient=None,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
        )

        self.publish(message)
        return message

    def get_message_history(
        self, message_type: str | None = None, limit: int | None = None
    ) -> list[Message]:
        """
        Get message history.

        Args:
            message_type: Filter by message type (optional)
            limit: Limit number of messages (optional)

        Returns:
            List of messages
        """
        messages = self.message_history

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        if limit:
            messages = messages[-limit:]

        return messages


