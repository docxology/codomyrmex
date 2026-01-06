# Project Orchestration - MCP Tool Specification

This document outlines the Model Context Protocol (MCP) tools provided by the Project Orchestration module for AI-driven project management and workflow automation.

## General Considerations

- **Session Management**: Tools can operate within orchestration sessions for context preservation
- **Resource Awareness**: All operations respect system resource limits and availability  
- **Error Recovery**: Tools include automatic retry and error recovery mechanisms
- **Performance Monitoring**: All tool executions are monitored for performance metrics
- **Dependency Resolution**: Tools automatically handle inter-module dependencies

---

## Tool: `execute_workflow`

### 1. Tool Purpose and Description

Executes a predefined or custom workflow with AI-guided parameter optimization and intelligent error handling.

### 2. Invocation Name

`execute_workflow`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `workflow_name` | `string` | Yes | Name of the workflow to execute | `"ai-analysis"` |
| `parameters` | `object` | No | Workflow-specific parameters | `{"code_path": "./src", "output_path": "./reports"}` |
| `session_id` | `string` | No | Orchestration session ID for context | `"session_123"` |
| `mode` | `string` | No | Execution mode: "sequential", "parallel", "resource_aware" | `"resource_aware"` |
| `timeout_seconds` | `integer` | No | Maximum execution time in seconds | `3600` |
| `resource_requirements` | `object` | No | Required resources for execution | `{"cpu": {"cores": 2}, "memory": {"gb": 4}}` |
| `priority` | `string` | No | Execution priority: "low", "normal", "high", "critical" | `"normal"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Execution status: "success", "failure", "timeout", "cancelled" | `"success"` |
| `session_id` | `string` | Session ID used for execution | `"session_123"` |
| `workflow_results` | `object` | Detailed results from each workflow step | `{"analyze_code": {"score": 8.5}, "generate_report": {"file": "report.html"}}` |
| `execution_time` | `number` | Total execution time in seconds | `245.67` |
| `resources_used` | `object` | Resources consumed during execution | `{"cpu_seconds": 120, "memory_mb": 512}` |
| `steps_completed` | `integer` | Number of workflow steps completed | `3` |
| `steps_total` | `integer` | Total number of workflow steps | `3` |
| `error_message` | `string` | Error description if status is "failure" | `"Module 'static_analysis' timeout after 300s"` |
| `metrics` | `object` | Performance and execution metrics | `{"tasks_executed": 5, "avg_task_time": 49.2}` |

### 5. Error Handling

- **Resource Unavailable**: Returns failure with resource allocation details
- **Timeout**: Returns partial results with timeout status
- **Module Unavailable**: Returns failure with missing module information
- **Workflow Not Found**: Returns failure with available workflow list
- **Parameter Validation**: Returns failure with parameter requirements

### 6. Idempotency

- **Idempotent**: No (by default)
- **Session-based Idempotency**: Available with session_id parameter
- **Explanation**: Workflow execution may have side effects (file creation, API calls). Use session management for controlled re-execution.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "execute_workflow",
  "arguments": {
    "workflow_name": "ai-analysis",
    "parameters": {
      "code_path": "./src/myproject",
      "output_path": "./analysis_results",
      "include_visualization": true,
      "ai_provider": "openai"
    },
    "mode": "resource_aware",
    "timeout_seconds": 1800
  }
}
```

### 8. Security Considerations

- **Path Validation**: All file paths are validated and sandboxed
- **Resource Limits**: Execution respects system resource quotas
- **API Security**: External API calls use secure credential management
- **Isolation**: Workflow execution is isolated from system processes

---

## Tool: `create_project`

### 1. Tool Purpose and Description

Creates a new project from a template with intelligent configuration and optional workflow execution.

### 2. Invocation Name

