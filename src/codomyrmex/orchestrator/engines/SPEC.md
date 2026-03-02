# Orchestration Engines -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides workflow execution engines with dependency-ordered task scheduling, retry logic, conditional skipping, and both sequential and parallel execution strategies. Includes a factory function for engine selection.

## Architecture

Strategy pattern with an `ExecutionEngine` ABC defining synchronous `execute` and async `execute_async` contracts. Two concrete implementations: `SequentialEngine` (single-threaded, fail-fast) and `ParallelEngine` (ThreadPoolExecutor-based, level-parallel with dependency ordering via Kahn's algorithm).

## Key Classes

### `WorkflowDefinition` (dataclass)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_task` | `name, action, dependencies, **kwargs` | `str` (task ID) | Add a task with optional dependencies, timeout, retries |
| `get_task` | `task_id: str` | `TaskDefinition\|None` | Lookup by ID or name |
| `get_execution_order` | | `list[list[TaskDefinition]]` | Topological sort into parallelizable batches (Kahn's algorithm) |

### `TaskDefinition` (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | UUID | Unique task identifier |
| `name` | `str` | `""` | Human-readable name |
| `action` | `Callable\|None` | `None` | Function to execute; receives context dict |
| `dependencies` | `list[str]` | `[]` | Task IDs/names this task depends on |
| `timeout` | `float\|None` | `None` | Maximum execution time |
| `retries` | `int` | `0` | Number of retry attempts on failure |
| `retry_delay` | `float` | `1.0` | Delay between retries in seconds |
| `condition` | `Callable[[dict], bool]\|None` | `None` | Optional condition; task is SKIPPED if False |

### `ExecutionEngine` (ABC)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `workflow, initial_context` | `WorkflowResult` | Synchronous workflow execution |
| `execute_async` | `workflow, initial_context` | `WorkflowResult` | Asynchronous workflow execution |

### `SequentialEngine`

Executes tasks one at a time in dependency order. Fails fast on first task failure. Retries up to `task.retries` times with `task.retry_delay` between attempts.

### `ParallelEngine`

Executes independent tasks concurrently within each dependency level using `ThreadPoolExecutor(max_workers)`. Context updates are protected by `threading.Lock`. Cancels remaining futures on first failure.

### `create_engine` (factory)

| Parameter | Type | Description |
|-----------|------|-------------|
| `engine_type` | `str` | `"sequential"` or `"parallel"` |
| `**kwargs` | | Passed to engine constructor (e.g., `max_workers`, `max_retries`) |

## Dependencies

- **Internal**: None (self-contained)
- **External**: `asyncio`, `threading`, `concurrent.futures`, `uuid`, `time`, `datetime` (stdlib)

## Constraints

- `get_execution_order` uses Kahn's algorithm; tasks without dependencies run first; cyclic dependencies are silently dropped.
- Task actions receive the accumulated context dict as their sole argument.
- Each completed task's output is stored in context under both `task.id` and `task.name` keys.
- `ParallelEngine.execute_async` delegates to `run_in_executor` wrapping synchronous execution.
- Zero-mock: real thread pools and real task execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Task exceptions are caught and stored in `TaskResult.error`; failed tasks produce `TaskState.FAILED`.
- Workflow-level exceptions produce a `WorkflowResult` with `success=False` and the error message.
- All errors logged before propagation.
