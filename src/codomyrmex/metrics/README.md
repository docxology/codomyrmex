# metrics

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Metrics collection, aggregation, and export module for Codomyrmex. Provides four standard metric types (Counter, Gauge, Histogram, Summary) with an in-memory backend and optional integration with Prometheus and StatsD for external monitoring. The `MetricAggregator` class enables local metric buffering with snapshot and reset capabilities before pushing to external systems.

## Key Exports

- **`Metrics`** -- Central metrics registry that manages creation and retrieval of named metric instances, configurable with `backend` parameter (in_memory, prometheus)
- **`Counter`** -- Monotonically increasing metric with `inc()` and `get()` methods, supports labels
- **`Gauge`** -- Metric that can go up and down via `set()`, `inc()`, and `dec()` methods, supports labels
- **`Histogram`** -- Distribution metric that records observed values and computes sum, count, and average
- **`Summary`** -- Quantile-based summary metric for tracking value distributions
- **`PrometheusExporter`** -- Optional exporter that bridges metrics to Prometheus client format (requires `prometheus_client`)
- **`StatsDClient`** -- Optional exporter that sends metrics to a StatsD server (requires `statsd`)
- **`MetricAggregator`** -- Local aggregation layer that buffers counters and gauges, produces timestamped snapshots, and supports reset
- **`get_metrics()`** -- Factory function that returns a `Metrics` instance for a given backend

## Directory Contents

- `metrics.py` -- Core metric types (Counter, Gauge, Histogram, Summary) and the Metrics registry class
- `aggregator.py` -- MetricAggregator for local buffering and snapshot generation
- `prometheus_exporter.py` -- Prometheus integration exporter (optional dependency)
- `statsd_client.py` -- StatsD integration client (optional dependency)

## Navigation

- **Full Documentation**: [docs/modules/metrics/](../../../docs/modules/metrics/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
