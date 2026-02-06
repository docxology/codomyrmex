"""
Streaming Module

Real-time data streaming patterns with SSE and message broker support.
"""

__version__ = "0.1.0"

import asyncio
import json
import queue
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union
import uuid


class EventType(Enum):
    """Standard event types."""
    MESSAGE = "message"
    ERROR = "error"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    HEARTBEAT = "heartbeat"


@dataclass
class Event:
    """A stream event."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.MESSAGE
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }
    
    def to_sse(self) -> str:
        """Convert to SSE format."""
        lines = [
            f"id: {self.id}",
            f"event: {self.type.value}",
            f"data: {json.dumps(self.data) if self.data else ''}",
            "",
        ]
        return "\n".join(lines)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            type=EventType(data.get("type", "message")),
            data=data.get("data"),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
        )


@dataclass
class Subscription:
    """A subscription to a stream."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = "*"
    handler: Optional[Callable[[Event], None]] = None
    filter_fn: Optional[Callable[[Event], bool]] = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def cancel(self) -> None:
        """Cancel this subscription."""
        self.active = False
    
    def should_receive(self, event: Event) -> bool:
        """Check if this subscription should receive an event."""
        if not self.active:
            return False
        if self.topic != "*" and self.topic != event.metadata.get("topic", "*"):
            return False
        if self.filter_fn and not self.filter_fn(event):
            return False
        return True


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
        filter_fn: Optional[Callable[[Event], bool]] = None,
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
        self._subscriptions: Dict[str, Subscription] = {}
        self._event_buffer: List[Event] = []
        self._buffer_size = 1000
        self._lock = threading.Lock()
    
    async def publish(self, event: Event) -> None:
        """Publish an event."""
        with self._lock:
            # Buffer event
            self._event_buffer.append(event)
            if len(self._event_buffer) > self._buffer_size:
                self._event_buffer.pop(0)
            
            # Notify subscribers
            for sub in self._subscriptions.values():
                if sub.should_receive(event) and sub.handler:
                    try:
                        sub.handler(event)
                    except Exception:
                        pass  # Don't let handler errors affect other subscribers
    
    async def subscribe(
        self,
        handler: Callable[[Event], None],
        topic: str = "*",
        filter_fn: Optional[Callable[[Event], bool]] = None,
    ) -> Subscription:
        """Subscribe to events."""
        sub = Subscription(
            topic=topic,
            handler=handler,
            filter_fn=filter_fn,
        )
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
    
    def get_recent_events(self, count: int = 10) -> List[Event]:
        """Get recent events from buffer."""
        return self._event_buffer[-count:]


class SSEStream(Stream):
    """Server-Sent Events stream implementation."""
    
    def __init__(self, buffer_size: int = 100):
        self._subscriptions: Dict[str, Subscription] = {}
        self._event_queues: Dict[str, asyncio.Queue] = {}
        self._buffer_size = buffer_size
        self._event_buffer: List[Event] = []
    
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
        filter_fn: Optional[Callable[[Event], bool]] = None,
    ) -> Subscription:
        """Subscribe to SSE events."""
        sub = Subscription(
            topic=topic,
            handler=handler,
            filter_fn=filter_fn,
        )
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
            except asyncio.TimeoutError:
                # Send heartbeat
                yield Event(type=EventType.HEARTBEAT)
    
    async def sse_generator(self, subscription_id: str) -> AsyncIterator[str]:
        """Generate SSE-formatted strings."""
        async for event in self.events(subscription_id):
            yield event.to_sse()


class StreamProcessor:
    """Process events from a stream with transformations."""
    
    def __init__(self, source: Stream):
        self.source = source
        self._transforms: List[Callable[[Event], Optional[Event]]] = []
        self._sinks: List[Stream] = []
    
    def map(self, fn: Callable[[Event], Event]) -> "StreamProcessor":
        """Add a map transformation."""
        self._transforms.append(fn)
        return self
    
    def filter(self, fn: Callable[[Event], bool]) -> "StreamProcessor":
        """Add a filter transformation."""
        def filter_transform(event: Event) -> Optional[Event]:
            return event if fn(event) else None
        self._transforms.append(filter_transform)
        return self
    
    def sink(self, target: Stream) -> "StreamProcessor":
        """Add a sink to forward processed events."""
        self._sinks.append(target)
        return self
    
    async def start(self) -> Subscription:
        """Start processing."""
        async def process_event(event: Event) -> None:
            result = event
            for transform in self._transforms:
                result = transform(result)
                if result is None:
                    return
            
            for sink in self._sinks:
                await sink.publish(result)
        
        return await self.source.subscribe(
            handler=lambda e: asyncio.create_task(process_event(e))
        )


class TopicStream:
    """Stream with topic-based routing."""
    
    def __init__(self):
        self._topics: Dict[str, InMemoryStream] = {}
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
    
    def list_topics(self) -> List[str]:
        """List all topics."""
        return list(self._topics.keys())


# Convenience functions
def create_event(
    data: Any,
    event_type: EventType = EventType.MESSAGE,
    **metadata,
) -> Event:
    """Create a new event."""
    return Event(
        type=event_type,
        data=data,
        metadata=metadata,
    )


async def broadcast(
    streams: List[Stream],
    event: Event,
) -> None:
    """Broadcast an event to multiple streams."""
    await asyncio.gather(*[s.publish(event) for s in streams])


__all__ = [
    # Core classes
    "Stream",
    "InMemoryStream",
    "SSEStream",
    "TopicStream",
    "StreamProcessor",
    # Data classes
    "Event",
    "EventType",
    "Subscription",
    # Convenience functions
    "create_event",
    "broadcast",
]
