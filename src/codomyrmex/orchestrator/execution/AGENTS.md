# Codomyrmex Agents — src/codomyrmex/orchestrator/execution

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides synchronous and asynchronous execution primitives for running Python scripts and coroutines in parallel. Includes process-based script execution with resource limits, thread-pool-based parallel runners, native asyncio runners with structured concurrency (TaskGroup), and an async-first job scheduler with priority queuing and EventBus integration.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `runner.py` | `run_script` | Execute a Python script via `subprocess.run` with timeout, memory limits, and environment setup |
| `runner.py` | `run_function` | Run a callable in a separate `multiprocessing.Process` with timeout and memory limits |
| `parallel_runner.py` | `ParallelRunner` | Concurrent script execution via `ProcessPoolExecutor` with progress callbacks and fail-fast |
| `parallel_runner.py` | `BatchRunner` | Sequential batch execution of script groups using `ParallelRunner` internally |
| `parallel_runner.py` | `ExecutionResult` | Aggregated outcome dataclass (total, passed, failed, timeout, skipped) |
| `async_runner.py` | `AsyncParallelRunner` | Native asyncio concurrency with `Semaphore` bounds and optional `TaskGroup` fail-fast |
| `async_runner.py` | `AsyncTaskResult` / `AsyncExecutionResult` | Per-task and batch-level result containers for async execution |
| `async_scheduler.py` | `AsyncScheduler` | Priority-based async job scheduler with `EventBus` lifecycle event emission |
| `async_scheduler.py` | `AsyncJob` / `AsyncJobStatus` / `SchedulerMetrics` | Job model, status enum, and runtime metrics dataclass |

## Operating Contracts

- Script execution uses `subprocess.run` with `stdin=DEVNULL`; never connects interactive stdin.
- Memory limits (via `resource.setrlimit`) apply only on Unix; silently skipped on other platforms.
- `AsyncParallelRunner` requires Python 3.11+ for `asyncio.TaskGroup` structured concurrency.
- `AsyncScheduler` emits optional EventBus events; missing EventBus is tolerated silently.
- All execution errors are logged via `logging_monitoring.get_logger` before propagation.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring` (structured logging), `codomyrmex.events.core.event_schema` (optional EventBus events)
- **Used by**: `orchestrator.scheduler`, `orchestrator.workflows`, top-level `orchestrator.process_orchestrator`

## Navigation

- **Parent**: [orchestrator](../README.md)
- **Root**: [Root](../../../../README.md)
