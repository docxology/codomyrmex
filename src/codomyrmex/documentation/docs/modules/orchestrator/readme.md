# Orchestrator Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

Script orchestration engine for discovering, configuring, and running Python scripts within the Codomyrmex project. Provides workflow DAG execution with dependency resolution, parallel execution with resource management, retry logic with exponential backoff, conditional step execution, and CI/CD pipeline integration. Includes both a full-featured workflow system and a thin convenience API for common patterns.

## PAI Integration

The orchestrator module is central to PAI's **PLAN phase**. The `Architect` subagent uses `analyze_workflow_dependencies` to validate DAG structure and detect cycles before BUILD begins. The `QATester` subagent reads `get_scheduler_metrics` during VERIFY to confirm workflow execution completed without deadlocks or timeouts. See [AGENTS.md](AGENTS.md) for the full agent role access matrix.

| Algorithm Phase | Orchestrator Role |
|----------------|------------------|
| PLAN | `Architect` → `analyze_workflow_dependencies` to validate DAG |
| EXECUTE | `Engineer` → `Workflow` / `ParallelRunner` for parallel task execution |
| VERIFY | `QATester` → `get_scheduler_metrics` to confirm execution health |

## Key Exports

### Core Orchestration

- **`run_orchestrator`** -- Main entry point from `core.py` for running the orchestrator
- **`load_config()`** -- Load orchestrator configuration from file
- **`get_script_config()`** -- Get configuration for a specific script
- **`discover_scripts()`** -- Discover runnable scripts in the project

### Workflow DAG

- **`Workflow`** -- DAG-based workflow with task dependencies, parallel execution, and cycle detection
- **`Task`** -- A single unit of work within a workflow with status tracking
- **`TaskStatus`** -- Task lifecycle states (pending, running, completed, failed)
- **`TaskResult`** -- Result of task execution with output and error info
- **`RetryPolicy`** -- Configurable retry strategy with backoff parameters
- **`chain()`** -- Helper to create a linear chain of dependent tasks
- **`parallel()`** -- Helper to create tasks that run in parallel
- **`fan_out_fan_in()`** -- Pattern for distributing work and collecting results

### Exceptions

- **`WorkflowError`** -- Base workflow exception
- **`CycleError`** -- Raised when a dependency cycle is detected in the workflow DAG
- **`TaskFailedError`** -- Raised when a task fails execution
- **`StepError`** -- Error in a specific orchestration step
- **`OrchestratorTimeoutError`** -- Raised when execution exceeds timeout
- **`StateError`** -- Invalid orchestrator state transition
- **`DependencyResolutionError`** -- Cannot resolve task dependencies
- **`ConcurrencyError`** -- Error in parallel execution

### Runners

- **`run_script()`** -- Execute a script by path
- **`run_function()`** -- Execute a Python callable as a task
- **`ParallelRunner`** -- Manages concurrent execution of multiple tasks with thread/process pools
- **`BatchRunner`** -- Runs tasks in configurable batch sizes
- **`ExecutionResult`** -- Result container for parallel execution
- **`run_parallel()`** -- Synchronous parallel execution helper
- **`run_parallel_async()`** -- Async parallel execution helper

### Thin API

- **`run()`** -- Simple synchronous script runner
- **`run_async()`** -- Simple async script runner
- **`pipe()`** -- Pipe output of one step into the next
- **`batch()`** -- Run items in batches
- **`chain_scripts()`** -- Chain scripts sequentially
- **`workflow()`** -- Define a workflow from step functions
- **`step()`** -- Define a single step
- **`Steps`** -- Collection of step definitions
- **`StepResult`** -- Result of a thin-API step
- **`shell()`** -- Run a shell command as a step
- **`python_func()`** -- Run a Python function as a step
- **`retry()`** -- Retry decorator for steps
- **`timeout()`** -- Timeout decorator for steps
- **`condition()`** -- Conditional execution wrapper

### Integration Bridges

- **`OrchestratorBridge`** -- Bridge between orchestrator and external systems
- **`CICDBridge`** -- Integration with CI/CD pipelines
- **`AgentOrchestrator`** -- Orchestrate AI agent task execution
- **`StageConfig`** -- Configuration for a CI/CD pipeline stage
- **`PipelineConfig`** -- Full pipeline configuration
- **`create_pipeline_workflow()`** -- Convert pipeline config into a workflow
- **`run_ci_stage()`** -- Execute a single CI/CD stage
- **`run_agent_task()`** -- Execute an agent-orchestrated task

### Submodules

- **`engines`** -- Execution engine implementations
- **`schedulers`** -- Task scheduling strategies
- **`workflows`** -- Pre-built workflow templates
- **`monitors`** -- Execution monitoring and observability
- **`pipelines`** -- Pipeline definition and management
- **`triggers`** -- Event-based workflow triggers
- **`state`** -- Workflow state persistence
- **`templates`** -- Reusable workflow templates

## Directory Contents

- `__init__.py` - Module exports and submodule registration
- `core.py` - Main orchestrator entry point
- `config.py` - Configuration loading and script config access
- `discovery.py` - Script discovery across the project
- `workflow.py` - Workflow DAG, Task, RetryPolicy, and topology helpers
- `exceptions.py` - Orchestrator-specific exception hierarchy
- `runner.py` - Single-script and function execution
- `parallel_runner.py` - ParallelRunner, BatchRunner, and parallel execution helpers
- `thin.py` - Thin convenience API (run, pipe, batch, shell, etc.)
- `integration.py` - CI/CD and agent integration bridges
- `reporting.py` - Execution reporting utilities
- `engines/` - Execution engine implementations
- `schedulers/` - Task scheduling strategies
- `workflows/` - Pre-built workflow definitions
- `monitors/` - Execution monitoring
- `pipelines/` - Pipeline management
- `triggers/` - Event-based triggers
- `state/` - State persistence
- `templates/` - Reusable templates

## Quick Start

```python
import asyncio
from codomyrmex.orchestrator import Workflow, RetryPolicy

def fetch_data():
    return {"users": 150}

def transform(data):
    return {k: v * 2 for k, v in data.items()}

def report(result):
    print(f"Report: {result}")

wf = Workflow(name="etl-pipeline", fail_fast=True)
wf.add_task("fetch", action=fetch_data)
wf.add_task("transform", action=transform, dependencies=["fetch"],
            retry_policy=RetryPolicy(max_attempts=3))
wf.add_task("report", action=report, dependencies=["transform"])

results = asyncio.run(wf.run())
print(wf.get_summary())
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k orchestrator -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`scheduler/`** | Cron-like scheduling, one-off timers, recurring tasks |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/orchestrator/](../../../docs/modules/orchestrator/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
