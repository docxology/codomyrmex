"""OpenTelemetry-compatible span and metric collection.

Provides in-process tracing and metrics without requiring
an actual OTLP collector.
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


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
        status: Span status (``ok``, ``error``).
    """

    name: str
    trace_id: str = ""
    span_id: str = ""
    parent_id: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"

    def __post_init__(self) -> None:
        """post Init ."""
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex[:16]
        if not self.span_id:
            self.span_id = uuid.uuid4().hex[:8]
        if not self.start_time:
            self.start_time = time.time()

    @property
    def duration_ms(self) -> float:
        """duration Ms ."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def finish(self, status: str = "ok") -> None:
        """finish ."""
        self.end_time = time.time()
        self.status = status

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes,
        }


class Tracer:
    """In-process span tracer.

    Usage::

        tracer = Tracer()
        span = tracer.start_span("process_request")
        # ... do work ...
        span.finish()
        print(tracer.export())  # All completed spans
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._spans: list[Span] = []
        self._active_trace: str = ""

    def start_span(
        self,
        name: str,
        parent: Span | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """start Span ."""
        trace_id = parent.trace_id if parent else (self._active_trace or uuid.uuid4().hex[:16])
        span = Span(
            name=name,
            trace_id=trace_id,
            parent_id=parent.span_id if parent else "",
            attributes=attributes or {},
        )
        self._active_trace = trace_id
        self._spans.append(span)
        return span

    def export(self) -> list[dict[str, Any]]:
        """export ."""
        return [s.to_dict() for s in self._spans]

    @property
    def span_count(self) -> int:
        """span Count ."""
        return len(self._spans)

    def clear(self) -> None:
        """clear ."""
        self._spans.clear()


class MetricCounter:
    """Simple in-process metric counter.

    Tracks named counters and gauges.

    Usage::

        metrics = MetricCounter()
        metrics.increment("requests_total")
        metrics.gauge("active_connections", 42)
    """

    def __init__(self) -> None:
        """Initialize this instance."""
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}

    def increment(self, name: str, value: float = 1.0) -> None:
        """increment ."""
        self._counters[name] += value

    def gauge(self, name: str, value: float) -> None:
        """gauge ."""
        self._gauges[name] = value

    def get_counter(self, name: str) -> float:
        """get Counter ."""
        return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float | None:
        """get Gauge ."""
        return self._gauges.get(name)

    def export(self) -> dict[str, Any]:
        """export ."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }


__all__ = ["MetricCounter", "Span", "Tracer"]
