"""Custom span processing logic."""

from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor as OTSimpleSpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor as OTBatchSpanProcessor
from opentelemetry.trace import Span as TraceSpan
from opentelemetry import trace

class SimpleSpanProcessor(OTSimpleSpanProcessor):
    """Processor that exports spans immediately."""
    pass

class BatchSpanProcessor(OTBatchSpanProcessor):
    """Processor that batches spans before exporting."""
    pass

def add_span_processor(processor: SpanProcessor) -> None:
    """Add a span processor to the global tracer provider."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, "add_span_processor"):
        provider.add_span_processor(processor)
