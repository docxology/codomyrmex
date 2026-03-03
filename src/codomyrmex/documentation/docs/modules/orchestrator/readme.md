# Orchestrator Module

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Orchestrator module provides script discovery, workflow DAG execution, parallel and async runners, retry policies, and CI/CD integration bridges. It enables both simple script execution and complex multi-step workflow orchestration with dependency resolution, progress streaming, and resource management.

## PAI Integration

| Algorithm Phase | Orchestrator Role |
|----------------|-------------------|
| PLAN | Workflow DAG construction and dependency analysis |
| EXECUTE | Script/function execution, parallel runners, async schedulers |
| VERIFY | Workflow validation (cycle detection), scheduler metrics |
| OBSERVE | Execution result reporting, progress streaming |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `Workflow` | class | DAG-based workflow with tasks and dependencies |
| `Task` | class | Individual workflow task with function, retry, and timeout |
| `TaskStatus` | enum | Task states (PENDING, RUNNING, COMPLETED, FAILED, etc.) |
| `ParallelRunner` | class | Concurrent execution of multiple targets |
| `BatchRunner` | class | Batch processing with worker pools |
| `AsyncScheduler` | class | Async job scheduling with metrics tracking |
| `AsyncParallelRunner` | class | Async parallel execution |
| `with_retry` | decorator | Retry decorator with configurable policy |
| `run_script` | function | Execute a Python script with timeout |
| `run_function` | function | Execute a Python function with tracing |
| `discover_scripts` | function | Discover scripts in a directory tree |
| `chain` | function | Chain tasks sequentially in a workflow |
| `parallel` | function | Run tasks in parallel in a workflow |
| `fan_out_fan_in` | function | Fan-out/fan-in workflow pattern |
| `OrchestratorBridge` | class | Bridge to external orchestration systems |
| `CICDBridge` | class | CI/CD pipeline integration |
| `AgentOrchestrator` | class | Agent task orchestration |

## Quick Start

```python
from codomyrmex.orchestrator import Workflow, Task, chain, parallel

# Build a workflow
wf = Workflow(name="my_pipeline")
t1 = Task(id="lint", func=lambda: print("Linting..."))
t2 = Task(id="test", func=lambda: print("Testing..."))
t3 = Task(id="build", func=lambda: print("Building..."))

wf.add_task(t1)
wf.add_task(t2)
wf.add_task(t3)
wf.add_dependency("test", "lint")  # test depends on lint
wf.add_dependency("build", "test") # build depends on test

wf.execute()
```

## Architecture

```
orchestrator/
  __init__.py              # Public API (60+ exports)
  core.py                  # Main entry point, argument parsing, script runner
  config.py                # load_config, get_script_config
  discovery.py             # discover_scripts
  exceptions.py            # StepError, OrchestratorTimeoutError, StateError, etc.
  thin.py                  # Lightweight orchestration: run, pipe, batch, step, shell
  integration.py           # OrchestratorBridge, CICDBridge, AgentOrchestrator
  mcp_tools.py             # MCP tools: get_scheduler_metrics, analyze_workflow_dependencies
  agent_supervisor.py      # Agent supervision
  heartbeat.py             # Heartbeat monitoring
  module_connector.py      # Module connection
  process_orchestrator.py  # Process-level orchestration
  triage_engine.py         # Triage and routing
  engines/                 # Execution engine implementations
  execution/
    runner.py              # run_script, run_function
    parallel_runner.py     # ParallelRunner, BatchRunner, run_parallel
    async_runner.py        # AsyncParallelRunner, AsyncTaskResult
    async_scheduler.py     # AsyncScheduler, AsyncJob, SchedulerMetrics
  monitors/                # Execution monitoring
  observability/
    reporting.py           # generate_report, save_log
  pipelines/               # Pipeline definitions
  resilience/
    retry_policy.py        # with_retry decorator
  scheduler/               # Scheduler implementations
  state/                   # State management
  templates/               # Workflow templates
  triggers/                # Event triggers
  workflows/
    workflow.py            # Workflow, Task, TaskResult, TaskStatus, chain, parallel, fan_out_fan_in
```

## MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `get_scheduler_metrics` | Retrieve AsyncScheduler metrics (jobs scheduled, completed, failed) | None |
| `analyze_workflow_dependencies` | Analyze a proposed workflow DAG for cyclic dependencies | `tasks` (list of dicts with `id` and `dependencies`) |

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/orchestrator/ -v
```

## Navigation

- [AGENTS.md](AGENTS.md) -- Agent coordination documentation
- [SPEC.md](SPEC.md) -- Technical specification
- [Source Module](../../../../orchestrator/)
