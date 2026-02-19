# Engines

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Workflow engine implementations for the orchestrator. Provides sequential and parallel execution engines that process workflow DAGs with dependency resolution, retry logic, conditional execution, and timeout support.

## Key Exports

### Enums

- **`TaskState`** -- Task lifecycle states: PENDING, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED, SKIPPED

### Workflow Data Structures

- **`TaskDefinition`** -- Defines a task with action callable, dependency list, timeout, retry count, retry delay, and conditional execution gate
- **`TaskResult`** -- Result of task execution with state, output, error, timing, and attempt count
- **`WorkflowDefinition`** -- Complete workflow with task list, dependency graph, and topological execution ordering via Kahn's algorithm
- **`WorkflowResult`** -- Aggregate workflow result with per-task results, success flag, timing, and error reporting

### Execution Engines

- **`ExecutionEngine`** -- Abstract base class defining synchronous `execute()` and async `execute_async()` interfaces
- **`SequentialEngine`** -- Executes tasks one at a time in dependency order with retry support; fails fast on first task failure
- **`ParallelEngine`** -- Executes independent tasks concurrently using ThreadPoolExecutor with configurable worker count; thread-safe context sharing

### Factory

- **`create_engine()`** -- Factory function to create engines by type string ("sequential", "parallel") with keyword arguments

## Directory Contents

- `__init__.py` - All engine classes, data structures, and factory (451 lines)
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.orchestrator.engines import WorkflowDefinition, ParallelEngine

workflow = WorkflowDefinition(name="build_pipeline")
t1 = workflow.add_task("lint", action=lambda ctx: "ok")
t2 = workflow.add_task("test", action=lambda ctx: "ok")
t3 = workflow.add_task("deploy", action=lambda ctx: "deployed", dependencies=[t1, t2])

engine = ParallelEngine(max_workers=4)
result = engine.execute(workflow)
print(result.success)  # True
```

## Navigation

- **Parent Module**: [orchestrator](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
