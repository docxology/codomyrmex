# Performance Monitoring - Technical Specification

**Module**: `codomyrmex.performance.monitoring`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Architecture

Two complementary monitors: `PerformanceMonitor` for function-level timing metrics and `ResourceTracker` for system-level resource snapshots during operations.

## Key Classes

### PerformanceMonitor

| Method | Signature | Description |
|--------|-----------|-------------|
| `record_metrics` | `(name: str, duration: float, **tags)` | Record a timing measurement |
| `get_stats` | `(name: str) -> dict` | Aggregate stats: count, min, max, avg, p95 |
| `export_metrics` | `() -> dict` | Full export of all recorded metrics |
| `clear_metrics` | `()` | Reset all stored data |

### ResourceTracker

| Method | Signature | Description |
|--------|-----------|-------------|
| `start_tracking` | `(operation: str, context: dict \| None)` | Begin resource sampling for named operation |
| `stop_tracking` | `(operation: str) -> ResourceTrackingResult` | End tracking and compute aggregates |
| `get_current_snapshot` | `() -> ResourceSnapshot \| None` | Most recent snapshot |
| `is_tracking` | `() -> bool` | Whether tracking is active |

### ResourceSnapshot (dataclass)

Fields: `timestamp`, `memory_rss_mb`, `memory_vms_mb`, `cpu_percent`, `cpu_times_user`, `cpu_times_system`, `num_threads`, `num_fds`, `context`.

### ResourceTrackingResult (dataclass)

Fields: `operation`, `start_time`, `end_time`, `duration`, `snapshots`, `peak_memory_rss_mb`, `peak_memory_vms_mb`, `average_cpu_percent`, `total_cpu_time`, `memory_delta_mb`, `summary`.

## Dependencies

- `psutil` (optional): CPU, memory, thread, and file descriptor metrics. Graceful degradation when absent.
- `threading`: Lock for snapshot list access, daemon threads for `SystemMonitor`.
- `logging_monitoring.core.logger_config`: Structured logging.

## Constraints

- `ResourceTracker` is not re-entrant; concurrent `start_tracking()` calls are rejected with a warning.
- Snapshot retention bounded by `max_snapshots` (default 1000); overflow drops second-oldest, preserving first and last.
- `benchmark_resource_usage()` runs a function N iterations with 0.05s sample interval and returns a `create_resource_report()` aggregate.

## Error Handling

- `psutil.AccessDenied` during FD counting: caught, `num_fds` set to 0.
- Snapshot failures: caught, logged at ERROR, tracking continues.
