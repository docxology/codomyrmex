# Technical Specification - Tracing

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.telemetry.tracing`  
**Last Updated**: 2026-01-29

## 1. Purpose

Distributed tracing setup helpers and context propagation

## 2. Architecture

### 2.1 Components

```
tracing/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `telemetry`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.telemetry.tracing
from codomyrmex.telemetry.tracing import (
    SpanKind,            # Enum: INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER
    SpanStatus,          # Enum: UNSET, OK, ERROR
    SpanContext,         # Dataclass for trace propagation (trace_id, span_id, baggage)
    Span,                # Dataclass representing a unit of work
    SpanExporter,        # ABC for span exporters
    ConsoleExporter,     # Export spans to console (pretty-print or compact JSON)
    InMemoryExporter,    # Store spans in memory (useful for testing)
    Tracer,              # Main tracer for creating and managing spans
    get_tracer,          # Get or create a named tracer from the global registry
    trace,               # Decorator to auto-trace a function
    get_current_span,    # Get the current active span from thread-local storage
)

# Key class signatures:
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    sampled: bool
    baggage: dict[str, str]
    def to_dict(self) -> dict[str, Any]: ...
    def to_headers(self) -> dict[str, str]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpanContext: ...
    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> SpanContext | None: ...

class Span:
    name: str
    context: SpanContext
    kind: SpanKind
    status: SpanStatus
    def set_attribute(self, key: str, value: Any) -> Span: ...
    def add_event(self, name: str, attributes: dict | None = None) -> Span: ...
    def set_status(self, status: SpanStatus, message: str = "") -> Span: ...
    def record_exception(self, exception: Exception) -> Span: ...
    def finish(self) -> None: ...
    def to_dict(self) -> dict[str, Any]: ...

class Tracer:
    def __init__(self, service_name: str = "default", exporter: SpanExporter | None = None): ...
    def start_span(self, name: str, kind: SpanKind = SpanKind.INTERNAL, ...) -> Span: ...
    def span(self, name: str, kind: SpanKind = SpanKind.INTERNAL, **attributes) -> ContextManager[Span]: ...
    def flush(self) -> None: ...
    def shutdown(self) -> None: ...

def get_tracer(name: str = "default", exporter: SpanExporter | None = None) -> Tracer: ...
def trace(name: str | None = None, kind: SpanKind = SpanKind.INTERNAL, tracer_name: str = "default") -> Callable: ...
def get_current_span() -> Span | None: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Thread-local context propagation**: Span context is stored in `threading.local()` for automatic parent-child linking without explicit context passing.
2. **Batched export**: Spans are buffered and exported in batches of 10 to reduce exporter overhead in high-throughput scenarios.
3. **OpenTelemetry-aligned model**: `SpanKind`, `SpanStatus`, and the `SpanContext` propagation pattern follow OpenTelemetry conventions for future interop.

### 4.2 Limitations

- Known limitation 1
- Known limitation 2

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/telemetry/tracing/
```

## 6. Future Considerations

- Add OTLP/gRPC exporter for integration with Jaeger, Zipkin, and other backends
- Support async span export with configurable flush intervals
- Add W3C TraceContext header propagation (`traceparent` / `tracestate`)
