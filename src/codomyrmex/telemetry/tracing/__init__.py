"""
Telemetry Tracing Module

Distributed tracing, span management, and context propagation.
"""

__version__ = "0.1.0"

import functools
import json
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ContextManager, Dict, List, Optional, TypeVar
from collections.abc import Callable

T = TypeVar('T')


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
            parent_span_id=parent if parent else None,
            sampled=sampled,
        )


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
        self.events.append({
            "name": name,
            "timestamp": timestamp or time.time(),
            "attributes": attributes or {},
        })
        return self

    def set_status(
        self,
        status: SpanStatus,
        message: str = "",
    ) -> "Span":
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
            }
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


from abc import ABC, abstractmethod

class SpanExporter(ABC):
    """Base class for span exporters."""

    @abstractmethod
    def export(self, spans: list[Span]) -> None:
        """Export spans."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown exporter."""
        pass


class ConsoleExporter(SpanExporter):
    """Export spans to console."""

    def __init__(self, pretty: bool = True):
        self.pretty = pretty

    def export(self, spans: list[Span]) -> None:
        for span in spans:
            data = span.to_dict()
            if self.pretty:
                print(json.dumps(data, indent=2, default=str))
            else:
                print(json.dumps(data, default=str))

    def shutdown(self) -> None:
        """No-op shutdown for console exporter."""
        pass


class InMemoryExporter(SpanExporter):
    """Store spans in memory (useful for testing)."""

    def __init__(self, max_spans: int = 1000):
        self.max_spans = max_spans
        self.spans: list[Span] = []
        self._lock = threading.Lock()

    def export(self, spans: list[Span]) -> None:
        with self._lock:
            self.spans.extend(spans)
            # Trim if over limit
            if len(self.spans) > self.max_spans:
                self.spans = self.spans[-self.max_spans:]

    def get_spans(self, trace_id: str | None = None) -> list[Span]:
        """Get spans, optionally filtered by trace_id."""
        with self._lock:
            if trace_id:
                return [s for s in self.spans if s.trace_id == trace_id]
            return self.spans.copy()

    def clear(self) -> None:
        """Clear all spans."""
        with self._lock:
            self.spans.clear()

    def shutdown(self) -> None:
        """Clear spans on shutdown."""
        self.clear()


# Thread-local storage for context
_context_local = threading.local()


def _generate_id(length: int = 16) -> str:
    """Generate a random hex ID."""
    return uuid.uuid4().hex[:length]


class Tracer:
    """
    Tracer for creating and managing spans.

    Usage:
        tracer = Tracer("my-service")

        with tracer.start_span("operation") as span:
            span.set_attribute("key", "value")
            # do work

        # Or manual
        span = tracer.start_span("operation")
        try:
            # do work
        finally:
            span.finish()
    """

    def __init__(
        self,
        service_name: str = "default",
        exporter: SpanExporter | None = None,
    ):
        self.service_name = service_name
        self.exporter = exporter or ConsoleExporter()
        self._pending_spans: list[Span] = []
        self._lock = threading.Lock()

    def _get_current_context(self) -> SpanContext | None:
        """Get current span context from thread-local storage."""
        return getattr(_context_local, 'context', None)

    def _set_current_context(self, context: SpanContext | None) -> None:
        """Set current span context in thread-local storage."""
        _context_local.context = context

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent: SpanContext | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """
        Start a new span.

        Args:
            name: Span name
            kind: Span kind
            parent: Parent context (auto-detected if None)
            attributes: Initial attributes

        Returns:
            New Span
        """
        # Get parent context
        parent_ctx = parent or self._get_current_context()

        # Generate IDs
        trace_id = parent_ctx.trace_id if parent_ctx else _generate_id(32)
        span_id = _generate_id(16)
        parent_span_id = parent_ctx.span_id if parent_ctx else None

        context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )

        span = Span(
            name=name,
            context=context,
            kind=kind,
            attributes=attributes or {},
        )

        # Add service name
        span.set_attribute("service.name", self.service_name)

        return span

    @contextmanager
    def span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        **attributes,
    ) -> ContextManager[Span]:
        """
        Context manager for spans.

        Usage:
            with tracer.span("operation") as span:
                span.set_attribute("key", "value")
        """
        span = self.start_span(name, kind=kind, attributes=attributes)
        previous_context = self._get_current_context()
        self._set_current_context(span.context)

        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            raise
        finally:
            span.finish()
            self._set_current_context(previous_context)
            self._export_span(span)

    def _export_span(self, span: Span) -> None:
        """Export a finished span."""
        with self._lock:
            self._pending_spans.append(span)

            # Batch export (export every 10 spans or immediately in tests)
            if len(self._pending_spans) >= 10:
                self.exporter.export(self._pending_spans)
                self._pending_spans.clear()

    def flush(self) -> None:
        """Flush pending spans."""
        with self._lock:
            if self._pending_spans:
                self.exporter.export(self._pending_spans)
                self._pending_spans.clear()

    def shutdown(self) -> None:
        """Shutdown tracer."""
        self.flush()
        self.exporter.shutdown()


# Global tracer registry
_tracers: dict[str, Tracer] = {}
_tracers_lock = threading.Lock()


def get_tracer(
    name: str = "default",
    exporter: SpanExporter | None = None,
) -> Tracer:
    """Get or create a named tracer."""
    with _tracers_lock:
        if name not in _tracers:
            _tracers[name] = Tracer(name, exporter)
        return _tracers[name]


def trace(
    name: str | None = None,
    kind: SpanKind = SpanKind.INTERNAL,
    tracer_name: str = "default",
) -> Callable:
    """
    Decorator to trace a function.

    Usage:
        @trace("my_operation")
        def my_function():
            ...

        @trace()  # Uses function name
        def another_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        span_name = name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            tracer = get_tracer(tracer_name)
            with tracer.span(span_name, kind=kind) as span:
                span.set_attribute("function.name", func.__name__)
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_current_span() -> Span | None:
    """Get the current active span context."""
    context = getattr(_context_local, 'context', None)
    return context


__all__ = [
    # Enums
    "SpanKind",
    "SpanStatus",
    # Data classes
    "SpanContext",
    "Span",
    # Exporters
    "SpanExporter",
    "ConsoleExporter",
    "InMemoryExporter",
    # Tracer
    "Tracer",
    # Functions
    "get_tracer",
    "trace",
    "get_current_span",
]
