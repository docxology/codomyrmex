"""
Tests for Telemetry Tracing Module
"""

import pytest
import time
from codomyrmex.telemetry.tracing import (
    Tracer,
    Span,
    SpanContext,
    SpanKind,
    SpanStatus,
    InMemoryExporter,
    get_tracer,
    trace,
)


class TestSpanContext:
    """Tests for SpanContext."""
    
    def test_to_dict(self):
        """Should convert to dict."""
        ctx = SpanContext(
            trace_id="trace123",
            span_id="span456",
            parent_span_id="parent789",
        )
        
        data = ctx.to_dict()
        assert data["trace_id"] == "trace123"
        assert data["span_id"] == "span456"
        assert data["parent_span_id"] == "parent789"
    
    def test_from_dict(self):
        """Should create from dict."""
        ctx = SpanContext.from_dict({
            "trace_id": "trace123",
            "span_id": "span456",
        })
        
        assert ctx.trace_id == "trace123"
        assert ctx.span_id == "span456"
    
    def test_to_headers(self):
        """Should convert to HTTP headers."""
        ctx = SpanContext(
            trace_id="trace123",
            span_id="span456",
        )
        
        headers = ctx.to_headers()
        assert headers["X-Trace-Id"] == "trace123"
        assert headers["X-Span-Id"] == "span456"
    
    def test_from_headers(self):
        """Should extract from HTTP headers."""
        ctx = SpanContext.from_headers({
            "X-Trace-Id": "trace123",
            "X-Span-Id": "span456",
        })
        
        assert ctx is not None
        assert ctx.trace_id == "trace123"
        assert ctx.span_id == "span456"
    
    def test_from_headers_missing(self):
        """Should return None if headers missing."""
        ctx = SpanContext.from_headers({})
        assert ctx is None


class TestSpan:
    """Tests for Span."""
    
    def test_create_span(self):
        """Should create a span."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        assert span.name == "test"
        assert span.trace_id == "t"
        assert span.span_id == "s"
    
    def test_set_attribute(self):
        """Should set attribute."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        span.set_attribute("key", "value")
        assert span.attributes["key"] == "value"
    
    def test_add_event(self):
        """Should add event."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        span.add_event("my_event", {"foo": "bar"})
        assert len(span.events) == 1
        assert span.events[0]["name"] == "my_event"
    
    def test_set_status(self):
        """Should set status."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        span.set_status(SpanStatus.OK, "all good")
        assert span.status == SpanStatus.OK
        assert span.status_message == "all good"
    
    def test_record_exception(self):
        """Should record exception."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        span.record_exception(ValueError("test error"))
        assert span.status == SpanStatus.ERROR
        assert len(span.events) == 1
        assert span.events[0]["name"] == "exception"
    
    def test_finish(self):
        """Should set end time."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        assert span.end_time is None
        span.finish()
        assert span.end_time is not None
    
    def test_duration(self):
        """Should calculate duration."""
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        time.sleep(0.01)
        span.finish()
        
        assert span.duration_ms >= 10


class TestTracer:
    """Tests for Tracer."""
    
    def test_create_tracer(self):
        """Should create tracer."""
        tracer = Tracer("test-service")
        assert tracer.service_name == "test-service"
    
    def test_start_span(self):
        """Should start a span."""
        tracer = Tracer("test-service")
        span = tracer.start_span("operation")
        
        assert span.name == "operation"
        assert span.trace_id is not None
        assert span.span_id is not None
        assert span.attributes["service.name"] == "test-service"
    
    def test_span_context_manager(self):
        """Context manager should work."""
        exporter = InMemoryExporter()
        tracer = Tracer("test-service", exporter=exporter)
        
        with tracer.span("operation") as span:
            span.set_attribute("key", "value")
        
        # Force flush
        tracer.flush()
        
        assert len(exporter.spans) == 1
        assert exporter.spans[0].attributes["key"] == "value"
    
    def test_nested_spans(self):
        """Nested spans should inherit trace ID."""
        exporter = InMemoryExporter()
        tracer = Tracer("test-service", exporter=exporter)
        
        with tracer.span("outer") as outer:
            with tracer.span("inner") as inner:
                pass
        
        tracer.flush()
        
        assert len(exporter.spans) == 2
        # Both should have same trace ID
        assert exporter.spans[0].trace_id == exporter.spans[1].trace_id
    
    def test_exception_handling(self):
        """Context manager should handle exceptions."""
        exporter = InMemoryExporter()
        tracer = Tracer("test-service", exporter=exporter)
        
        try:
            with tracer.span("operation") as span:
                raise ValueError("test error")
        except ValueError:
            pass
        
        tracer.flush()
        
        assert len(exporter.spans) == 1
        assert exporter.spans[0].status == SpanStatus.ERROR


class TestInMemoryExporter:
    """Tests for InMemoryExporter."""
    
    def test_export(self):
        """Should export spans."""
        exporter = InMemoryExporter()
        ctx = SpanContext(trace_id="t", span_id="s")
        span = Span(name="test", context=ctx)
        
        exporter.export([span])
        
        assert len(exporter.spans) == 1
    
    def test_max_spans(self):
        """Should limit stored spans."""
        exporter = InMemoryExporter(max_spans=2)
        
        for i in range(5):
            ctx = SpanContext(trace_id=f"t{i}", span_id=f"s{i}")
            span = Span(name=f"test{i}", context=ctx)
            exporter.export([span])
        
        assert len(exporter.spans) == 2
    
    def test_get_spans_filtered(self):
        """Should filter by trace ID."""
        exporter = InMemoryExporter()
        
        ctx1 = SpanContext(trace_id="t1", span_id="s1")
        ctx2 = SpanContext(trace_id="t2", span_id="s2")
        exporter.export([Span(name="a", context=ctx1)])
        exporter.export([Span(name="b", context=ctx2)])
        
        filtered = exporter.get_spans("t1")
        assert len(filtered) == 1
        assert filtered[0].trace_id == "t1"


class TestTraceDecorator:
    """Tests for trace decorator."""
    
    def test_decorator(self):
        """Decorator should trace function."""
        @trace("my_operation", tracer_name="test")
        def my_func():
            return 42
        
        result = my_func()
        assert result == 42
    
    def test_decorator_uses_function_name(self):
        """Decorator should use function name if not specified."""
        @trace(tracer_name="test")
        def another_func():
            return "result"
        
        result = another_func()
        assert result == "result"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
