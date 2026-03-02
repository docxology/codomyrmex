# Codomyrmex Agents — src/codomyrmex/orchestrator/workflows

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides DAG-based workflow orchestration with two complementary engines: a rich async `Workflow` class with retry policies, conditional execution, result passing, and progress callbacks; and a synchronous `WorkflowRunner` with Kahn's-algorithm topological sorting. Includes workflow journaling for audit trails, analytics for failure hotspot detection, and reusable workflow templates.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `workflow.py` | `Workflow` | Async DAG executor with retry, conditions, timeouts, fail-fast, EventBus integration |
| `workflow.py` | `Task` / `TaskStatus` / `TaskResult` / `RetryPolicy` | Task model with dependencies, conditional execution, and retry config |
| `workflow.py` | `chain`, `parallel`, `fan_out_fan_in` | Convenience factory functions for common workflow patterns |
| `workflow.py` | `WorkflowError` / `CycleError` / `TaskFailedError` | Exception hierarchy for workflow failures |
| `workflow_engine.py` | `WorkflowRunner` | Synchronous DAG runner using Kahn's topological sort |
| `workflow_engine.py` | `WorkflowStep` / `StepStatus` / `WorkflowResult` | Step model with status, timing, and aggregated result |
| `workflow_journal.py` | `WorkflowJournal` | Records workflow start/step/complete events as `JournalEntry` objects |
| `workflow_journal.py` | `JournalEntry` | Structured event record with workflow_id, event_type, status, duration |
| `workflow_analytics.py` | `WorkflowAnalytics` | Analyzes journal entries for failure hotspots, duration trends, and per-step success rates |
| `workflow_analytics.py` | `WorkflowInsight` | Summary dataclass with aggregated metrics |
| `workflow_templates.py` | `WorkflowTemplate` | Reusable template that instantiates `WorkflowRunner` with overrideable step actions |
| `workflow_templates.py` | `ci_cd_template`, `code_review_template`, `data_pipeline_template` | Pre-built pipeline templates |

## Operating Contracts

- `Workflow.run()` validates the DAG for cycles before execution (raises `CycleError`).
- Tasks with unsatisfied dependencies are skipped; fail-fast mode cancels remaining tasks.
- `Workflow` injects `_task_results` into async task kwargs for inter-task result passing.
- `WorkflowRunner` uses Kahn's algorithm; raises `ValueError` on cycle detection.
- `WorkflowJournal` optionally persists entries to `MemoryStore` for cross-session storage.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `codomyrmex.logging_monitoring`, `codomyrmex.agents.memory.store.MemoryStore` (optional persistence), `orchestrator.workflows.observability` (optional EventBus events)
- **Used by**: `orchestrator` top-level, CI/CD pipelines, agent task execution

## Navigation

- **Parent**: [orchestrator](../README.md)
- **Root**: [Root](../../../../README.md)
