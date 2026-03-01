# Orchestrator - MCP Tool Specification

This document specifies the MCP tools **currently implemented** in the Orchestrator module.

> **Note:** This spec was updated to reflect the actual implementation in `mcp_tools.py`.
> Previously documented tools (`run_workflow`, `list_workflows`, `create_workflow`, `cancel_workflow`)
> are **not yet implemented** — they are planned future additions. See the Planned Tools section below.

## General Considerations

- **Tool Integration**: This module provides scheduler metrics and workflow DAG analysis.
- **Category**: `orchestrator`
- **Auto-discovered**: Yes (via `@mcp_tool` decorator in `mcp_tools.py`)

---

## Tool: `get_scheduler_metrics`

### 1. Tool Purpose and Description

Retrieve the current metrics of the Orchestrator's `AsyncScheduler`, including jobs scheduled, completed, failed, cancelled, and total execution time.

### 2. Invocation Name

`get_scheduler_metrics`

### 3. Input Schema (Parameters)

None — this tool takes no parameters.

### 4. Output Schema

| Field | Type | Description |
|:------|:-----|:------------|
| `status` | `string` | `"success"` or `"error"` |
| `metrics.total_jobs` | `integer` | Total jobs scheduled |
| `metrics.completed` | `integer` | Jobs completed successfully |
| `metrics.failed` | `integer` | Jobs that failed |
| `metrics.cancelled` | `integer` | Jobs that were cancelled |
| `metrics.execution_time` | `float` | Cumulative execution time in seconds |
| `message` | `string` | Error message (only on `"error"` status) |

### 5. Example Usage

```json
// Request: no parameters
// Response (success):
{
  "status": "success",
  "metrics": {
    "total_jobs": 42,
    "completed": 38,
    "failed": 2,
    "cancelled": 2,
    "execution_time": 314.7
  }
}
```

---

## Tool: `analyze_workflow_dependencies`

### 1. Tool Purpose and Description

Analyze a proposed workflow task graph (DAG) for cyclic dependencies. Validates that the workflow can be scheduled and returns a valid execution order if the graph is acyclic.

### 2. Invocation Name

`analyze_workflow_dependencies`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `tasks` | `array[object]` | Yes | List of task descriptors with id and dependencies | See example |

Each task object:

| Field | Type | Required | Description |
|:------|:-----|:---------|:------------|
| `id` | `string` | Yes | Unique task identifier |
| `dependencies` | `array[string]` | No | IDs of tasks this task depends on |

### 4. Output Schema

| Field | Type | Description |
|:------|:-----|:------------|
| `status` | `string` | `"success"` or `"error"` |
| `valid_dag` | `boolean` | `true` if no cycles detected |
| `execution_order` | `array[string]` | Topological order of task IDs (on success) |
| `message` | `string` | Error details (on `"error"` or cycle detected) |

### 5. Example Usage

```json
// Request:
{
  "tasks": [
    {"id": "build", "dependencies": []},
    {"id": "test", "dependencies": ["build"]},
    {"id": "deploy", "dependencies": ["test"]}
  ]
}

// Response (valid DAG):
{
  "status": "success",
  "valid_dag": true,
  "execution_order": ["build", "test", "deploy"]
}

// Response (cycle detected):
{
  "status": "error",
  "valid_dag": false,
  "message": "Cycle detected: deploy -> build -> deploy"
}
```

---

## Planned Tools (Not Yet Implemented)

The following tools are documented as future work. They do **not** exist in the current implementation
and will raise `NotImplementedError` until implemented.

| Tool Name | Description |
|:----------|:------------|
| `run_workflow` | Execute a named workflow with parameters and dry-run support |
| `list_workflows` | List all available workflow definitions |
| `create_workflow` | Create a new workflow definition from a task graph |
| `cancel_workflow` | Cancel a running workflow by ID |
