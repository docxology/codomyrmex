"""Span exporters: SpanExporter ABC, ConsoleExporter, InMemoryExporter."""

import json
import threading
from abc import ABC, abstractmethod

from .models import Span


class SpanExporter(ABC):
    """Base class for span exporters."""

    @abstractmethod
    def export(self, spans: list[Span]) -> None:
        """Export spans."""

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown exporter."""


class ConsoleExporter(SpanExporter):
    """Export spans to console."""

    def __init__(self, pretty: bool = True):
        self.pretty = pretty

    def export(self, spans: list[Span]) -> None:
        """Export spans to stdout as JSON."""
        for span in spans:
            data = span.to_dict()
            if self.pretty:
                print(json.dumps(data, indent=2, default=str))
            else:
                print(json.dumps(data, default=str))

    def shutdown(self) -> None:
        """No-op shutdown for console exporter."""
        return  # Intentional no-op


class InMemoryExporter(SpanExporter):
    """Store spans in memory (useful for testing)."""

    def __init__(self, max_spans: int = 1000):
        self.max_spans = max_spans
        self.spans: list[Span] = []
        self._lock = threading.Lock()

    def export(self, spans: list[Span]) -> None:
        """Append spans, trimming to max_spans if needed."""
        with self._lock:
            self.spans.extend(spans)
            if len(self.spans) > self.max_spans:
                self.spans = self.spans[-self.max_spans :]

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
