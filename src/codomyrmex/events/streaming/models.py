"""
Streaming Models

Data classes and enums for event streaming.
"""

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
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
    def from_dict(cls, data: dict[str, Any]) -> "Event":
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
    handler: Callable[[Event], None] | None = None
    filter_fn: Callable[[Event], bool] | None = None
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


def create_event(
    data: Any,
    event_type: EventType = EventType.MESSAGE,
    **metadata,
) -> Event:
    """Create a new event."""
    return Event(type=event_type, data=data, metadata=metadata)
