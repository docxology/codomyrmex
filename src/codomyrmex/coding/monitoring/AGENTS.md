# Codomyrmex Agents — src/codomyrmex/coding/monitoring

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides execution monitoring, resource tracking, and metrics collection for code execution operations. This module tracks execution status, monitors CPU and memory usage, and aggregates execution metrics for analysis and reporting.

## Active Components

- `execution_monitor.py` - Execution status tracking with `ExecutionMonitor`
- `resource_tracker.py` - CPU and memory monitoring with `ResourceMonitor`
- `metrics_collector.py` - Metrics aggregation with `MetricsCollector`
- `__init__.py` - Module exports

## Key Classes and Functions

### execution_monitor.py
- **`ExecutionMonitor`** - Tracks execution status and metrics:
  - `start_execution(execution_id, language, code_length)` - Begin tracking an execution with metadata.
  - `end_execution(execution_id, status, result)` - Complete tracking with final status and results.
  - `get_execution_stats()` - Get aggregated statistics for all tracked executions.
  - Returns: total_executions, completed_executions, average_execution_time, success_count, error_count.

### resource_tracker.py
- **`ResourceMonitor`** - Monitors resource usage during execution:
  - `start_monitoring()` - Initialize monitoring, capture starting memory usage.
  - `update_monitoring()` - Sample current CPU and memory usage (call periodically).
  - `get_resource_usage()` - Get resource usage statistics:
    - `execution_time_seconds` - Total execution time.
    - `memory_start_mb` - Initial memory usage in MB.
    - `memory_peak_mb` - Peak memory usage during execution.
    - `cpu_samples` - Number of CPU usage samples collected.
    - `cpu_average_percent` - Average CPU usage percentage.
    - `cpu_peak_percent` - Peak CPU usage percentage.
- **Note**: Requires `psutil` package for full functionality. Gracefully degrades if unavailable.

### metrics_collector.py
- **`MetricsCollector`** - Collects and aggregates execution metrics:
  - `record_execution(execution_result)` - Record an execution result for metrics collection.
  - `get_language_stats()` - Get statistics grouped by programming language:
    - Per-language: count, success_count, error_count, total_execution_time, average_execution_time.
  - `get_summary()` - Get overall summary statistics:
    - total_executions, success_count, error_count, success_rate, average_execution_time, total_execution_time.
  - `clear()` - Clear all collected metrics.

## Operating Contracts

- Resource monitoring is non-blocking and runs in background threads.
- CPU sampling occurs at 100ms intervals during execution.
- Memory usage is tracked from process start to peak.
- Metrics are stored in memory and can be cleared as needed.
- All monitoring is optional and gracefully degrades without psutil.
- Execution tracking includes language, code length, and timing metadata.

## Signposting

- **Dependencies**: Optional `psutil` package for CPU/memory monitoring.
- **Parent Directory**: [coding](../README.md) - Parent module documentation.
- **Related Modules**:
  - `execution/` - Generates execution events to monitor.
  - `sandbox/isolation.py` - Uses ResourceMonitor for execution monitoring.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
