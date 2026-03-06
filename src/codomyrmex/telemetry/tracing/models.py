"""Tracing data models: SpanKind, SpanStatus, SpanContext, Span."""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SpanKind(Enum):
    """Type of span."""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Status of a span."""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """Context for trace propagation."""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    sampled: bool = True
    baggage: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for propagation."""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "sampled": self.sampled,
            "baggage": self.baggage,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpanContext":
        """Create from dict."""
        return cls(
            trace_id=data["trace_id"],
            span_id=data["span_id"],
            parent_span_id=data.get("parent_span_id"),
            sampled=data.get("sampled", True),
            baggage=data.get("baggage", {}),
        )

    def to_headers(self) -> dict[str, str]:
        """Convert to HTTP headers for propagation."""
        return {
            "X-Trace-Id": self.trace_id,
            "X-Span-Id": self.span_id,
            "X-Parent-Span-Id": self.parent_span_id or "",
            "X-Sampled": str(self.sampled).lower(),
        }

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> Optional["SpanContext"]:
        """Extract from HTTP headers."""
        trace_id = headers.get("X-Trace-Id") or headers.get("x-trace-id")
        span_id = headers.get("X-Span-Id") or headers.get("x-span-id")

        if not trace_id or not span_id:
            return None

        parent = headers.get("X-Parent-Span-Id") or headers.get("x-parent-span-id")
        sampled = headers.get("X-Sampled", "true").lower() == "true"

        return cls(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent or None,
            sampled=sampled,
        )


def _generate_id(length: int = 16) -> str:
    """Generate a random hex ID."""
    return uuid.uuid4().hex[:length]


@dataclass
class Span:
    """A trace span representing a unit of work."""

    name: str
    context: SpanContext
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def trace_id(self) -> str:
        return self.context.trace_id

    @property
    def span_id(self) -> str:
        return self.context.span_id

    @property
    def parent_span_id(self) -> str | None:
        return self.context.parent_span_id

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    @property
    def is_finished(self) -> bool:
        return self.end_time is not None

    def set_attribute(self, key: str, value: Any) -> "Span":
        """Set an attribute. Returns self for chaining."""
        self.attributes[key] = value
        return self

    def set_attributes(self, attributes: dict[str, Any]) -> "Span":
        """Set multiple attributes."""
        self.attributes.update(attributes)
        return self

    def add_event(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
        timestamp: float | None = None,
    ) -> "Span":
        """Add an event to the span."""
        self.events.append(
            {
                "name": name,
                "timestamp": timestamp or time.time(),
                "attributes": attributes or {},
            }
        )
        return self

    def set_status(self, status: SpanStatus, message: str = "") -> "Span":
        """Set span status."""
        self.status = status
        self.status_message = message
        return self

    def record_exception(self, exception: Exception) -> "Span":
        """Record an exception as an event."""
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            },
        )
        self.set_status(SpanStatus.ERROR, str(exception))
        return self

    def finish(self) -> None:
        """Finish the span."""
        if self.end_time is None:
            self.end_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "kind": self.kind.value,
            "status": self.status.value,
            "status_message": self.status_message,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": self.events,
        }
