# tracing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Distributed tracing, span management, and context propagation for the telemetry module. Implements an OpenTelemetry-inspired tracing system with hierarchical spans, trace context propagation via HTTP headers, thread-local context storage, pluggable span exporters (console and in-memory), automatic parent-child span linking, a context manager API for scoped spans, a `@trace` decorator for function-level instrumentation, and a global tracer registry.

## Key Exports

- **`SpanKind`** -- Enum of span types: INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER
- **`SpanStatus`** -- Enum of span statuses: UNSET, OK, ERROR
- **`SpanContext`** -- Dataclass for trace propagation carrying trace_id, span_id, parent_span_id, sampled flag, and baggage; supports serialization to/from dicts and HTTP headers
- **`Span`** -- Dataclass representing a unit of work with name, context, kind, status, start/end times, attributes, events, duration, exception recording, and dict serialization
- **`SpanExporter`** -- Base class for span exporters with export() and shutdown() methods
- **`ConsoleExporter`** -- Exporter that prints span data to stdout as JSON (supports pretty-printing)
- **`InMemoryExporter`** -- Thread-safe exporter that stores spans in memory with configurable max capacity; supports filtered retrieval by trace_id (useful for testing)
- **`Tracer`** -- Main tracer: creates spans with automatic parent context detection via thread-local storage, provides a `span()` context manager with automatic exception recording and context restoration, batch-exports finished spans, and supports flush/shutdown lifecycle
- **`get_tracer()`** -- Get or create a named tracer from the global tracer registry (thread-safe singleton per name)
- **`trace()`** -- Decorator that wraps a function in an automatically traced span, using the function name as the default span name
- **`get_current_span()`** -- Retrieve the current active span context from thread-local storage

## Directory Contents

- `__init__.py` - All tracing classes, enums, dataclasses, exporters, tracer, and decorator
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [telemetry](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
