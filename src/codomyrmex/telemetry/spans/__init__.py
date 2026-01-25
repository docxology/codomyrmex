"""
Telemetry span management.

Provides utilities for creating and managing distributed trace spans.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from contextlib import contextmanager
import uuid
import threading
import time


@dataclass
class SpanContext:
    """Context for a span in a distributed trace."""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    sampled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "sampled": self.sampled,
        }
    
    @classmethod
    def new_root(cls) -> 'SpanContext':
        """Create a new root span context."""
        return cls(
            trace_id=uuid.uuid4().hex,
            span_id=uuid.uuid4().hex[:16],
        )
    
    def child(self) -> 'SpanContext':
        """Create a child span context."""
        return SpanContext(
            trace_id=self.trace_id,
            span_id=uuid.uuid4().hex[:16],
            parent_span_id=self.span_id,
            sampled=self.sampled,
        )


@dataclass
class SpanEvent:
    """An event within a span."""
    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "attributes": self.attributes,
        }


@dataclass
class SpanLink:
    """A link to another span."""
    trace_id: str
    span_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


class SpanStatus:
    """Status of a span."""
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class Span:
    """A single span in a distributed trace."""
    
    def __init__(
        self,
        name: str,
        context: Optional[SpanContext] = None,
        kind: str = "internal",
    ):
        self.name = name
        self.context = context or SpanContext.new_root()
        self.kind = kind  # internal, server, client, producer, consumer
        
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.attributes: Dict[str, Any] = {}
        self.events: List[SpanEvent] = []
        self.links: List[SpanLink] = []
        self.status: str = SpanStatus.UNSET
        self.status_message: str = ""
    
    def start(self) -> 'Span':
        """Start the span."""
        self.start_time = datetime.now()
        return self
    
    def end(self) -> 'Span':
        """End the span."""
        self.end_time = datetime.now()
        return self
    
    def set_attribute(self, key: str, value: Any) -> 'Span':
        """Set an attribute on the span."""
        self.attributes[key] = value
        return self
    
    def set_attributes(self, attributes: Dict[str, Any]) -> 'Span':
        """Set multiple attributes."""
        self.attributes.update(attributes)
        return self
    
    def add_event(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> 'Span':
        """Add an event to the span."""
        self.events.append(SpanEvent(
            name=name,
            attributes=attributes or {},
        ))
        return self
    
    def add_link(
        self,
        context: SpanContext,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> 'Span':
        """Add a link to another span."""
        self.links.append(SpanLink(
            trace_id=context.trace_id,
            span_id=context.span_id,
            attributes=attributes or {},
        ))
        return self
    
    def set_status(self, status: str, message: str = "") -> 'Span':
        """Set the span status."""
        self.status = status
        self.status_message = message
        return self
    
    def record_exception(self, exception: Exception) -> 'Span':
        """Record an exception on the span."""
        self.add_event(
            "exception",
            {
                "exception.type": type(exception).__name__,
                "exception.message": str(exception),
            }
        )
        self.set_status(SpanStatus.ERROR, str(exception))
        return self
    
    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "kind": self.kind,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": [e.to_dict() for e in self.events],
            "status": self.status,
            "status_message": self.status_message,
        }


# Thread-local storage for current span
_current_span = threading.local()


def get_current_span() -> Optional[Span]:
    """Get the current span from context."""
    return getattr(_current_span, 'span', None)


def set_current_span(span: Optional[Span]) -> None:
    """Set the current span in context."""
    _current_span.span = span


class Tracer:
    """Creates and manages spans."""
    
    def __init__(
        self,
        name: str,
        on_span_end: Optional[Callable[[Span], None]] = None,
    ):
        self.name = name
        self.on_span_end = on_span_end
    
    def start_span(
        self,
        name: str,
        kind: str = "internal",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """Start a new span."""
        parent = get_current_span()
        
        if parent:
            context = parent.context.child()
        else:
            context = SpanContext.new_root()
        
        span = Span(name=name, context=context, kind=kind)
        
        if attributes:
            span.set_attributes(attributes)
        
        span.start()
        return span
    
    @contextmanager
    def span(
        self,
        name: str,
        kind: str = "internal",
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """Context manager for creating spans."""
        span = self.start_span(name, kind, attributes)
        previous = get_current_span()
        set_current_span(span)
        
        try:
            yield span
            if span.status == SpanStatus.UNSET:
                span.set_status(SpanStatus.OK)
        except Exception as e:
            span.record_exception(e)
            raise
        finally:
            span.end()
            set_current_span(previous)
            
            if self.on_span_end:
                self.on_span_end(span)
    
    def wrap(
        self,
        name: Optional[str] = None,
        kind: str = "internal",
    ):
        """Decorator to wrap a function with span creation."""
        def decorator(func: Callable) -> Callable:
            span_name = name or func.__name__
            
            def wrapper(*args, **kwargs):
                with self.span(span_name, kind):
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator


class SpanProcessor:
    """Processes completed spans."""
    
    def __init__(self):
        self._spans: List[Span] = []
        self._lock = threading.Lock()
    
    def process(self, span: Span) -> None:
        """Process a completed span."""
        with self._lock:
            self._spans.append(span)
    
    def get_spans(self) -> List[Span]:
        """Get all processed spans."""
        with self._lock:
            return list(self._spans)
    
    def clear(self) -> None:
        """Clear all spans."""
        with self._lock:
            self._spans.clear()
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace."""
        with self._lock:
            return [s for s in self._spans if s.context.trace_id == trace_id]


class BatchSpanProcessor(SpanProcessor):
    """Batch processes spans before export."""
    
    def __init__(
        self,
        exporter: Callable[[List[Span]], None],
        max_batch_size: int = 100,
        flush_interval: float = 5.0,
    ):
        super().__init__()
        self.exporter = exporter
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self._batch: List[Span] = []
        self._last_flush = time.time()
    
    def process(self, span: Span) -> None:
        """Add span to batch."""
        with self._lock:
            self._batch.append(span)
            
            if len(self._batch) >= self.max_batch_size:
                self._flush()
            elif time.time() - self._last_flush > self.flush_interval:
                self._flush()
    
    def _flush(self) -> None:
        """Flush the current batch."""
        if self._batch:
            self.exporter(self._batch)
            self._spans.extend(self._batch)
            self._batch = []
            self._last_flush = time.time()
    
    def force_flush(self) -> None:
        """Force flush pending spans."""
        with self._lock:
            self._flush()


def create_tracer(
    name: str = "default",
    processor: Optional[SpanProcessor] = None,
) -> Tracer:
    """Create a tracer with optional span processor."""
    if processor:
        return Tracer(name, on_span_end=processor.process)
    return Tracer(name)


__all__ = [
    "SpanContext",
    "SpanEvent",
    "SpanLink",
    "SpanStatus",
    "Span",
    "get_current_span",
    "set_current_span",
    "Tracer",
    "SpanProcessor",
    "BatchSpanProcessor",
    "create_tracer",
]
