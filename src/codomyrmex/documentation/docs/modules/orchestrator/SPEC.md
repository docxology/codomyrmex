# Orchestrator Module - Technical Specification

**Version**: v1.0.8 | **Last Updated**: March 2026

## Overview

The Orchestrator module provides script discovery, DAG-based workflow execution, parallel/async runners, retry policies, and CI/CD integration. It supports both lightweight orchestration (thin API) and full workflow management with dependency resolution and cycle detection.

## Design Principles

- **Zero-Mock Policy**: Tests use real function execution and actual script discovery.
- **Explicit Failure**: `CycleError`, `StepError`, `OrchestratorTimeoutError` for all failure modes.
- **DAG-First Execution**: Workflows validate dependency graphs before execution via topological sort.

## Architecture

```
orchestrator/
  __init__.py              # 60+ exports
  core.py                  # Entry point, argument parsing
  config.py                # Configuration loading
  discovery.py             # Script discovery
  exceptions.py            # Exception hierarchy
  thin.py                  # Lightweight API (run, pipe, batch, step)
  integration.py           # External system bridges
  mcp_tools.py             # 2 MCP tools
  execution/
    runner.py              # run_script, run_function
    parallel_runner.py     # ParallelRunner, BatchRunner
    async_runner.py        # AsyncParallelRunner
    async_scheduler.py     # AsyncScheduler, SchedulerMetrics
  resilience/
    retry_policy.py        # with_retry decorator
  workflows/
    workflow.py            # Workflow, Task, chain, parallel, fan_out_fan_in
  observability/
    reporting.py           # Report generation
  engines/                 # Engine implementations
  monitors/                # Execution monitors
  pipelines/               # Pipeline definitions
  scheduler/               # Scheduler implementations
  state/                   # State management
  templates/               # Workflow templates
  triggers/                # Event triggers
```

## Functional Requirements

1. Discover Python scripts in configurable directory trees.
2. Execute scripts with configurable timeouts and progress reporting.
3. Build and execute DAG-based workflows with topological ordering.
4. Detect cyclic dependencies and raise `CycleError`.
5. Run tasks in parallel via `ParallelRunner` or `BatchRunner` with worker pools.
6. Schedule async jobs with `AsyncScheduler` and track metrics.
7. Apply retry policies with configurable max retries, delay, and backoff.
8. Integrate with CI/CD systems via `CICDBridge` and `create_pipeline_workflow`.
9. Provide lightweight orchestration via thin API (run, pipe, batch).
10. Expose scheduler metrics and DAG validation as MCP tools.

## Interface Contracts

```python
class Workflow:
    def __init__(self, name: str): ...
    def add_task(self, task: Task) -> None: ...
    def add_dependency(self, task_id: str, depends_on: str) -> None: ...
    def execute(self) -> dict[str, TaskResult]: ...

class Task:
    id: str
    func: Callable
    retry_policy: RetryPolicy | None
    timeout: float | None

class AsyncScheduler:
    metrics: SchedulerMetrics
    async def schedule(self, job: AsyncJob) -> str: ...

class ParallelRunner:
    def __init__(self, max_workers: int = 4): ...
    def run(self, targets: list) -> list[ExecutionResult]: ...

def with_retry(max_retries: int = 3, delay: float = 1.0) -> Callable: ...
```

## Dependencies

**Internal**: `codomyrmex.logging_monitoring`, `codomyrmex.utils.cli_helpers`, `codomyrmex.model_context_protocol.decorators`, `codomyrmex.validation.schemas` (optional)

**External**: `concurrent.futures` (stdlib), `asyncio` (stdlib), `argparse` (stdlib)

## Constraints

- Workflow execution is single-process by default; `ParallelRunner` uses threads.
- `AsyncScheduler` requires an event loop; metrics are per-instance.
- Script discovery filters by `.py` extension and excludes `__pycache__`.

## Navigation

- [readme.md](readme.md) -- Module overview
- [AGENTS.md](AGENTS.md) -- Agent coordination
- [Source Module](../../../../orchestrator/)