`create_project`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `project_name` | `string` | Yes | Unique name for the new project | `"ai-chatbot-analysis"` |
| `template_name` | `string` | No | Project template to use | `"ai_analysis"` |
| `description` | `string` | No | Project description | `"AI analysis of chatbot conversation data"` |
| `project_path` | `string` | No | Custom project directory path | `"./projects/chatbot-analysis"` |
| `author` | `string` | No | Project author/owner | `"John Doe"` |
| `tags` | `array` | No | Project tags for organization | `["ai", "chatbot", "analysis"]` |
| `config_overrides` | `object` | No | Override default template configuration | `{"ai": {"provider": "anthropic"}}` |
| `execute_workflow` | `string` | No | Workflow to execute after project creation | `"ai-analysis"` |
| `workflow_parameters` | `object` | No | Parameters for the workflow execution | `{"include_sentiment": true}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Creation status: "success", "failure" | `"success"` |
| `project_id` | `string` | Unique project identifier | `"ai-chatbot-analysis"` |
| `project_path` | `string` | Full path to created project | `"/home/user/projects/ai-chatbot-analysis"` |
| `template_used` | `string` | Template used for project creation | `"ai_analysis"` |
| `files_created` | `array` | List of files and directories created | `["src/", "data/", "config/analysis.json"]` |
| `workflow_executed` | `boolean` | Whether initial workflow was executed | `true` |
| `workflow_result` | `object` | Results from initial workflow execution | `{"success": true, "reports_generated": 3}` |
| `next_steps` | `array` | Suggested next actions | `["Configure data sources", "Run initial analysis"]` |
| `error_message` | `string` | Error description if status is "failure" | `"Project directory already exists"` |

### 5. Error Handling

- **Name Conflicts**: Returns failure if project name already exists
- **Directory Issues**: Returns failure if target directory is not writable
- **Template Not Found**: Returns failure with available template list
- **Resource Constraints**: Returns failure if insufficient disk space
- **Permission Errors**: Returns failure with permission requirements

### 6. Idempotency

- **Idempotent**: No
- **Explanation**: Creates files and directories that persist. Subsequent calls with same name will fail unless project is deleted first.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "create_project",
  "arguments": {
    "project_name": "ecommerce-code-review",
    "template_name": "ai_analysis", 
    "description": "AI-powered code review for e-commerce platform",
    "author": "Development Team",
    "tags": ["code-review", "ecommerce", "quality"],
    "config_overrides": {
      "analysis": {
        "focus_areas": ["security", "performance", "maintainability"],
        "exclude_patterns": ["*/vendor/*", "*/node_modules/*"]
      }
    },
    "execute_workflow": "ai-analysis"
  }
}
```

### 8. Security Considerations

- **Path Security**: Project paths are validated and restricted to safe locations
- **Template Security**: Templates are validated for malicious content
- **File Permissions**: Created files have appropriate security permissions
- **Resource Quotas**: Disk usage is monitored and limited

---

## Tool: `execute_task`

### 1. Tool Purpose and Description

Executes a single task with intelligent resource management and integration with other Codomyrmex modules.

### 2. Invocation Name

`execute_task`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `task_name` | `string` | Yes | Descriptive name for the task | `"analyze_python_code"` |
| `module` | `string` | Yes | Codomyrmex module to use | `"static_analysis"` |
| `action` | `string` | Yes | Module action/function to execute | `"analyze_code_quality"` |
| `parameters` | `object` | Yes | Parameters for the module action | `{"path": "./src", "include_security": true}` |
| `dependencies` | `array` | No | Task IDs this task depends on | `["task_123", "task_124"]` |
| `priority` | `string` | No | Task priority: "low", "normal", "high", "critical" | `"high"` |
| `timeout_seconds` | `integer` | No | Maximum execution time | `600` |
| `retry_count` | `integer` | No | Number of retries on failure | `3` |
| `resource_requirements` | `object` | No | Required resources | `{"memory": {"gb": 2}}` |
| `session_id` | `string` | No | Session for context preservation | `"session_456"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Task status: "completed", "failed", "cancelled", "timeout" | `"completed"` |
| `task_id` | `string` | Unique identifier for the executed task | `"task_789"` |
| `result` | `object` | Result data from the module action | `{"quality_score": 8.5, "issues_found": 12}` |
| `execution_time` | `number` | Task execution time in seconds | `45.2` |
| `memory_used_mb` | `number` | Peak memory usage during execution | `256` |
| `retry_attempts` | `integer` | Number of retry attempts made | `0` |
| `dependencies_satisfied` | `boolean` | Whether all dependencies were met | `true` |
| `resource_allocation` | `object` | Resources allocated to the task | `{"cpu_cores": 1, "memory_mb": 512}` |
| `error_message` | `string` | Error description if status is "failed" | `"Module timeout: static_analysis took too long"` |
| `metadata` | `object` | Additional execution metadata | `{"module_version": "1.2.0", "start_time": "2024-01-01T10:00:00Z"}` |

### 5. Error Handling

- **Module Import Errors**: Returns failure with module availability information
- **Parameter Validation**: Returns failure with required parameter details
- **Resource Allocation**: Returns failure if required resources unavailable
- **Timeout Handling**: Returns timeout status with partial results if available
- **Dependency Failures**: Returns failure if dependent tasks failed

### 6. Idempotency

- **Idempotent**: Depends on module action
- **Explanation**: Idempotency depends on the specific module action being executed. Read-only operations are typically idempotent.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "execute_task",
  "arguments": {
    "task_name": "generate_visualization",
    "module": "data_visualization", 
    "action": "create_bar_chart",
    "parameters": {
      "categories": ["Security", "Performance", "Maintainability"],
      "values": [8.5, 7.2, 9.1],
      "title": "Code Quality Metrics",
      "output_path": "./reports/quality_chart.png"
    },
    "priority": "normal",
    "dependencies": ["analyze_python_code"]
  }
}
```

