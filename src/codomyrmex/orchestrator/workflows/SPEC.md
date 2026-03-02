# Workflows — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

DAG-based workflow orchestration with two execution engines, execution journaling, analytics, and reusable templates.

## Architecture

Dual-engine design:

1. **Async Engine** (`workflow.py`) -- `Workflow` class runs tasks as `asyncio.gather` batches in topological order with retry, conditional execution, timeouts, and EventBus events.
2. **Sync Engine** (`workflow_engine.py`) -- `WorkflowRunner` executes steps sequentially in Kahn's-algorithm topological order with shared context passing.
3. **Journaling** (`workflow_journal.py`) -- `WorkflowJournal` observes execution lifecycle and records structured `JournalEntry` events, optionally persisting to `MemoryStore`.
4. **Analytics** (`workflow_analytics.py`) -- `WorkflowAnalytics` aggregates journal data into `WorkflowInsight` summaries.
5. **Templates** (`workflow_templates.py`) -- `WorkflowTemplate` instantiates `WorkflowRunner` with predefined step DAGs.

## Key Classes

### `Workflow` (async)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_task` | `name, action, dependencies, args, kwargs, timeout, retry_policy, condition, transform_result, tags, metadata` | `Workflow` | Add a task (chainable) |
| `run` | none | `dict[str, Any]` | Execute all tasks in topological batches via `asyncio.gather` |
| `validate` | none | `None` | Check for missing deps and cycles |
| `cancel` | none | `None` | Request workflow cancellation |
| `get_summary` | none | `dict` | Execution summary with counts and timings |

### `WorkflowRunner` (sync)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_step` | `step: WorkflowStep` | `None` | Add a step to the DAG |
| `run` | `context: dict \| None` | `WorkflowResult` | Execute in topological order |
| `step_count` | property | `int` | Number of registered steps |
| `step_names` | none | `list[str]` | Ordered step name list |

### `WorkflowJournal`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `on_workflow_start` | `runner: WorkflowRunner, workflow_id: str` | `None` | Record start event |
| `on_step_complete` | `workflow_id: str, step: WorkflowStep` | `None` | Record step event |
| `on_workflow_complete` | `result: WorkflowResult` | `None` | Record completion event |
| `record_full_workflow` | `runner, result` | `None` | Record all events in one call |
| `by_workflow_id` | `workflow_id: str` | `list[JournalEntry]` | Filter by workflow |
| `by_event_type` | `event_type: str` | `list[JournalEntry]` | Filter by event type |

### `WorkflowAnalytics`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `failure_hotspots` | `n: int = 5` | `list[tuple[str, int]]` | Top-N steps by failure count |
| `duration_trend` | `window: int = 10` | `list[float]` | Moving average of workflow durations |
| `success_rate` | `step_name: str` | `float` | Per-step success rate |
| `generate_insight` | none | `WorkflowInsight` | Full summary with all metrics |

### `WorkflowTemplate`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `instantiate` | `overrides: dict[str, Callable] \| None` | `WorkflowRunner` | Create runner from template with optional action overrides |

Built-in templates: `ci_cd_template` (lint-build-test-deploy), `code_review_template` (generate-test-review-merge), `data_pipeline_template` (ingest-validate-transform-export).

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.agents.memory.store.MemoryStore` (optional)
- **External**: Standard library (`asyncio`, `collections`, `time`, `uuid`)

## Constraints

- `Workflow.run()` validates DAG before execution; raises `CycleError` on cycles and `WorkflowError` on deadlock.
- Sync functions in `Workflow` are offloaded to `loop.run_in_executor` to avoid blocking the event loop.
- `WorkflowRunner._topological_sort` uses Kahn's algorithm; raises `ValueError` on cycle detection.
- `WorkflowTemplate.instantiate` produces steps with `None` action if no override is provided for a step.
- Zero-mock: real execution only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `CycleError` raised during `Workflow.validate()` or `WorkflowRunner._topological_sort()`.
- `WorkflowError` raised on workflow timeout or deadlock.
- `asyncio.TimeoutError` raised per-task when task-level timeout is exceeded.
- `WorkflowJournal._persist` silently drops persistence if no `MemoryStore` is configured.
- All errors logged before propagation.
