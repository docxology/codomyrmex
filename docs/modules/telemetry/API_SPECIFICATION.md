# Telemetry - API Specification

## Introduction

The Telemetry module provides OpenTelemetry-compatible tracing and observability tools for the Codomyrmex framework. It enables distributed tracing, span management, and telemetry data export for monitoring and debugging applications.

## Endpoints / Functions / Interfaces

### Function 1: `start_span()`

- **Description**: Creates and starts a new trace span.
- **Method**: N/A (library function)
- **Parameters/Arguments**:
    - `name` (str): Name of the span.
    - `attributes` (dict, optional): Key-value attributes for the span.
    - `parent` (TraceContext, optional): Parent context for span linking.
- **Returns**:
    - `TraceContext`: Context object for the new span.
- **Events Emitted**:
    - `span_started`: Emitted when a span starts.

### Function 2: `get_current_span()`

- **Description**: Retrieves the currently active span from the context.
- **Method**: N/A (library function)
- **Returns**:
    - `TraceContext | None`: Current span context or None if no active span.

### Function 3: `traced()`

- **Description**: Decorator to automatically trace function execution.
- **Method**: N/A (decorator)
- **Parameters/Arguments**:
    - `name` (str, optional): Custom span name. Defaults to function name.
    - `attributes` (dict, optional): Additional span attributes.
- **Returns**:
    - `Callable`: Decorated function with automatic tracing.

### Function 4: `link_span()`

- **Description**: Links the current span to another span context.
- **Method**: N/A (library function)
- **Parameters/Arguments**:
    - `context` (TraceContext): Context to link to.
    - `attributes` (dict, optional): Link attributes.
- **Returns**:
    - `bool`: True if link was successful.

### Class: `TraceContext`

- **Description**: Represents a trace context with span information.
- **Methods**:
    - `set_attribute(key: str, value: Any)`: Set a span attribute.
    - `add_event(name: str, attributes: dict)`: Add an event to the span.
    - `end()`: End the current span.
    - `get_trace_id() -> str`: Get the trace ID.
    - `get_span_id() -> str`: Get the span ID.

### Class: `SimpleSpanProcessor`

- **Description**: Processes spans synchronously as they complete.
- **Methods**:
    - `on_start(span: Span)`: Called when a span starts.
    - `on_end(span: Span)`: Called when a span ends.
    - `shutdown()`: Shutdown the processor.

### Class: `BatchSpanProcessor`

- **Description**: Batches spans for efficient export.
- **Methods**:
    - `on_start(span: Span)`: Called when a span starts.
    - `on_end(span: Span)`: Called when a span ends.
    - `force_flush(timeout_ms: int)`: Force flush pending spans.
    - `shutdown()`: Shutdown the processor.

### Class: `OTLPExporter`

- **Description**: Exports spans to an OTLP-compatible backend.
- **Constructor**:
    - `endpoint` (str): OTLP collector endpoint.
    - `headers` (dict, optional): HTTP headers for authentication.
    - `timeout` (int, optional): Request timeout in milliseconds.
- **Methods**:
    - `export(spans: list[Span]) -> ExportResult`: Export spans to backend.
    - `shutdown()`: Shutdown the exporter.

## Data Models

### Model: `Span`
- `trace_id` (str): Unique trace identifier.
- `span_id` (str): Unique span identifier.
- `parent_span_id` (str | None): Parent span ID.
- `name` (str): Span name.
- `start_time` (float): Start timestamp.
- `end_time` (float | None): End timestamp.
- `attributes` (dict): Span attributes.
- `events` (list): Span events.
- `status` (SpanStatus): Span status.

### Model: `SpanStatus`
- `code` (StatusCode): OK, ERROR, or UNSET.
- `description` (str | None): Status description.

## Authentication & Authorization

OTLP exporters support header-based authentication for secure telemetry export. Configure appropriate headers when connecting to secured backends.

## Rate Limiting

The BatchSpanProcessor includes built-in rate limiting through configurable batch sizes and export intervals.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
