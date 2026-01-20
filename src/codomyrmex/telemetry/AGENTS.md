# Codomyrmex Agents — telemetry

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `telemetry` module enables agents to observe the execution flow of complex tasks. It provides the infrastructure to record spans, propagate context, and export performance data for analysis.

## Active Components

- `trace_context.py` – Manages the active span and trace ID lifecycle.
- `otlp_exporter.py` – Handles the transmission of telemetry data to external collectors.
- `span_processor.py` – Allows for real-time transformation of span data.

## Operating Contracts

1. **Trace Consistency**: Ensure Trace IDs are preserved across module boundaries.
2. **Context Integrity**: Never silence or drop spans unless explicitly configured for performance.
3. **Provider Agnostic**: Use OTLP standard interfaces to remain compatible with various backends (Jaeger, Honeycomb, Datadog).

## Core Interfaces

- `TraceContext`: Global or local management of trace state.
- `traced`: Decorator for automatic function instrumentation.
- `link_span`: Tool for manual context bridging.
- `Span`: Represents a single unit of work with attributes and timing.
- `OTLPExporter`: Interface for OTLP-compliant data export.

## Navigation Links

- **🏠 Project Root**: ../../../README.md
- **📦 Module README**: ./README.md
- **📜 Functional Spec**: ./SPEC.md
