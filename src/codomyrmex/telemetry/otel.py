"""OpenTelemetry-compatible span and metric collection.

Provides in-process tracing and metrics without requiring
an actual OTLP collector.
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Generator, Optional

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# Context variable to track the current active span
_current_span: ContextVar[Optional["Span"]] = ContextVar("current_span", default=None)


@dataclass
class Span:
    """A tracing span.

    Attributes:
        name: Operation name.
        trace_id: Trace identifier.
        span_id: Span identifier.
        parent_id: Parent span ID (empty for root).
        start_time: Start timestamp.
        end_time: End timestamp.
        attributes: Span attributes.
        events: List of timed events.
        status: Span status (``ok``, ``error``).
    """

    name: str
    trace_id: str = ""
    span_id: str = ""
    parent_id: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    _token: Any = None

    def __post_init__(self) -> None:
        if not self.trace_id:
            # 128-bit trace ID (32 hex chars) is standard for OTLP
            self.trace_id = uuid.uuid4().hex
        if not self.span_id:
            # 64-bit span ID (16 hex chars)
            self.span_id = uuid.uuid4().hex[:16]
        if not self.start_time:
            self.start_time = time.time()

    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add a timed event to the span."""
        self.events.append(
            {
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {},
            }
        )

    def finish(self, status: str = "ok") -> None:
        """Finish the span."""
        if not self.end_time:
            self.end_time = time.time()
        self.status = status
        if self._token:
            _current_span.reset(self._token)
            self._token = None

    def __enter__(self) -> "Span":
        self._token = _current_span.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            self.status = "error"
            self.add_event(
                "exception",
                {"exception.type": exc_type.__name__, "exception.message": str(exc_val)},
            )
        self.finish(self.status)

    def to_dict(self) -> dict[str, Any]:
        """Convert to OTLP-compatible dictionary format."""
        return {
            "name": self.name,
            "context": {
                "trace_id": self.trace_id,
                "span_id": self.span_id,
            },
            "parent_id": self.parent_id,
            "start_time_unix_nano": int(self.start_time * 1e9),
            "end_time_unix_nano": int(self.end_time * 1e9) if self.end_time else None,
            "duration_ms": round(self.duration_ms, 2),
            "status": {"code": self.status.upper()},
            "attributes": self.attributes,
            "events": self.events,
        }


class Tracer:
    """In-process span tracer with context propagation.

    Usage::

        tracer = Tracer()
        with tracer.start_span("process_request") as span:
            # ... do work ...
            with tracer.start_span("sub_operation") as child:
                 child.set_attribute("key", "value")

        print(tracer.export())  # All completed spans
    """

    def __init__(self, service_name: str = "unknown_service") -> None:
        self.service_name = service_name
        self._spans: list[Span] = []

    def start_span(
        self,
        name: str,
        parent: Span | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """Start a new span. If parent is not provided, it looks in current context."""
        current = _current_span.get()
        effective_parent = parent or current

        trace_id = effective_parent.trace_id if effective_parent else uuid.uuid4().hex
        parent_id = effective_parent.span_id if effective_parent else ""

        span = Span(
            name=name,
            trace_id=trace_id,
            parent_id=parent_id,
            attributes=attributes or {},
        )
        self._spans.append(span)
        return span

    @contextmanager
    def start_as_current_span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[Span, None, None]:
        """Context manager that sets the span as current in the context."""
        with self.start_span(name, attributes=attributes) as span:
            yield span

    def export(self) -> list[dict[str, Any]]:
        """Export all recorded spans."""
        return [s.to_dict() for s in self._spans]

    @property
    def span_count(self) -> int:
        return len(self._spans)

    def clear(self) -> None:
        """Clear."""
        self._spans.clear()


class MetricCounter:
    """Simple in-process metric counter.

    Tracks named counters, gauges, and basic histograms.

    Usage::

        metrics = MetricCounter()
        metrics.increment("requests_total", labels={"method": "GET"})
        metrics.gauge("active_connections", 42)
        metrics.observe("latency", 0.123)
    """

    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)

    def _get_key(self, name: str, labels: dict[str, str] | None = None) -> str:
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def increment(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Increment a counter."""
        key = self._get_key(name, labels)
        self._counters[key] += value

    def gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Set a gauge."""
        key = self._get_key(name, labels)
        self._gauges[key] = value

    def observe(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """Record an observation."""
        key = self._get_key(name, labels)
        self._histograms[key].append(value)

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        return self._counters.get(self._get_key(name, labels), 0.0)

    def get_gauge(
        self, name: str, labels: dict[str, str] | None = None
    ) -> float | None:
        return self._gauges.get(self._get_key(name, labels))

    def export(self) -> dict[str, Any]:
        """Export metrics."""
        hist_stats = {}
        for name, values in self._histograms.items():
            if not values:
                continue
            sorted_v = sorted(values)
            hist_stats[name] = {
                "count": len(values),
                "sum": sum(values),
                "min": sorted_v[0],
                "max": sorted_v[-1],
                "mean": sum(values) / len(values),
            }

        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": hist_stats,
        }


__all__ = ["MetricCounter", "Span", "Tracer"]
