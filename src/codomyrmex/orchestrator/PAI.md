# Personal AI Infrastructure -- Orchestrator Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Orchestrator module provides DAG-based workflow construction and execution for the PAI Algorithm's PLAN phase. It defines multi-step agent workflows as directed acyclic graphs with dependency resolution, conditional branching, and parallel execution.

## PAI Capabilities

### Workflow Engine

```python
from codomyrmex.orchestrator import WorkflowEngine

engine = WorkflowEngine()

# Define DAG-based workflows
workflow = engine.create_workflow("code_review_pipeline")
workflow.add_step("scan", handler=scan_code)
workflow.add_step("review", handler=review_code, depends_on=["scan"])
workflow.add_step("fix", handler=apply_fixes, depends_on=["review"])
workflow.add_step("verify", handler=verify_fixes, depends_on=["fix"])

# Execute with dependency resolution
results = await engine.execute(workflow)
```

### Workflow Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Pipeline** | A -> B -> C | Sequential multi-step processing |
| **Fan-out** | A -> [B, C, D] | Parallel task dispatch |
| **Fan-in** | [B, C, D] -> E | Result aggregation |
| **Gate** | A -> check -> B or retry | Conditional execution |
| **TDD Loop** | A <-> B | Iterative refinement |

### Thin Orchestration API

For lightweight scripting without full DAG construction:

```python
from codomyrmex.orchestrator import run, pipe, batch, chain_scripts, step, shell

# Run a single function
result = run(my_func, arg1, arg2)

# Chain steps in a pipeline
result = pipe(step("lint", shell("ruff check src/")),
              step("test", shell("pytest")),
              step("build", shell("python -m build")))

# Run tasks in parallel
results = batch([func_a, func_b, func_c])
```

### Scheduler

```python
from codomyrmex.orchestrator.scheduler import Scheduler, every, cron

scheduler = Scheduler()
scheduler.schedule(func=cleanup, trigger=every(hours=1), name="hourly_cleanup")
scheduler.schedule(func=backup, trigger=cron("0 2 * * *"), name="nightly_backup")
scheduler.start()
```

### Resilience and Retry

```python
from codomyrmex.orchestrator import with_retry, RetryPolicy

# Decorator-based retry
@with_retry(max_attempts=3, backoff_factor=2.0)
async def flaky_operation():
    ...

# Policy-based retry within workflows
policy = RetryPolicy(max_retries=3, backoff_seconds=1.0)
task = Task(id="deploy", func=deploy, retry_policy=policy)
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Workflow` | Class | DAG workflow construction with tasks and dependencies |
| `Task` | Class | Individual unit of work within a workflow |
| `AsyncScheduler` | Class | Asynchronous job scheduling with metrics |
| `Scheduler` | Class | Thread-based task scheduler with triggers |
| `ParallelRunner` | Class | Concurrent task execution engine |
| `AgentOrchestrator` | Class | Bridge for dispatching agent tasks |
| `CICDBridge` | Class | CI/CD pipeline integration |
| `run` / `pipe` / `batch` | Functions | Thin orchestration primitives |
| `with_retry` | Decorator | Retry logic for unreliable operations |
| `chain` / `parallel` / `fan_out_fan_in` | Functions | Workflow composition helpers |

## PAI Algorithm Phase Mapping

| Phase | Orchestrator Contribution |
|-------|---------------------------|
| **OBSERVE** | `discover_scripts` scans project for available scripts and workflows; `SchedulerMetrics` reports on job completion rates |
| **THINK** | `analyze_workflow_dependencies` validates proposed DAGs for cycles; workflow patterns inform approach selection |
| **PLAN** | Construct `Workflow` DAGs from task requirements; define `Task` dependencies, `RetryPolicy`, and conditional gates |
| **BUILD** | `step` / `shell` / `python_func` primitives compose individual build actions into executable pipelines |
| **EXECUTE** | `AsyncScheduler` and `ParallelRunner` execute workflows with dependency resolution, parallelism, and retry |
| **VERIFY** | Validate workflow completion via `TaskResult` and `TaskStatus`; check all steps passed without `TaskFailedError` |
| **LEARN** | `SchedulerMetrics` captures jobs_scheduled, jobs_completed, jobs_failed, and total_execution_time for trend analysis |

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `get_scheduler_metrics` | Retrieve AsyncScheduler metrics (active jobs, completion rates, execution time) | Safe |
| `analyze_workflow_dependencies` | Validate a proposed workflow DAG for cyclic dependencies and return execution order | Safe |

## Agent Capabilities

| Agent Type | Orchestrator Role |
|------------|-------------------|
| **Engineer** | Consumes `pipe` and `step` to chain build-lint-test cycles |
| **Architect** | Uses `analyze_workflow_dependencies` to validate proposed workflow structures |
| **QATester** | Reads `SchedulerMetrics` to verify execution health; validates `TaskResult` outcomes |

## Architecture Role

**Service Layer** -- Central workflow engine consuming `events/` (triggers), `concurrency/` (parallel execution), `agents/` (task dispatch). Consumed by PAI Algorithm's PLAN phase. Depends on `logging_monitoring` (Foundation) for correlation IDs and performance logging.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Related**: [../agents/PAI.md](../agents/PAI.md) -- Agent orchestration patterns | [../concurrency/PAI.md](../concurrency/PAI.md) -- Parallel execution primitives
