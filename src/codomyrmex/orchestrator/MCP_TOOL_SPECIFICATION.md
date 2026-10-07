# Orchestrator - MCP Tool Specification

This document specifies the MCP tools implemented in the Orchestrator module's `mcp_tools.py`. They are surfaced by the PAI MCP bridge as `codomyrmex.<name>`. The fractal task tool is documented in `fractals/MCP_TOOL_SPECIFICATION.md`.

> **Note:** The orchestrator has no MCP tools to run, create or cancel named workflows. Listing Claude Code workflows is provided by the PAI bridge's static `codomyrmex.list_workflows` tool.

## General Considerations

- **Tool Integration**: This module provides scheduler metrics, workflow DAG analysis and swarm-topology task execution.
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
| :--- | :--- | :--- |
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
| :--- | :--- | :--- | :--- | :--- |
| `tasks` | `array[object]` | Yes | List of task descriptors with id and dependencies | See example |

Each task object:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | `string` | Yes | Unique task identifier |
| `dependencies` | `array[string]` | No | IDs of tasks this task depends on |

### 4. Output Schema

| Field | Type | Description |
| :--- | :--- | :--- |
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

## Tool: `orchestrator_run_dag`

### 1. Tool Purpose and Description

Executes a list of tasks with a swarm topology (`fan_out`, `fan_in`, `pipeline` or `broadcast`) and aggregates their outputs. Tasks can only run bounded expressions or callables from a fixed registry; arbitrary code is rejected.

### 2. Invocation Name

`orchestrator_run_dag`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `topology` | `string` | Yes | `"fan_out"`, `"fan_in"`, `"pipeline"` or `"broadcast"` | `"fan_out"` |
| `tasks` | `array[object]` | Yes | 1-256 task objects (see below) | see example |
| `broadcast_message` | `object` | No | Payload injected in `broadcast` mode | `{"event": "start"}` |
| `max_workers` | `integer` | No | Parallel workers, 1-32 (default `8`) | `4` |

Each task object has:

- `id` (string): unique, non-empty task ID (default `task_<index>`);
- `fn_expr` (string): a bounded expression over pure builtins, e.g. `"len('hello')"`, **or** `fn` (string): one of `builtins.abs`, `builtins.int`, `builtins.len`, `builtins.max`, `builtins.min`, `builtins.round`, `builtins.str`, `builtins.sum`; with neither, the task echoes its arguments;
- optional `args` (array), `kwargs` (object) and `metadata` (object).

### 4. Output Schema

| Field | Type | Description |
| :--- | :--- | :--- |
| `status` | `string` | `"success"` when no task failed, `"failed"` when some did, `"error"` for invalid input |
| `topology` | `string` | Topology used |
| `success_count` / `error_count` | `integer` | Task outcome counts |
| `results` | `array` | Per task: `task_id`, `output`, `error`, `duration_ms` |
| `merged_outputs` | `object` | Merged outputs (topology dependent) |
| `errors` | `array` | Task errors |
| `message` | `string` | `"DAG execution failed: <reason>"` (only for `"error"`) |

### 5. Example Usage

```json
// Request:
{
  "topology": "fan_out",
  "tasks": [
    {"id": "a", "fn_expr": "len('hello')"},
    {"id": "b", "fn": "builtins.abs", "args": [-3]}
  ]
}

// Response:
{
  "status": "success",
  "topology": "fan_out",
  "success_count": 2,
  "error_count": 0,
  "results": [
    {"task_id": "a", "output": 5, "error": "", "duration_ms": 0.01},
    {"task_id": "b", "output": 3, "error": "", "duration_ms": 0.001}
  ],
  "merged_outputs": {},
  "errors": []
}
```

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
