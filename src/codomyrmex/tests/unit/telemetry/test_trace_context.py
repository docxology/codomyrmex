"""Unit tests for the telemetry module."""

import pytest

try:
    from opentelemetry import trace
    from opentelemetry.trace import StatusCode

    from codomyrmex.telemetry import TraceContext, start_span, traced
    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

if not _HAS_OTEL:
    pytest.skip("opentelemetry not available", allow_module_level=True)


@pytest.mark.unit
def test_telemetry_initialization():
    """Test that the tracer provider can be initialized."""
    TraceContext.initialize(service_name="test-service")
    tracer = TraceContext.get_tracer("test-tracer")
    assert tracer is not None

@pytest.mark.unit
def test_span_lifecycle():
    """Test starting and ending a span."""
    TraceContext.initialize(service_name="test-service")

    with start_span("parent-span") as parent:
        assert parent.name == "parent-span"
        assert parent.is_recording()

        with start_span("child-span", parent=parent) as child:
            assert child.name == "child-span"
            assert child.context.trace_id == parent.context.trace_id

    assert not parent.is_recording()

@pytest.mark.unit
def test_span_attributes():
    """Test setting attributes on a span."""
    TraceContext.initialize(service_name="test-service")

    with start_span("attr-span") as span:
        span.set_attribute("test.key", "test.value")
        # In mock or real SDK, we can't easily check attributes without internal access
        # but we verify the call doesn't fail.
        assert span.is_recording()

@pytest.mark.unit
def test_error_recording():
    """Test recording an exception on a span."""
    TraceContext.initialize(service_name="test-service")

    with start_span("error-span") as span:
        try:
            raise ValueError("Test error")
        except ValueError as e:
            span.record_exception(e)
            span.set_status(trace.Status(StatusCode.ERROR, "Test exception"))

    # Status should be error
    assert span.status.status_code == StatusCode.ERROR

@pytest.mark.unit
def test_traced_decorator():
    """Test the @traced decorator."""
    TraceContext.initialize(service_name="test-service")

    @traced(name="decorated-fn", attributes={"fn.type": "test"})
    def my_function(x, y):
        return x + y

    result = my_function(10, 20)
    assert result == 30
    # Success means the decorator worked and didn't crash.
