"""Unified observability pipeline.

Correlates spans, metrics, logs, and audit events by
correlation_id for end-to-end traceability.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventKind(Enum):
    """Kind of observability event."""

    SPAN = "span"
    METRIC = "metric"
    LOG = "log"
    AUDIT = "audit"


@dataclass
class ObservabilityEvent:
    """A single observability event.

    Attributes:
        event_id: Unique event identifier.
        kind: Event type.
        name: Event name.
        data: Event payload.
        correlation_id: Correlation identifier.
        timestamp: Event creation time.
        source: Event source.
        duration_ms: Duration (for spans).
    """

    event_id: str = ""
    kind: EventKind = EventKind.LOG
    name: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    duration_ms: float = 0.0

    def __post_init__(self) -> None:
        if not self.event_id:
            self.event_id = f"evt-{uuid.uuid4().hex[:10]}"


class ObservabilityPipeline:
    """Unified pipeline correlating spans, metrics, logs, audit.

    Example::

        pipeline = ObservabilityPipeline()
        cid = pipeline.start_correlation()
        pipeline.record_span("api.request", cid, duration_ms=42)
        pipeline.record_metric("latency_ms", cid, value=42)
        pipeline.record_log("info", cid, message="handled")
        events = pipeline.get_correlated(cid)
    """

    def __init__(self) -> None:
        self._events: list[ObservabilityEvent] = []
        self._by_correlation: dict[str, list[ObservabilityEvent]] = {}

    @property
    def event_count(self) -> int:
        return len(self._events)

    def start_correlation(self) -> str:
        """Generate a new correlation ID."""
        return f"cor-{uuid.uuid4().hex[:12]}"

    def record_span(
        self, name: str, correlation_id: str = "",
        duration_ms: float = 0.0, source: str = "",
        data: dict[str, Any] | None = None,
    ) -> ObservabilityEvent:
        """Record a span event."""
        return self._record(
            EventKind.SPAN, name, correlation_id,
            duration_ms=duration_ms, source=source, data=data,
        )

    def record_metric(
        self, name: str, correlation_id: str = "",
        value: float = 0.0, source: str = "",
        data: dict[str, Any] | None = None,
    ) -> ObservabilityEvent:
        """Record a metric event."""
        d = data or {}
        d["value"] = value
        return self._record(EventKind.METRIC, name, correlation_id, source=source, data=d)

    def record_log(
        self, level: str, correlation_id: str = "",
        message: str = "", source: str = "",
        data: dict[str, Any] | None = None,
    ) -> ObservabilityEvent:
        """Record a log event."""
        d = data or {}
        d["level"] = level
        d["message"] = message
        return self._record(EventKind.LOG, f"log.{level}", correlation_id, source=source, data=d)

    def record_audit(
        self, action: str, correlation_id: str = "",
        actor: str = "", source: str = "",
        data: dict[str, Any] | None = None,
    ) -> ObservabilityEvent:
        """Record an audit event."""
        d = data or {}
        d["action"] = action
        d["actor"] = actor
        return self._record(EventKind.AUDIT, f"audit.{action}", correlation_id, source=source, data=d)

    def get_correlated(self, correlation_id: str) -> list[ObservabilityEvent]:
        """Get all events for a correlation ID."""
        return list(self._by_correlation.get(correlation_id, []))

    def get_by_kind(self, kind: EventKind) -> list[ObservabilityEvent]:
        """Get all events of a specific kind."""
        return [e for e in self._events if e.kind == kind]

    def _record(
        self, kind: EventKind, name: str, correlation_id: str,
        duration_ms: float = 0.0, source: str = "",
        data: dict[str, Any] | None = None,
    ) -> ObservabilityEvent:
        event = ObservabilityEvent(
            kind=kind, name=name, correlation_id=correlation_id,
            duration_ms=duration_ms, source=source, data=data or {},
        )
        self._events.append(event)
        if correlation_id:
            self._by_correlation.setdefault(correlation_id, []).append(event)
        return event


__all__ = ["EventKind", "ObservabilityEvent", "ObservabilityPipeline"]
