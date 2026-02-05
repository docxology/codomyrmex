# telemetry

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The telemetry module provides an OpenTelemetry-compatible observability framework for distributed tracing, metrics collection, span processing, and alerting. It supports trace context propagation, multiple span processors (simple and batch), OTLP export, sampling strategies, and configurable alerting -- enabling end-to-end visibility across distributed workflows.

## Key Exports

### Submodules (always available)

- **`exporters`** -- Telemetry data exporters including OTLP protocol support
- **`spans`** -- Span creation and processing (SimpleSpanProcessor, BatchSpanProcessor)
- **`metrics`** -- Metrics collection and reporting
- **`tracing`** -- Distributed tracing utilities
- **`sampling`** -- Trace sampling strategies for controlling data volume
- **`alerting`** -- Configurable alert rules and notification triggers

### Trace Context (conditionally available)

- **`TraceContext`** -- Manages distributed trace context propagation across service boundaries
- **`start_span()`** -- Create and start a new trace span
- **`get_current_span()`** -- Retrieve the currently active span from context
- **`traced`** -- Decorator for automatically tracing function execution
- **`link_span()`** -- Link related spans across trace boundaries

### Span Processors (conditionally available)

- **`SimpleSpanProcessor`** -- Synchronous span processor that exports spans immediately on completion
- **`BatchSpanProcessor`** -- Asynchronous span processor that batches spans for efficient bulk export

### Exporters (conditionally available)

- **`OTLPExporter`** -- Exports telemetry data using the OpenTelemetry Protocol (OTLP)

## Directory Contents

- `__init__.py` - Module entry point with conditional imports for optional components
- `context/` - Trace context propagation (`trace_context.py`)
- `exporters/` - Data exporters including OTLP (`otlp_exporter.py`)
- `spans/` - Span creation and processing (`span_processor.py`)
- `metrics/` - Metrics collection and aggregation
- `tracing/` - Distributed tracing utilities
- `sampling/` - Trace sampling strategies
- `alerting/` - Alert rule configuration and notification
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/telemetry/](../../../docs/modules/telemetry/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
