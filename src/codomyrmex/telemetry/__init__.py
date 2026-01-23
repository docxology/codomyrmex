"""Telemetry module for Codomyrmex.

This module provides OpenTelemetry-compatible tracing and observability tools.
"""

from .context.trace_context import (
    TraceContext,
    start_span,
    get_current_span,
    traced,
    link_span,
)
from .spans.span_processor import (
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from .exporters.otlp_exporter import (
    OTLPExporter,
)

# Submodule exports
from . import exporters
from . import spans
from . import context
from . import metrics

__all__ = [
    "TraceContext",
    "start_span",
    "get_current_span",
    "traced",
    "link_span",
    "SimpleSpanProcessor",
    "BatchSpanProcessor",
    "OTLPExporter",
    "exporters",
    "spans",
    "context",
    "metrics",
]

