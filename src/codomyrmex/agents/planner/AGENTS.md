# Codomyrmex Agents — src/codomyrmex/agents/planner

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Hierarchical task planning subsystem that decomposes goals into tree-structured plans, executes them via a workflow runner, evaluates quality with multi-dimensional scoring, and iterates in a convergent feedback loop backed by memory persistence.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `plan_engine.py` | `PlanEngine` | Decomposes goal strings into hierarchical `Plan` objects using keyword-based phase detection |
| `plan_engine.py` | `Plan` | Hierarchical plan with goal, tasks list, completion tracking, and task flattening |
| `plan_engine.py` | `PlanTask` | Tree node with name, description, subtasks, dependencies, priority, and state |
| `plan_engine.py` | `TaskPriority` / `TaskState` | Enums for LOW/MEDIUM/HIGH/CRITICAL priority and PENDING/IN_PROGRESS/COMPLETED/BLOCKED/FAILED state |
| `plan_evaluator.py` | `PlanEvaluator` | Scores plan execution via weighted composite of success rate, time efficiency, retry ratio, and memory hits |
| `plan_evaluator.py` | `PlanScore` | Dataclass with overall composite, four component scores, iteration number, and details dict |
| `executor.py` | `PlanExecutor` | Flattens task tree and executes actions with progress tracking and failure counting |
| `executor.py` | `ExecutionResult` | Dataclass with success flag, completed/failed counts, replan flag, duration_ms |
| `feedback_loop.py` | `FeedbackLoop` | Full cycle: PlanEngine -> WorkflowRunner -> PlanEvaluator -> MemoryStore, iterating until convergence |
| `feedback_loop.py` | `FeedbackResult` | Dataclass capturing goal, success, final score, iteration count, convergence status |
| `feedback_config.py` | `FeedbackConfig` | Configuration for iteration limits, quality floor, convergence threshold, retry policy, scoring weights |

## Operating Contracts

- `PlanEngine.decompose()` uses keyword matching to select phase templates: build/create -> [design, implement, test, deploy]; fix/debug -> [diagnose, fix, verify]; analyze/audit -> [gather_data, analyze, report]; default -> [plan, execute, review].
- `PlanEvaluator` default weights: success_rate 0.4, time_efficiency 0.3, retry_ratio 0.2, memory_hits 0.1.
- `FeedbackLoop.run()` terminates when: (a) score >= quality_floor, (b) convergence detected (improvement < threshold), (c) max_iterations exhausted, or (d) partial failure with retry disabled.
- Memory entries are tagged with `feedback:{goal_hash}` and respect configurable TTL (default 24h).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`, `codomyrmex.agents.memory.store.MemoryStore`, `codomyrmex.orchestrator.workflows.workflow_engine`
- **Used by**: Agent orchestration pipelines, PAI PLAN phase implementations

## Navigation

- **Parent**: [agents](../README.md)
- **Root**: [Root](../../../../README.md)
