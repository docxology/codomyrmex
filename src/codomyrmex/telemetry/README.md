# telemetry

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

The `telemetry` module provides enterprise-grade observability for the Codomyrmex ecosystem. It is designed to be compatible with OpenTelemetry (OTLP) and provides structured tracing, span management, and context propagation across distributed components.

## Key Features

- **OpenTelemetry Compatibility**: Standardized tracing using OTLP.
- **Context Propagation**: Maintains trace continuity across asynchronous and distributed boundaries.
- **Custom Span Processors**: Extensible logic for span enrichment and filtering.
- **Distributed Observability**: Enables complex workflow analysis through parent-child span relationships.
- **Decorator Support**: Easy tracing of functions via `@traced`.

## Module Structure

- `trace_context.py` – Core logic for span management and context propagation.
- `otlp_exporter.py` – Exporting traces to OTLP collectors.
- `span_processor.py` – Custom processing and filtering of telemetry data.

## Implementation Standards

- **Zero Mocks**: Uses real OTLP-compatible structures.
- **Logging Integration**: Seamlessly attaches trace IDs to system logs.
- **Performance Focused**: Minimal overhead during span lifecycle.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
