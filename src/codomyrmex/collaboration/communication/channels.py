"""
Communication channels for inter-agent messaging.

Provides Channel, MessageQueue, and ChannelManager classes for
establishing communication pathways between agents.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from ..exceptions import ChannelError
from ..protocols import AgentMessage

logger = get_logger(__name__)


class ChannelState(Enum):
    """State of a communication channel."""
    OPEN = "open"
    CLOSED = "closed"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ChannelInfo:
    """Information about a channel."""
    channel_id: str
    name: str
    state: ChannelState
    subscriber_count: int
    message_count: int
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "channel_id": self.channel_id,
            "name": self.name,
            "state": self.state.value,
            "subscriber_count": self.subscriber_count,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
        }


class Channel(ABC):
    """
    Abstract base class for communication channels.

    Channels provide a conduit for message passing between agents.
    Different channel implementations support different messaging patterns.
    """

    def __init__(self, channel_id: str | None = None, name: str = "Channel"):
        self._channel_id = channel_id or str(uuid.uuid4())
        self._name = name
        self._state = ChannelState.OPEN
        self._created_at = datetime.now()
        self._message_count = 0

    @property
    def channel_id(self) -> str:
        return self._channel_id

    @property
    def name(self) -> str:
        """name ."""
        return self._name

    @property
    def state(self) -> ChannelState:
        """state ."""
        return self._state

    @abstractmethod
    async def send(self, message: AgentMessage) -> None:
        """Send a message through the channel."""
        pass

    @abstractmethod
    async def receive(self) -> AgentMessage:
        """Receive a message from the channel."""
        pass

    @abstractmethod
    def get_info(self) -> ChannelInfo:
        """Get channel information."""
        pass

    def close(self) -> None:
        """Close the channel."""
        self._state = ChannelState.CLOSED
        logger.info(f"Channel {self._name} ({self._channel_id}) closed")

    def pause(self) -> None:
        """Pause the channel."""
        self._state = ChannelState.PAUSED

    def resume(self) -> None:
        """Resume a paused channel."""
        if self._state == ChannelState.PAUSED:
            self._state = ChannelState.OPEN


class MessageQueue:
    """
    Async message queue for buffering messages.

    Provides a thread-safe, async-compatible queue for agent messages
    with optional maximum size and message expiration.

    Attributes:
        max_size: Maximum queue size (0 for unlimited).
        message_ttl: Time-to-live for messages in seconds (0 for no expiration).
    """

    def __init__(self, max_size: int = 0, message_ttl: float = 0):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_size) if max_size > 0 else asyncio.Queue()
        self._max_size = max_size
        self._message_ttl = message_ttl
        self._message_count = 0

    @property
    def size(self) -> int:
        """Current queue size."""
        return self._queue.qsize()

    @property
    def is_empty(self) -> bool:
        """Whether the queue is empty."""
        return self._queue.empty()

    @property
    def is_full(self) -> bool:
        """Whether the queue is full."""
        return self._max_size > 0 and self._queue.full()

    async def put(self, message: AgentMessage, timeout: float | None = None) -> None:
        """
        Put a message in the queue.

        Args:
            message: The message to queue.
            timeout: Optional timeout in seconds.

        Raises:
            ChannelError: If the queue is full and timeout expires.
        """
        try:
            if timeout:
                await asyncio.wait_for(self._queue.put(message), timeout)
            else:
                await self._queue.put(message)
            self._message_count += 1
        except TimeoutError:
            raise ChannelError(
                "message_queue",
                f"Queue is full, timeout after {timeout}s"
            ) from None

    def put_nowait(self, message: AgentMessage) -> None:
        """Put a message without waiting."""
        try:
            self._queue.put_nowait(message)
            self._message_count += 1
        except asyncio.QueueFull:
            raise ChannelError("message_queue", "Queue is full") from None

    async def get(self, timeout: float | None = None) -> AgentMessage:
        """
        Get a message from the queue.

        Args:
            timeout: Optional timeout in seconds.

        Returns:
            The next message in the queue.

        Raises:
            ChannelError: If timeout expires before a message is available.
        """
        try:
            if timeout:
                message = await asyncio.wait_for(self._queue.get(), timeout)
            else:
                message = await self._queue.get()

            # Check message expiration
            if self._message_ttl > 0:
                age = (datetime.now() - message.timestamp).total_seconds()
                if age > self._message_ttl:
                    # Message expired, try to get next one
                    return await self.get(timeout)

            return message
        except TimeoutError:
            raise ChannelError(
                "message_queue",
                f"No message available, timeout after {timeout}s"
            ) from None

    def get_nowait(self) -> AgentMessage | None:
        """Get a message without waiting, returns None if empty."""
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty as e:
            logger.debug("No message available in queue: %s", e)
            return None

    def clear(self) -> int:
        """Clear all messages from the queue. Returns count of cleared messages."""
        count = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                count += 1
            except asyncio.QueueEmpty:
                break
        return count


class QueueChannel(Channel):
    """
    A channel backed by a message queue.

    Supports point-to-point messaging with message buffering.
    """

    def __init__(
        self,
        channel_id: str | None = None,
        name: str = "QueueChannel",
        max_size: int = 1000,
        message_ttl: float = 0,
    ):
        super().__init__(channel_id, name)
        self._queue = MessageQueue(max_size, message_ttl)

    async def send(self, message: AgentMessage) -> None:
        """Send a message to the queue."""
        if self._state != ChannelState.OPEN:
            raise ChannelError(self._channel_id, f"Channel is {self._state.value}")

        await self._queue.put(message)
        self._message_count += 1
        logger.debug(f"Message {message.id} sent on channel {self._name}")

    async def receive(self, timeout: float | None = None) -> AgentMessage:
        """Receive a message from the queue."""
        if self._state == ChannelState.CLOSED:
            raise ChannelError(self._channel_id, "Channel is closed")

        return await self._queue.get(timeout)

    def get_info(self) -> ChannelInfo:
        return ChannelInfo(
            channel_id=self._channel_id,
            name=self._name,
            state=self._state,
            subscriber_count=1,  # Point-to-point
            message_count=self._message_count,
            created_at=self._created_at,
        )


class ChannelManager:
    """
    Manager for creating and maintaining communication channels.

    Provides a centralized registry for channels and handles
    channel lifecycle management.
    """

    def __init__(self):
        self._channels: dict[str, Channel] = {}

    def create_channel(
        self,
        name: str,
        channel_type: str = "queue",
        **kwargs
    ) -> Channel:
        """
        Create a new channel.

        Args:
            name: Human-readable channel name.
            channel_type: Type of channel ("queue").
            **kwargs: Additional channel configuration.

        Returns:
            The created channel.
        """
        if channel_type == "queue":
            channel = QueueChannel(name=name, **kwargs)
        else:
            raise ValueError(f"Unknown channel type: {channel_type}")

        self._channels[channel.channel_id] = channel
        logger.info(f"Created channel: {name} ({channel.channel_id})")
        return channel

    def get_channel(self, channel_id: str) -> Channel | None:
        """Get a channel by ID."""
        return self._channels.get(channel_id)

    def get_channel_by_name(self, name: str) -> Channel | None:
        """Get a channel by name."""
        for channel in self._channels.values():
            if channel.name == name:
                return channel
        return None

    def list_channels(self) -> list[ChannelInfo]:
        """List all channels."""
        return [ch.get_info() for ch in self._channels.values()]

    def close_channel(self, channel_id: str) -> bool:
        """Close and remove a channel."""
        if channel_id in self._channels:
            self._channels[channel_id].close()
            del self._channels[channel_id]
            return True
        return False

    def close_all(self) -> None:
        """Close all channels."""
        for channel in list(self._channels.values()):
            channel.close()
        self._channels.clear()


__all__ = [
    "ChannelState",
    "ChannelInfo",
    "Channel",
    "MessageQueue",
    "QueueChannel",
    "ChannelManager",
]
