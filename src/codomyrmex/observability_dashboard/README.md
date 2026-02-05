# observability_dashboard

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Unified monitoring dashboard system for collecting metrics, managing alerts, and composing visual panels. Provides thread-safe metric collection with configurable retention, rule-based alerting with severity levels, and dashboard composition with multiple panel types (graphs, stats, tables, heatmaps, gauges, and logs).

## Key Exports

### Enums

- **`MetricType`** -- Metric classification: COUNTER, GAUGE, HISTOGRAM, SUMMARY
- **`AlertSeverity`** -- Alert severity levels: INFO, WARNING, ERROR, CRITICAL
- **`PanelType`** -- Dashboard panel types: GRAPH, STAT, TABLE, HEATMAP, GAUGE, LOG

### Data Classes

- **`MetricValue`** -- A single metric data point with name, value, timestamp, labels, and type
- **`Alert`** -- An alert notification with severity, fire/resolve timestamps, and active status tracking
- **`Panel`** -- A dashboard panel with type, associated metrics, query, and grid position
- **`Dashboard`** -- A complete dashboard containing panels with refresh interval and tags

### Components

- **`MetricCollector`** -- Thread-safe metric recording and retrieval with configurable retention; supports time-range queries, latest-value access, and automatic cleanup of expired data
- **`AlertManager`** -- Rule-based alert management; define conditions as callables, check metrics against rules, and track active/resolved alert history
- **`DashboardManager`** -- Creates, retrieves, lists, and deletes dashboards; fetches panel-specific metric data from the underlying MetricCollector

## Directory Contents

- `__init__.py` - Module definition with all classes (MetricCollector, AlertManager, DashboardManager)
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Detailed API documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/observability_dashboard/](../../../docs/modules/observability_dashboard/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
