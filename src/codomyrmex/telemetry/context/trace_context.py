"""Core logic for span management and context propagation."""

from functools import wraps
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Span, Status, StatusCode

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class TraceContext:
    """Manager for the global or local trace state."""

    _initialized = False

    @classmethod
    def initialize(cls, service_name: str = "codomyrmex", attributes: dict[str, Any] | None = None) -> None:
        """Initialize the global tracer provider."""
        if cls._initialized:
            return

        resource = Resource.create(attributes={
            "service.name": service_name,
            **(attributes or {})
        })

        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
        cls._initialized = True
        logger.info(f"Telemetry initialized for service: {service_name}")

    @staticmethod
    def get_tracer(name: str = "codomyrmex") -> trace.Tracer:
        """Get a tracer instance."""
        return trace.get_tracer(name)

def start_span(name: str, attributes: dict[str, Any] | None = None, parent: Span | None = None) -> Span:
    """Start a new span.

    Args:
        name: Name of the span.
        attributes: Initial attributes for the span.
        parent: Optional parent span for nesting.

    Returns:
        The started span.
    """
    tracer = TraceContext.get_tracer()

    # If a parent is provided, we use it as the context for the new span
    if parent:
        context = trace.set_span_in_context(parent)
        return tracer.start_span(name, attributes=attributes, context=context)

    return tracer.start_span(name, attributes=attributes)

def get_current_span() -> Span:
    """Get the currently active span."""
    return trace.get_current_span()

def record_exception(span: Span, exception: Exception, escaped: bool = True) -> None:
    """Record an exception on the span and set status to ERROR."""
    span.record_exception(exception, escaped=escaped)
    span.set_status(Status(StatusCode.ERROR, str(exception)))

def traced(name: str | None = None, attributes: dict[str, Any] | None = None):
    """Decorator to automatically wrap a function in a span."""
    def decorator(func):
        """Decorator."""
        span_name = name or func.__name__
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper."""
            tracer = TraceContext.get_tracer()
            with tracer.start_as_current_span(span_name, attributes=attributes) as span:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    record_exception(span, e)
                    raise
        return wrapper
    return decorator

def link_span(span: Span, target: Span) -> None:
    """Link two spans together (e.g. for async producer/consumer)."""
    # OpenTelemetry prefers links at creation, but we can emit a linked event
    # as a functional fallback to support post-creation linkage semantics.
    if hasattr(target, "get_span_context"):
        ctx = target.get_span_context()
        span.add_event(
            "linked_span",
            attributes={
                "linked_trace_id": format(ctx.trace_id, "032x"),
                "linked_span_id": format(ctx.span_id, "016x")
            }
        )
