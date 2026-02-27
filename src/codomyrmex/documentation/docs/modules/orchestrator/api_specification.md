# Orchestrator Module API Specification

**Version**: v0.1.7 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `orchestrator` module provides a flexible way to discover, configure, and execute Python scripts in the project. It abstracts script execution into a managed "orchestration" layer.

## 2. Core Components

### 2.1 Execution
- **`run_orchestrator()`**: The main entry point for the orchestration CLI.
- **`get_script_config()`**: Retrieves configuration for a specific script.

### 2.2 Workflow Engine
- **Workflow DAG execution**: Define tasks with dependencies; engine resolves execution order.
- **Parallel execution**: Independent tasks run concurrently with configurable resource limits.
- **Retry logic**: Configurable retries with backoff for transient failures.
- **Progress streaming**: Real-time callbacks for task state transitions.

### 2.3 MCP Tools
- **`get_scheduler_metrics()`**: Returns current scheduler state (active jobs, queue depth, throughput).
- **`analyze_workflow_dependencies(tasks)`**: Validates a task list for DAG validity and returns the execution order.

## 3. Usage Example

```python
from codomyrmex.orchestrator import run_orchestrator

# Launch the interactive orchestrator menu
run_orchestrator()
```

```python
# MCP tool usage — analyze workflow
from codomyrmex.orchestrator.mcp_tools import analyze_workflow_dependencies

tasks = [
    {"id": "build", "depends_on": []},
    {"id": "test", "depends_on": ["build"]},
    {"id": "deploy", "depends_on": ["test"]},
]
result = analyze_workflow_dependencies(tasks)
# result: {"execution_order": ["build", "test", "deploy"], "parallel_groups": [...]}
```
