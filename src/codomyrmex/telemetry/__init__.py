"""Telemetry module for Codomyrmex.

This module provides OpenTelemetry-compatible tracing and observability tools.
"""

from .trace_context import (
    TraceContext,
    start_span,
    get_current_span,
    traced,
    link_span,
)
from .span_processor import (
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from .otlp_exporter import (
    OTLPExporter,
)

__all__ = [
    "TraceContext",
    "start_span",
    "get_current_span",
    "traced",
    "link_span",
    "SimpleSpanProcessor",
    "BatchSpanProcessor",
    "OTLPExporter",
]
