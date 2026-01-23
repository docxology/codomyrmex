# Orchestrator - MCP Tool Specification

This document outlines the specification for tools within the Orchestrator module that are intended to be integrated with the Model Context Protocol (MCP).

## General Considerations

- **Tool Integration**: This module provides workflow execution and multi-step task orchestration.
- **Configuration**: Workflows are defined in YAML/JSON and can be parameterized.

---

## Tool: `run_workflow`

### 1. Tool Purpose and Description

Executes a defined workflow, coordinating multiple steps and handling data flow between them. Supports sequential, parallel, and conditional execution patterns.

### 2. Invocation Name

`run_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `workflow_name` | `string` | Yes | Name or path of the workflow to execute | `"build_and_test"` |
| `parameters` | `object` | No | Parameters to pass to the workflow | `{"target": "production"}` |
| `dry_run` | `boolean` | No | If true, validate without executing | `false` |
| `timeout` | `integer` | No | Overall workflow timeout in seconds | `3600` |
| `parallel_limit` | `integer` | No | Max concurrent parallel steps | `4` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Overall status: "success", "failed", "partial" | `"success"` |
| `workflow_id` | `string` | Unique identifier for this execution | `"wf-abc123"` |
| `steps_completed` | `integer` | Number of steps completed | `5` |
| `steps_total` | `integer` | Total number of steps | `5` |
| `step_results` | `array[object]` | Results from each step | See below |
| `execution_time` | `number` | Total execution time in seconds | `45.2` |
| `error_message` | `string` | Error details if status is "failed" | `null` |

**Step result structure:**

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `step_name` | `string` | Name of the step |
| `status` | `string` | Step status |
| `output` | `any` | Step output data |
| `duration` | `number` | Step execution time |

### 5. Error Handling

- **Workflow Not Found**: Returns error if workflow definition doesn't exist
- **Parameter Validation**: Validates required parameters before execution
- **Step Failures**: Can be configured to continue, retry, or abort on step failure
- **Timeout**: Aborts workflow if overall timeout is exceeded

### 6. Idempotency

- **Idempotent**: Depends on workflow definition; some workflows may be idempotent

### 7. Usage Examples

```json
{
  "tool_name": "run_workflow",
  "arguments": {
    "workflow_name": "ci_pipeline",
    "parameters": {
      "branch": "main",
      "run_tests": true,
      "deploy_target": "staging"
    },
    "timeout": 1800
  }
}
```

### 8. Security Considerations

- **Access Control**: Workflows may require specific permissions
- **Secret Management**: Secrets should be injected at runtime, not stored in definitions
- **Sandboxing**: Consider sandboxing untrusted workflow steps

---

## Tool: `list_workflows`

### 1. Tool Purpose and Description

Lists all available workflow definitions with their metadata and execution status.

### 2. Invocation Name

`list_workflows`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `category` | `string` | No | Filter by workflow category | `"build"` |
| `include_running` | `boolean` | No | Include currently running instances | `true` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `workflows` | `array[object]` | List of workflow definitions |
| `running_count` | `integer` | Number of currently running workflows |

### 5. Error Handling

- Returns empty list if no workflows are defined

### 6. Idempotency

- **Idempotent**: Yes

---

## Tool: `create_workflow`

### 1. Tool Purpose and Description

Creates a new workflow definition from a specification.

### 2. Invocation Name

`create_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `name` | `string` | Yes | Workflow name | `"my_workflow"` |
| `definition` | `object` | Yes | Workflow definition object | See documentation |
| `overwrite` | `boolean` | No | Overwrite if exists | `false` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "created", "updated", or "error" |
| `workflow_path` | `string` | Path to the saved workflow |

### 5. Error Handling

- **Validation Error**: Returns error if definition is invalid
- **Already Exists**: Returns error if workflow exists and overwrite is false

### 6. Idempotency

- **Idempotent**: Yes, with overwrite=true

---

## Tool: `cancel_workflow`

### 1. Tool Purpose and Description

Cancels a running workflow execution.

### 2. Invocation Name

`cancel_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `workflow_id` | `string` | Yes | ID of the workflow execution to cancel | `"wf-abc123"` |
| `reason` | `string` | No | Reason for cancellation | `"User requested"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description |
|:-----------|:-----|:------------|
| `status` | `string` | "cancelled" or "error" |
| `steps_completed` | `integer` | Steps completed before cancellation |

### 5. Error Handling

- **Not Found**: Returns error if workflow_id doesn't exist
- **Already Completed**: Returns info if workflow already finished

### 6. Idempotency

- **Idempotent**: Yes

---

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
