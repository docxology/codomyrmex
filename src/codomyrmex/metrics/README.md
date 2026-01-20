# metrics

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

The `metrics` module provides high-performance performance monitoring and instrumentation for Codomyrmex. It supports multiple backends (Prometheus, StatsD, In-Memory) and localized aggregation.

## Key Features

- **Multi-Backend Support**: Unified interface for Prometheus, StatsD, and local mocks.
- **Rich Metric Types**: Counter, Gauge, Histogram, and Summary statistics.
- **Aggregation Layer**: `MetricAggregator` for local buffering and snapshotting.
- **Standardized Export**: Seamless integration with the `telemetry` module.

## Module Structure

- `metrics.py` – Core metric type definitions and state management.
- `aggregator.py` – Local aggregation and snapshot logic.
- `prometheus_exporter.py` – Prometheus SCRAPE endpoint implementation.
- `statsd_client.py` – High-frequency StatsD UDP client.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
