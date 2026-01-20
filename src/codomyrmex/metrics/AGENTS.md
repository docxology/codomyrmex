# Codomyrmex Agents — metrics

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The `metrics` module provides the instrumentation layer for agents to monitor system performance and health. It allows for recording high-fidelity metrics with minimal overhead.

## Active Components

- `metrics.py` – Core instrumentation primitives (Counter, Gauge, Histogram, Summary).
- `aggregator.py` – Local multi-metric aggregation and snapshotting.
- `prometheus_exporter.py` – Interface for external time-series database scraping.
- `statsd_client.py` – High-frequency metrics transmission via UDP.

## Operating Contracts

1. **Performance First**: Metric collection must not block the main execution flow.
2. **Standardization**: Use consistent label naming conventions across all modules.
3. **Observability**: Metrics should be easily correlated with telemetry traces.

## Core Interfaces

- `Metrics`: Primary manager for creating and exporting metrics.
- `MetricAggregator`: Utility for localized metric buffering.
- `Counter / Gauge / Histogram`: Individual metric types for recording data.

## Navigation Links

- **🏠 Project Root**: ../../../README.md
- **📦 Module README**: ./README.md
- **📜 Functional Spec**: ./SPEC.md
