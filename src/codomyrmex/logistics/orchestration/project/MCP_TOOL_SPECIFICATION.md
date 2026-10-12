# Project Orchestration - MCP Tool Specification

This document describes the Model Context Protocol (MCP) tools provided by the Project Orchestration package for project management and workflow automation.

## General Considerations

- **Class-based adapter**: The tools are served by `OrchestrationMCPTools` in `mcp_tools.py`. `get_mcp_tool_definitions()` returns their schemas and `execute_mcp_tool(tool_name, arguments)` runs one. They do not use `@mcp_tool`, so the PAI MCP bridge does not auto-discover them; a host must register the adapter itself.
- **Shared state**: The adapter uses the process-wide orchestration engine, workflow manager, task orchestrator, project manager and resource manager, so workflows and projects persist across calls within one process.
- **Result format**: Every call returns an `MCPToolResult` with `status` (`"success"` or `"failure"`) and `data` of the form `{"data": <tool result>, "metadata": {"timestamp": "<ISO 8601>", ...}}`. Failures carry an `error` (`MCPErrorDetail`) with `error_type` and `error_message`; unknown tool names fail with `"Tool '<name>' not found"`.

| Tool | Purpose |
| :--- | :--- |
| `execute_workflow` | Execute a registered workflow |
| `create_workflow` | Register a workflow from a list of steps |
| `list_workflows` | List registered workflows |
| `create_project` | Create a project, optionally from a template |
| `list_projects` | List projects |
| `execute_task` | Execute a single module action as a task |
| `get_system_status` | Return the orchestration engine's system status |
| `get_health_status` | Return the orchestration engine's health status |
| `allocate_resources` | Allocate resources for a user |
| `create_complex_workflow` | Create and execute a workflow with dependencies |

---

## Tool: `execute_workflow`

### 1. Tool Purpose and Description

Executes a workflow with the orchestration engine.

### 2. Invocation Name

`execute_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `workflow_name` | `string` | Yes | Name of the workflow to execute | `"ai-analysis"` |
| `parameters` | `object` | No | Workflow parameters (default `{}`) | `{"code_path": "./src"}` |
| `session_id` | `string` | No | Session ID for tracking | `"session_123"` |

### 4. Output Schema (Return Value)

`data.data` is the engine's execution result; `data.metadata` adds `workflow_name` and `session_id`. `status` is `"success"` when the result reports `success: true`.

## Tool: `create_workflow`

### 1. Tool Purpose and Description

Registers a new workflow from a list of steps.

### 2. Invocation Name

`create_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | Yes | Workflow name | `"lint-and-test"` |
| `steps` | `array[object]` | Yes | Steps as `{"name", "module", "action", "parameters"?, "dependencies"?, "timeout"?}` | `[{"name": "lint", "module": "static_analysis", "action": "analyze_file"}]` |
| `description` | `string` | No | Workflow description | `"Lint then test"` |

### 4. Output Schema (Return Value)

`data.data` contains `workflow_name`, `steps_count` and `description`.

## Tool: `list_workflows`

### 1. Tool Purpose and Description

Lists the registered workflows.

### 2. Invocation Name

`list_workflows`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

`data.data` contains `workflows` and `count`.

## Tool: `create_project`

### 1. Tool Purpose and Description

Creates a project, optionally from a template.

### 2. Invocation Name

`create_project`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | Yes | Project name | `"chatbot-analysis"` |
| `template` | `string` | No | Project template (default `"ai_analysis"`) | `"ai_analysis"` |
| `description` | `string` | No | Project description | `"Analyse chatbot logs"` |
| `path` | `string` | No | Project directory path | `"./projects/chatbot-analysis"` |

### 4. Output Schema (Return Value)

`data.data` contains `project_name`, `project_type`, `project_path`, `template_used` and `workflows`.

## Tool: `list_projects`

### 1. Tool Purpose and Description

Lists the known projects.

### 2. Invocation Name

`list_projects`

### 3. Input Schema (Parameters)

None.

### 4. Output Schema (Return Value)

`data.data` contains `projects` (each with `name`, `type`, `status`, `path`, `created_at`) and `count`.

## Tool: `execute_task`

### 1. Tool Purpose and Description

Runs one module action as an orchestrated task.

### 2. Invocation Name

`execute_task`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | Yes | Task name | `"analyze_python_code"` |
| `module` | `string` | Yes | Module to execute | `"static_analysis"` |
| `action` | `string` | Yes | Action to execute | `"analyze_file"` |
| `parameters` | `object` | No | Action parameters (default `{}`) | `{"file_path": "src/app.py"}` |
| `priority` | `string` | No | `low`, `normal`, `high` or `critical` (default `normal`) | `"high"` |
| `dependencies` | `array[string]` | No | Task dependencies (default `[]`) | `[]` |

### 4. Output Schema (Return Value)

`data.data` is the task result; `data.metadata` adds `task_name`, `module` and `action`.

## Tool: `get_system_status`

### 1. Tool Purpose and Description

Returns the orchestration engine's system status.

### 2. Invocation Name

`get_system_status`

### 3. Input Schema (Parameters)

None.

## Tool: `get_health_status`

### 1. Tool Purpose and Description

Returns the orchestration engine's health status.

### 2. Invocation Name

`get_health_status`

### 3. Input Schema (Parameters)

None.

## Tool: `allocate_resources`

### 1. Tool Purpose and Description

Allocates system resources to a user through the resource manager.

### 2. Invocation Name

`allocate_resources`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `string` | Yes | User identifier | `"agent-1"` |
| `requirements` | `object` | Yes | Resource requirements | `{"cpu": {"cores": 2}}` |

## Tool: `create_complex_workflow`

### 1. Tool Purpose and Description

Creates and executes a workflow with multiple dependent steps.

### 2. Invocation Name

`create_complex_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `name` | `string` | Yes | Workflow name | `"release-pipeline"` |
| `workflow_definition` | `object` | Yes | Workflow definition with steps and dependencies | `{"steps": []}` |

---

## Usage Example

```python
from codomyrmex.logistics.orchestration.project import execute_mcp_tool

result = execute_mcp_tool("list_projects", {})
print(result.status, result.data["data"]["count"])
```

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)

<!-- markdownlint-configure-file { "MD024": { "siblings_only": true } } -->
