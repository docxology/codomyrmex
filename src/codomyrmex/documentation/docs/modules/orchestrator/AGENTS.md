# Orchestrator Module - Agent Coordination

**Version**: v1.0.8 | **Last Updated**: March 2026

## Overview

The Orchestrator module provides agents with workflow DAG execution, parallel/async runners, retry policies, and CI/CD integration. Agents use it to define, validate, and execute multi-step workflows with dependency management.

## Key Files

| File | Class/Function | Role |
|------|---------------|------|
| `workflows/workflow.py` | `Workflow`, `Task`, `TaskStatus` | Core DAG-based workflow engine |
| `workflows/workflow.py` | `chain`, `parallel`, `fan_out_fan_in` | Workflow construction helpers |
| `execution/runner.py` | `run_script`, `run_function` | Script and function execution |
| `execution/parallel_runner.py` | `ParallelRunner`, `BatchRunner` | Concurrent execution |
| `execution/async_scheduler.py` | `AsyncScheduler`, `SchedulerMetrics` | Async job scheduling |
| `resilience/retry_policy.py` | `with_retry` | Retry decorator |
| `integration.py` | `OrchestratorBridge`, `CICDBridge`, `AgentOrchestrator` | External system bridges |
| `thin.py` | `run`, `pipe`, `batch`, `step`, `shell` | Lightweight orchestration API |
| `mcp_tools.py` | `get_scheduler_metrics`, `analyze_workflow_dependencies` | MCP tools |
| `exceptions.py` | `CycleError`, `StepError`, `OrchestratorTimeoutError` | Exception hierarchy |

## MCP Tools Available

| Tool | Category | Description |
|------|----------|-------------|
| `get_scheduler_metrics` | orchestrator | Retrieve AsyncScheduler metrics (scheduled, completed, failed, cancelled) |
| `analyze_workflow_dependencies` | orchestrator | Validate a workflow DAG for cyclic dependencies |

## Agent Instructions

1. Use `analyze_workflow_dependencies` to validate task dependency graphs before execution.
2. Use `get_scheduler_metrics` to monitor running scheduler health and job completion rates.
3. Build workflows using `Workflow`, `Task`, and `add_dependency` for complex multi-step operations.
4. Use the thin API (`run`, `pipe`, `batch`) for simple script orchestration without DAG overhead.
5. Apply `with_retry` decorator for fault-tolerant task execution with configurable retry policies.

## Operating Contracts

- `analyze_workflow_dependencies` raises `CycleError` if the DAG contains cycles; returns `{"valid_dag": True, "execution_order": [...]}` on success.
- `get_scheduler_metrics` instantiates a fresh `AsyncScheduler` and returns its metrics layout.
- `Workflow.execute()` runs tasks in topological order respecting all dependency edges.
- `ParallelRunner` uses `ThreadPoolExecutor` for concurrent execution with configurable worker counts.

## Common Patterns

```python
from codomyrmex.orchestrator import Workflow, Task, chain, with_retry

# Simple chained workflow
wf = Workflow(name="pipeline")
t1 = Task(id="step1", func=lambda: "done")
t2 = Task(id="step2", func=lambda: "done")
wf.add_task(t1)
wf.add_task(t2)
wf.add_dependency("step2", "step1")
wf.execute()

# Retry-decorated function
@with_retry(max_retries=3, delay=1.0)
def flaky_operation():
    pass
```

## PAI Agent Role Access Matrix

| Agent | Access Level | Primary Tools |
|-------|-------------|---------------|
| Engineer | Full | `Workflow`, `Task`, `run_script`, `with_retry`, all MCP tools |
| Architect | Plan | `analyze_workflow_dependencies`, `get_scheduler_metrics` |
| QATester | Execute | `run_script`, `run_function`, `get_scheduler_metrics` |

## Navigation

- [readme.md](readme.md) -- Module overview
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../orchestrator/)
