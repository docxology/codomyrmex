# Planner — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Hierarchical goal decomposition and convergent planning-execution-feedback system. Breaks high-level goals into structured task trees, executes them with progress tracking, scores quality across four dimensions, and re-plans using memory-enriched context until convergence.

## Architecture

Three-layer design with a closed feedback loop:

1. **Planning Layer**: `PlanEngine` decomposes goals into `Plan` objects containing `PlanTask` trees with dependencies and priorities
2. **Execution Layer**: `PlanExecutor` flattens task trees and runs callable actions; `FeedbackLoop` wires to `WorkflowRunner` for richer execution
3. **Evaluation Layer**: `PlanEvaluator` produces weighted `PlanScore` composites; convergence detection stops iteration when improvement plateaus

## Key Classes

### `PlanEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `decompose` | `goal: str`, `max_depth: int = 2` | `Plan` | Keyword-based goal decomposition into phase tasks with subtask generation |

### `PlanExecutor`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `plan: Plan`, `actions: dict[str, Callable]` | `ExecutionResult` | Flatten and execute all tasks with timing and failure tracking |

### `PlanEvaluator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `evaluate` | `workflow_result`, `iteration`, `memory_hits`, `memory_queries`, `time_budget_ms` | `PlanScore` | Weighted composite from success rate, time efficiency, retry ratio, memory hits |
| `compare` | `score_a: PlanScore`, `score_b: PlanScore` | `float` | Improvement delta between two scores |
| `is_converging` | `scores: list[PlanScore]` | `bool` | True if latest improvement < convergence_threshold |

### `FeedbackLoop`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `run` | `goal: str` | `FeedbackResult` | Full cycle: decompose -> execute -> evaluate -> store -> re-plan until convergence |

### `FeedbackConfig`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `max_iterations` | `int` | 3 | Maximum re-plan cycles |
| `convergence_threshold` | `float` | 0.05 | Minimum improvement to continue |
| `quality_floor` | `float` | 0.6 | Score threshold for acceptance |
| `retry_on_partial_failure` | `bool` | True | Re-plan on partial failures |
| `memory_ttl` | `float` | 86400.0 | Feedback memory entry TTL (seconds) |
| `weight_success_rate` | `float` | 0.4 | Scoring weight |
| `weight_time_efficiency` | `float` | 0.3 | Scoring weight |
| `weight_retry_ratio` | `float` | 0.2 | Scoring weight |
| `weight_memory_hits` | `float` | 0.1 | Scoring weight |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.agents.memory.store`, `codomyrmex.orchestrator.workflows.workflow_engine`
- **External**: Standard library only (`hashlib`, `time`, `dataclasses`, `enum`)

## Constraints

- Plan scores are clamped to [0.0, 1.0].
- Goal hashes use SHA-256 truncated to 12 hex characters.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `PlanExecutor.execute()` catches task action exceptions, marks task as FAILED, logs via `logger.warning`, and continues to next task.
- `FeedbackLoop.run()` logs each iteration with goal, score, and convergence status. Does not propagate task-level exceptions.
