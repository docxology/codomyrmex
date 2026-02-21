# Telemetry Module Documentation

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Telemetry module provides a unified observability framework based on the OpenTelemetry standard. It enables the system to record, correlate, and analyze the performance and behavior of distributed workflows through tracing, span management, context propagation, metrics collection, and OTLP-compatible export. The module integrates with OpenTelemetry SDKs when available and provides standalone tracing capabilities for environments without the full OTEL stack.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Distributed Tracing**: Full span lifecycle management with parent-child relationships, context propagation via thread-local storage and HTTP headers
- **OpenTelemetry Integration**: `TraceContext` class wrapping OpenTelemetry `TracerProvider` for standardized trace initialization
- **Span Processing**: Simple (immediate) and batch span processors for controlling export behavior
- **OTLP Export**: HTTP-based export to OTLP collectors with configurable endpoint and environment variable support
- **Standalone Tracer**: Built-in `Tracer` class with console and in-memory exporters for use without external OTEL dependencies
- **Function Tracing Decorators**: `@trace()` and `@traced()` decorators for automatic span creation around function calls
- **Sampling**: Dynamic sampling strategies submodule for high-volume telemetry (early development)
- **Alerting**: Alert rule configuration and notification routing submodule (early development)
- **Graceful Degradation**: Optional submodules load conditionally with availability flags, preventing import failures


## Key Components

### Context (`context/`)

| Component | Description |
|-----------|-------------|
| `TraceContext` | Manager for global trace state; initializes `TracerProvider` with service name and resource attributes |
| `start_span()` | Create a new span with optional attributes and parent span |
| `get_current_span()` | Retrieve the currently active span from the trace context |
| `traced()` | Decorator that automatically wraps a function in a span with exception recording |
| `link_span()` | Utility for linking related spans (e.g., async producer/consumer patterns) |

### Tracing (`tracing/`)

| Component | Description |
|-----------|-------------|
| `Tracer` | Standalone tracer with context manager span creation, batched export, and thread-local context propagation |
| `Span` | Trace span dataclass with attributes, events, status, exception recording, and duration tracking |
| `SpanContext` | Context for trace propagation with trace/span IDs, sampling flag, and HTTP header serialization |
| `SpanKind` | Enum: `INTERNAL`, `SERVER`, `CLIENT`, `PRODUCER`, `CONSUMER` |
| `SpanStatus` | Enum: `UNSET`, `OK`, `ERROR` |
| `SpanExporter` | Base class for span exporters |
| `ConsoleExporter` | Exports spans as JSON to stdout |
| `InMemoryExporter` | Stores spans in memory with size limit (useful for testing) |
| `get_tracer()` | Get or create a named tracer from the global registry |
| `trace()` | Decorator for automatic function tracing with configurable span name and kind |

### Spans (`spans/`)

| Component | Description |
|-----------|-------------|
| `SimpleSpanProcessor` | Processes and exports spans immediately upon completion |
| `BatchSpanProcessor` | Batches spans before exporting for improved performance |

### Exporters (`exporters/`)

| Component | Description |
|-----------|-------------|
| `OTLPExporter` | HTTP-based exporter that sends spans to an OTLP collector (default: `http://localhost:4318/v1/traces`, configurable via `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` environment variable) |

### Metrics (`metrics/`)

| Component | Description |
|-----------|-------------|
| `metrics` | Metrics collection submodule (early development) |

### Sampling (`sampling/`)

| Component | Description |
|-----------|-------------|
| `sampling` | Dynamic sampling strategies for high-volume telemetry (early development) |

### Alerting (`alerting/`)

| Component | Description |
|-----------|-------------|
| `alerting` | Alert rule configuration and notification routing (early development) |

### Availability Flags

| Flag | Description |
|------|-------------|
| `HAS_TRACE_CONTEXT` | Whether the OpenTelemetry-based `TraceContext` and related functions are available |
| `HAS_SPAN_PROCESSOR` | Whether `SimpleSpanProcessor` and `BatchSpanProcessor` are available |
| `HAS_OTLP_EXPORTER` | Whether the `OTLPExporter` is available |

## Quick Start

### Standalone Tracing (No OTEL Dependencies)

```python
from codomyrmex.telemetry.tracing import Tracer, InMemoryExporter, trace

# Create a tracer with in-memory export
exporter = InMemoryExporter()
tracer = Tracer("my-service", exporter=exporter)

# Use context manager for spans
with tracer.span("process-data") as span:
    span.set_attribute("input.size", 1024)
    # Do work...

# Use decorator for automatic tracing
@trace("my_operation")
def my_function():
    pass

# Flush and inspect
tracer.flush()
spans = exporter.get_spans()
```

### OpenTelemetry Integration

```python
from codomyrmex.telemetry import TraceContext, start_span, traced

# Initialize global tracer provider
TraceContext.initialize(service_name="my-service")

# Create spans manually
span = start_span("operation", attributes={"key": "value"})
try:
    # Do work...
    pass
finally:
    span.end()

# Use decorator for automatic instrumentation
@traced("process_request")
def handle_request(data):
    return process(data)
```

### OTLP Export

```python
from codomyrmex.telemetry import OTLPExporter, SimpleSpanProcessor, TraceContext
from opentelemetry import trace

# Initialize with OTLP export
TraceContext.initialize(service_name="my-service")

exporter = OTLPExporter(endpoint="http://collector:4318/v1/traces")
processor = SimpleSpanProcessor(exporter)

provider = trace.get_tracer_provider()
provider.add_span_processor(processor)
```

## Related Modules

- [logging_monitoring](../logging_monitoring/) - Structured logging that complements trace-based observability
- [metrics](../metrics/) - Metrics collection and aggregation
- [concurrency](../concurrency/) - Lock manager statistics integrate with telemetry

## Navigation

- **Source**: [src/codomyrmex/telemetry/](../../../src/codomyrmex/telemetry/)
- **Parent**: [docs/modules/](../README.md)
