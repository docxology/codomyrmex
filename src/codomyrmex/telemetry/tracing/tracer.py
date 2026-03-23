"""Tracer: span lifecycle management, context propagation, and trace decorator."""

import functools
import threading
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

from .exporters import ConsoleExporter, SpanExporter
from .models import Span, SpanContext, SpanKind, _generate_id

T = TypeVar("T")

# Thread-local storage for active span context
_context_local = threading.local()


class Tracer:
    """
    Tracer for creating and managing spans.

    Usage:
        tracer = Tracer("my-service")

        with tracer.span("operation") as span:
            span.set_attribute("key", "value")
            # do work
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
        return getattr(_context_local, "context", None)

    def _set_current_context(self, context: SpanContext | None) -> None:
        """set current span context in thread-local storage."""
        _context_local.context = context

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent: SpanContext | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """Start a new span, inheriting parent context from thread-local if not provided."""
        parent_ctx = parent or self._get_current_context()

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
        span.set_attribute("service.name", self.service_name)
        return span

    @contextmanager
    def span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        **attributes,
    ) -> Generator[Span, None, None]:
        """Context manager that starts a span and exports it on exit."""
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
        """Buffer span and flush when 10 are pending."""
        with self._lock:
            self._pending_spans.append(span)
            if len(self._pending_spans) >= 10:
                self.exporter.export(self._pending_spans)
                self._pending_spans.clear()

    def flush(self) -> None:
        """Flush all pending spans."""
        with self._lock:
            if self._pending_spans:
                self.exporter.export(self._pending_spans)
                self._pending_spans.clear()

    def shutdown(self) -> None:
        """Flush and shut down the exporter."""
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
    """Decorator to trace a function call as a span."""

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
    return getattr(_context_local, "context", None)
