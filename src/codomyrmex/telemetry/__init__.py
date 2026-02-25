"""Telemetry module for Codomyrmex.

This module provides OpenTelemetry-compatible tracing and observability tools.


Submodules:
    dashboard: Consolidated dashboard capabilities.
    metrics: Consolidated metrics capabilities."""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Submodule exports - import first
from . import exporters, metrics, spans

# Try optional submodules
try:
    from . import context
except ImportError:
    pass

# Try to import from existing modules, but don't fail if they don't exist
try:
    from .context.trace_context import (
        TraceContext,
        get_current_span,
        link_span,
        start_span,
        traced,
    )
    HAS_TRACE_CONTEXT = True
except ImportError:
    HAS_TRACE_CONTEXT = False
    TraceContext = None

try:
    from .spans.span_processor import (
        BatchSpanProcessor,
        SimpleSpanProcessor,
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

from . import alerting, sampling, tracing


def cli_commands():
    """Return CLI commands for the telemetry module."""
    def _status(**kwargs):
        """Show telemetry status."""
        print("=== Telemetry Status ===")
        print(f"  Trace context: {'available' if HAS_TRACE_CONTEXT else 'not available'}")
        print(f"  Span processor: {'available' if HAS_SPAN_PROCESSOR else 'not available'}")
        print(f"  OTLP exporter: {'available' if HAS_OTLP_EXPORTER else 'not available'}")
        print("  Alerting module: loaded")
        print("  Sampling module: loaded")

    def _export(**kwargs):
        """Export telemetry data."""
        print("=== Telemetry Export ===")
        if HAS_OTLP_EXPORTER:
            print("  OTLP exporter is available for data export")
            print("  Use OTLPExporter class to configure export targets")
        else:
            print("  OTLP exporter not available (install opentelemetry dependencies)")
        print("  Span processors: " + (
            "BatchSpanProcessor, SimpleSpanProcessor" if HAS_SPAN_PROCESSOR
            else "not available"
        ))

    return {
        "status": {"handler": _status, "help": "Show telemetry status"},
        "export": {"handler": _export, "help": "Export telemetry data"},
    }


from . import dashboard

__all__ = [
    "dashboard",
    'alerting',
    'sampling',
    'tracing',
    "exporters",
    "spans",
    "metrics",
    "cli_commands",
]

if HAS_TRACE_CONTEXT:
    __all__.extend(["TraceContext", "start_span", "get_current_span", "traced", "link_span"])
if HAS_SPAN_PROCESSOR:
    __all__.extend(["SimpleSpanProcessor", "BatchSpanProcessor"])
if HAS_OTLP_EXPORTER:
    __all__.append("OTLPExporter")

__version__ = "0.1.0"
