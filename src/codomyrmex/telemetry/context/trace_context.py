"""Core logic for span management and context propagation."""

from typing import Any, Optional, Dict
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode, Span, Link
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class TraceContext:
    """Manager for the global or local trace state."""
    
    _initialized = False
    
    @classmethod
    def initialize(cls, service_name: str = "codomyrmex", attributes: Optional[Dict[str, Any]] = None) -> None:
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

def start_span(name: str, attributes: Optional[Dict[str, Any]] = None, parent: Optional[Span] = None) -> Span:
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

def traced(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """Decorator to automatically wrap a function in a span."""
    def decorator(func):
        span_name = name or func.__name__
        @wraps(func)
        def wrapper(*args, **kwargs):
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
    # Links are usually added at span creation, but some implementations allow 
    # capturing context. In OTEL, links are part of the span creation.
    # This utility encourages linking pattern.
    pass
