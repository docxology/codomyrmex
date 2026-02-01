"""Telemetry module for Codomyrmex.

This module provides OpenTelemetry-compatible tracing and observability tools.
"""

# Submodule exports - import first
from . import exporters
from . import spans
from . import metrics

# Try optional submodules
try:
    from . import context
except ImportError:
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .context.trace_context import (
        TraceContext,
        start_span,
        get_current_span,
        traced,
        link_span,
    )
    HAS_TRACE_CONTEXT = True
except ImportError:
    HAS_TRACE_CONTEXT = False
    TraceContext = None

try:
    from .spans.span_processor import (
        SimpleSpanProcessor,
        BatchSpanProcessor,
    )
    HAS_SPAN_PROCESSOR = True
except ImportError:
    HAS_SPAN_PROCESSOR = False

try:
    from .exporters.otlp_exporter import OTLPExporter
    HAS_OTLP_EXPORTER = True
except ImportError:
    HAS_OTLP_EXPORTER = False
    OTLPExporter = None

from . import tracing
from . import sampling
from . import alerting
__all__ = [
    'alerting',
    'sampling',
    'tracing',
    "exporters",
    "spans",
    "metrics",
]

if HAS_TRACE_CONTEXT:
    __all__.extend(["TraceContext", "start_span", "get_current_span", "traced", "link_span"])
if HAS_SPAN_PROCESSOR:
    __all__.extend(["SimpleSpanProcessor", "BatchSpanProcessor"])
if HAS_OTLP_EXPORTER:
    __all__.append("OTLPExporter")

__version__ = "0.1.0"
