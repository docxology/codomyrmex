# Codomyrmex Agents — src/codomyrmex/coding/monitoring

## Signposting
- **Parent**: [coding](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Code execution monitoring including execution monitoring, metrics collection, and resource tracking. Provides comprehensive monitoring capabilities for code execution in sandboxed environments.

## Active Components
- `README.md` – Project file
- `__init__.py` – Module exports and public API
- `execution_monitor.py` – Execution monitoring
- `metrics_collector.py` – Metrics collection
- `resource_tracker.py` – Resource tracking

## Key Classes and Functions

### ExecutionMonitor (`execution_monitor.py`)
- `ExecutionMonitor()` – Monitor code execution
- `monitor_execution(execution_id: str) -> ExecutionMetrics` – Monitor execution
- `get_execution_status(execution_id: str) -> ExecutionStatus` – Get execution status

### MetricsCollector (`metrics_collector.py`)
- `MetricsCollector()` – Collect execution metrics
- `collect_metrics(execution_id: str) -> Metrics` – Collect metrics
- `get_metrics_summary() -> MetricsSummary` – Get metrics summary

### ResourceMonitor (`resource_tracker.py`)
- `ResourceMonitor()` – Monitor resource usage
- `track_resources(execution_id: str) -> ResourceUsage` – Track resource usage
- `get_resource_stats() -> ResourceStats` – Get resource statistics

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation