"""
Stream Implementations

In-memory and SSE stream backends.
"""

import asyncio
import threading
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .models import Event, EventType, Subscription

logger = get_logger(__name__)


class Stream(ABC):
    """Abstract base class for streams."""

    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event to the stream."""
        pass

    @abstractmethod
    async def subscribe(
        self,
        handler: Callable[[Event], None],
        topic: str = "*",
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> Subscription:
        """Subscribe to events."""
        pass

    @abstractmethod
    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        pass


class InMemoryStream(Stream):
    """In-memory stream implementation."""

    def __init__(self):
        self._subscriptions: dict[str, Subscription] = {}
        self._event_buffer: list[Event] = []
        self._buffer_size = 1000
        self._lock = threading.Lock()

    async def publish(self, event: Event) -> None:
        """Publish an event."""
        with self._lock:
            self._event_buffer.append(event)
            if len(self._event_buffer) > self._buffer_size:
                self._event_buffer.pop(0)
            for sub in self._subscriptions.values():
                if sub.should_receive(event) and sub.handler:
                    try:
                        sub.handler(event)
                    except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                        logger.warning("Stream handler error for subscription '%s': %s", sub.topic, e)
                        pass

    async def subscribe(
        self,
        handler: Callable[[Event], None],
        topic: str = "*",
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> Subscription:
        """Subscribe to events."""
        sub = Subscription(topic=topic, handler=handler, filter_fn=filter_fn)
        with self._lock:
            self._subscriptions[sub.id] = sub
        return sub

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe."""
        with self._lock:
            if subscription_id in self._subscriptions:
                del self._subscriptions[subscription_id]
                return True
        return False

    def get_recent_events(self, count: int = 10) -> list[Event]:
        """Get recent events from buffer."""
        return self._event_buffer[-count:]


class SSEStream(Stream):
    """Server-Sent Events stream implementation."""

    def __init__(self, buffer_size: int = 100):
        self._subscriptions: dict[str, Subscription] = {}
        self._event_queues: dict[str, asyncio.Queue] = {}
        self._buffer_size = buffer_size
        self._event_buffer: list[Event] = []

    async def publish(self, event: Event) -> None:
        """Publish an event."""
        self._event_buffer.append(event)
        if len(self._event_buffer) > self._buffer_size:
            self._event_buffer.pop(0)
        for sub_id, sub in self._subscriptions.items():
            if sub.should_receive(event):
                if sub_id in self._event_queues:
                    await self._event_queues[sub_id].put(event)

    async def subscribe(
        self,
        handler: Callable[[Event], None],
        topic: str = "*",
        filter_fn: Callable[[Event], bool] | None = None,
    ) -> Subscription:
        """Subscribe to SSE events."""
        sub = Subscription(topic=topic, handler=handler, filter_fn=filter_fn)
        self._subscriptions[sub.id] = sub
        self._event_queues[sub.id] = asyncio.Queue()
        return sub

    async def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe."""
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            if subscription_id in self._event_queues:
                del self._event_queues[subscription_id]
            return True
        return False

    async def events(self, subscription_id: str) -> AsyncIterator[Event]:
        """Async iterator for events."""
        if subscription_id not in self._event_queues:
            return
        queue = self._event_queues[subscription_id]
        while subscription_id in self._subscriptions:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield event
            except TimeoutError:
                yield Event(type=EventType.HEARTBEAT)

    async def sse_generator(self, subscription_id: str) -> AsyncIterator[str]:
        """Generate SSE-formatted strings."""
        async for event in self.events(subscription_id):
            yield event.to_sse()


class TopicStream:
    """Stream with topic-based routing."""

    def __init__(self):
        self._topics: dict[str, InMemoryStream] = {}
        self._default = InMemoryStream()

    def topic(self, name: str) -> InMemoryStream:
        """Get or create a topic stream."""
        if name not in self._topics:
            self._topics[name] = InMemoryStream()
        return self._topics[name]

    async def publish(self, topic: str, event: Event) -> None:
        """Publish to a topic."""
        event.metadata["topic"] = topic
        stream = self.topic(topic)
        await stream.publish(event)

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[Event], None],
    ) -> Subscription:
        """Subscribe to a topic."""
        stream = self.topic(topic)
        return await stream.subscribe(handler, topic=topic)

    def list_topics(self) -> list[str]:
        """List all topics."""
        return list(self._topics.keys())


async def broadcast(streams: list[Stream], event: Event) -> None:
    """Broadcast an event to multiple streams."""
    await asyncio.gather(*[s.publish(event) for s in streams])
