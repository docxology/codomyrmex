# Performance Monitoring - Agentic Context

**Module**: `codomyrmex.performance.monitoring`
**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Key Components

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `PerformanceMonitor` | Record timing metrics per-function with stats aggregation | `record_metrics()`, `get_stats()`, `export_metrics()`, `clear_metrics()` |
| `SystemMonitor` | Background thread polling CPU/memory via `psutil` | `start()`, `stop()`, `get_latest_metrics()` |
| `ResourceTracker` | Detailed psutil-based resource snapshots during an operation | `start_tracking()`, `stop_tracking()` returning `ResourceTrackingResult` |
| `ResourceSnapshot` | Point-in-time capture of RSS, VMS, CPU times, threads, FDs | Dataclass with `to_dict()` |
| `monitor_performance` | Decorator that wraps a function with timing and metrics | Returns decorated function |
| `track_resource_usage` | Context manager for resource sampling during a block | Yields `ResourceTracker` |

## Operating Contracts

- `ResourceTracker` requires `psutil`; when absent it logs a warning and returns empty results instead of raising.
- `SystemMonitor` uses a daemon thread for background polling; call `stop()` before process exit.
- Snapshot retention is bounded by `max_snapshots` (default 1000); when exceeded, oldest non-boundary snapshots are dropped.
- `PerformanceMonitor` is available as a global singleton via `_performance_monitor`.

## Integration Points

- **psutil**: Optional dependency for CPU/memory/thread/FD metrics; gracefully degrades when missing.
- **logging_monitoring**: Uses `get_logger` for structured log output.
- **performance/profiling**: Complements `AsyncProfiler` with system-level resource tracking vs. per-function timing.

## Constraints

- `start_tracking()` is not re-entrant; calling while already tracking logs a warning and returns immediately.
- CPU percent values from `psutil.Process.cpu_percent(interval=None)` require two successive calls for accuracy.