### 8. Security Considerations

- **Module Sandboxing**: Tasks execute in controlled environments
- **Resource Isolation**: Resource usage is monitored and limited
- **Parameter Sanitization**: Input parameters are validated and sanitized
- **Output Validation**: Task outputs are validated before storage

---

## Tool: `get_system_status`

### 1. Tool Purpose and Description

Retrieves comprehensive system status including orchestration health, resource usage, and performance metrics.

### 2. Invocation Name

`get_system_status`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `include_detailed_metrics` | `boolean` | No | Include detailed performance metrics | `true` |
| `include_resource_health` | `boolean` | No | Include resource health information | `true` |
| `include_active_sessions` | `boolean` | No | Include active session information | `false` |
| `time_range_hours` | `integer` | No | Time range for historical metrics | `24` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `overall_status` | `string` | System health: "healthy", "degraded", "unhealthy" | `"healthy"` |
| `timestamp` | `string` | Status check timestamp | `"2024-01-01T12:00:00Z"` |
| `orchestration_engine` | `object` | Orchestration engine status | `{"active_sessions": 3, "healthy": true}` |
| `workflow_manager` | `object` | Workflow manager status | `{"total_workflows": 15, "running": 2}` |
| `task_orchestrator` | `object` | Task orchestrator status | `{"pending_tasks": 5, "running": 2, "completed": 45}` |
| `project_manager` | `object` | Project manager status | `{"total_projects": 8, "active": 3}` |
| `resource_manager` | `object` | Resource utilization | `{"cpu_usage": 45.2, "memory_usage": 60.1}` |
| `performance_metrics` | `object` | Performance statistics | `{"avg_task_time": 23.5, "success_rate": 98.2}` |
| `issues` | `array` | Current system issues | `["High memory usage on worker-2"]` |
| `recommendations` | `array` | System optimization suggestions | `["Consider adding more workers during peak hours"]` |

### 5. Error Handling

