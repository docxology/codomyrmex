# Execution — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The execution submodule provides four execution strategies: synchronous subprocess-based script running, process-pool parallel execution, native asyncio parallel execution, and async job scheduling with priority ordering.

## Architecture

Two parallel stacks coexist:

1. **Process-based** (`runner.py`, `parallel_runner.py`) -- uses `subprocess.run` and `ProcessPoolExecutor` for script-level isolation.
2. **Asyncio-based** (`async_runner.py`, `async_scheduler.py`) -- uses `asyncio.TaskGroup`, `Semaphore`, and priority heaps for coroutine-level concurrency.

## Key Classes

### `run_script`

| Parameter | Type | Description |
|-----------|------|-------------|
| `script_path` | `Path` | Path to the Python script |
| `timeout` | `int` | Execution timeout in seconds (default 60) |
| `env` | `dict[str, str] \| None` | Additional environment variables |
| `cwd` | `Path \| None` | Working directory |
| `memory_limit_mb` | `int \| None` | Unix-only memory limit via `resource.setrlimit` |

Returns a dict with keys: `script`, `name`, `status`, `exit_code`, `stdout`, `stderr`, `execution_time`, `error`.

### `ParallelRunner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run_scripts` | `scripts: list[Path], timeout, cwd, env, configs` | `ExecutionResult` | Run scripts via `ProcessPoolExecutor` |
| `run_scripts_async` | same as above | `ExecutionResult` | Async wrapper around `run_scripts` |
| `cancel` | none | `None` | Cancel running execution |

### `AsyncParallelRunner`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `tasks: list[tuple[str, Callable, tuple]]` | `AsyncExecutionResult` | Execute coroutines concurrently with optional semaphore bounds |

### `AsyncScheduler`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `schedule` | `func, name, args, kwargs, priority, max_runs` | `str` (job ID) | Queue an async job with priority ordering |
| `run_all` | none | `dict[str, AsyncJob]` | Execute all pending jobs respecting priority via `TaskGroup` |
| `cancel` | `job_id: str` | `bool` | Cancel a pending job |
| `list_jobs` | `status: AsyncJobStatus \| None` | `list[AsyncJob]` | List jobs optionally filtered by status |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.events.core.event_schema` (optional)
- **External**: Standard library (`asyncio`, `subprocess`, `concurrent.futures`, `multiprocessing`, `resource`)

## Constraints

- `AsyncParallelRunner.run` and `AsyncScheduler.run_all` require Python 3.11+ (`asyncio.TaskGroup`).
- `run_script` sets `PYTHONPATH` by searching up to 5 parent directories for a `src/` folder.
- `ParallelRunner.max_workers` defaults to `min(cpu_count, 8)`.
- Zero-mock: real subprocess execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `subprocess.TimeoutExpired` caught and recorded as `status: "timeout"` in the result dict.
- `AsyncParallelRunner` catches `CancelledError` separately and records as `cancelled` count.
- `AsyncScheduler` logs job failures and records error string on `AsyncJob.error`.
- All errors logged before propagation via `logging_monitoring`.