- **Component Unavailable**: Returns partial status with unavailable component list
- **Permission Errors**: Returns limited status information based on access level
- **Metric Collection Errors**: Returns status with warnings about incomplete metrics

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Read-only operation that returns current system state without side effects.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "get_system_status",
  "arguments": {
    "include_detailed_metrics": true,
    "include_resource_health": true,
    "time_range_hours": 6
  }
}
```

### 8. Security Considerations

- **Information Security**: Sensitive system information is filtered based on access level
- **Performance Impact**: Status collection is optimized to minimize system impact
- **Rate Limiting**: Frequent status requests are rate-limited to prevent abuse

---

## Tool: `manage_project`

### 1. Tool Purpose and Description

Manages project lifecycle operations including status updates, milestone tracking, and configuration management.

### 2. Invocation Name

`manage_project`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
|:---------------|:-----|:---------|:------------|:--------------|
| `project_name` | `string` | Yes | Name of the project to manage | `"chatbot-analysis"` |
| `operation` | `string` | Yes | Management operation: "status", "update", "milestone", "archive" | `"milestone"` |
| `parameters` | `object` | No | Operation-specific parameters | `{"milestone_name": "analysis_complete", "data": {...}}` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
|:-----------|:-----|:------------|:--------------|
| `status` | `string` | Operation status: "success", "failure" | `"success"` |
| `project_status` | `object` | Current project status | `{"name": "chatbot-analysis", "status": "active"}` |
| `operation_result` | `object` | Result of the management operation | `{"milestone_added": true, "total_milestones": 3}` |
| `error_message` | `string` | Error description if status is "failure" | `"Project not found"` |

### 5. Error Handling

- **Project Not Found**: Returns failure with available project list
- **Invalid Operation**: Returns failure with supported operation list
- **Permission Errors**: Returns failure with required permission details

### 6. Idempotency

- **Idempotent**: Depends on operation
- **Explanation**: Read operations (status) are idempotent, modification operations (update, milestone) may not be.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "manage_project",
  "arguments": {
    "project_name": "ecommerce-analysis",
    "operation": "milestone",
    "parameters": {
      "milestone_name": "initial_analysis_complete",
      "data": {
        "completion_date": "2024-01-01T15:30:00Z",
        "quality_score": 8.7,
        "issues_found": 23,
        "files_analyzed": 156
      }
    }
  }
}
```

### 8. Security Considerations

- **Project Access Control**: Operations are restricted based on project permissions
- **Data Validation**: All project data is validated before storage
- **Audit Trail**: All project modifications are logged for audit purposes

---

## Integration Examples

### AI-Driven Code Analysis Workflow
```json
{
  "tool_name": "create_project",
  "arguments": {
    "project_name": "ai-code-review",
    "template_name": "ai_analysis",
    "execute_workflow": "ai-analysis",
    "workflow_parameters": {
      "code_path": "./source-code",
      "focus_areas": ["security", "performance"],
      "ai_provider": "openai",
      "include_suggestions": true
    }
  }
}
```

### Multi-Step Analysis Pipeline
```json
[
  {
    "tool_name": "execute_task",
    "arguments": {
      "task_name": "static_analysis",
      "module": "static_analysis",
      "action": "analyze_code_quality",
      "parameters": {"path": "./src"}
    }
  },
  {
    "tool_name": "execute_task", 
    "arguments": {
      "task_name": "generate_chart",
      "module": "data_visualization",
      "action": "create_bar_chart",
      "dependencies": ["static_analysis"],
      "parameters": {
        "data_source": "${static_analysis.result}",
        "chart_type": "quality_metrics"
      }
    }
  },
  {
    "tool_name": "execute_task",
    "arguments": {
      "task_name": "ai_summary",
      "module": "ai_code_editing", 
      "action": "generate_code_snippet",
      "dependencies": ["static_analysis", "generate_chart"],
      "parameters": {
        "prompt": "Summarize code analysis: ${static_analysis.result}",
        "language": "markdown"
      }
    }
  }
]
```

---

## Best Practices for AI Integration

1. **Context Preservation**: Use session_id for related operations
2. **Resource Planning**: Specify resource requirements for complex tasks
3. **Error Recovery**: Implement retry logic for critical operations
4. **Progress Monitoring**: Use get_system_status to track long-running operations
5. **Result Chaining**: Use dependency mechanisms to chain related tasks
6. **Performance Optimization**: Monitor execution metrics and adjust parameters

---

## Error Codes Reference

- `RESOURCE_UNAVAILABLE`: Required resources not available
- `MODULE_NOT_FOUND`: Specified module not installed
- `WORKFLOW_NOT_FOUND`: Workflow definition not found
- `PROJECT_EXISTS`: Project name already in use
- `PERMISSION_DENIED`: Insufficient permissions for operation
- `TIMEOUT_EXCEEDED`: Operation exceeded time limit
- `DEPENDENCY_FAILED`: Required dependency task failed
- `INVALID_PARAMETERS`: Input parameters validation failed

---

*These MCP tools enable sophisticated AI-driven project management and workflow orchestration, providing intelligent automation capabilities across the entire Codomyrmex ecosystem.*

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
