# Personal AI Infrastructure — Logistics Orchestration/Project Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `logistics/orchestration/project`

## Overview

Project-level orchestration for multi-component projects and cross-repo workflows.
This module provides an `OrchestrationMCPTools` class that exposes workflow and
project management operations to PAI agents.

**Architecture note**: Unlike most codomyrmex modules, this module uses a
**class-based MCP tools pattern** rather than the `@mcp_tool` decorator. Its tools
are accessed via `get_mcp_tool_definitions()` and `execute_mcp_tool()` rather than
through the auto-discovery bridge scan.

## PAI Capabilities

### Workflow Execution

```python
from codomyrmex.logistics.orchestration.project.mcp_tools import (
    execute_mcp_tool, get_mcp_tool_definitions
)

# Execute a named workflow
result = execute_mcp_tool("execute_workflow", {
    "workflow_name": "ai_code_review",
    "parameters": {"target": "src/codomyrmex/"},
    "session_id": "pai-session-001",
})

# Create a multi-step workflow
result = execute_mcp_tool("create_workflow", {
    "name": "security_pipeline",
    "steps": [
        {"name": "scan", "module": "security", "action": "scan_vulnerabilities"},
        {"name": "review", "module": "agents", "action": "review", "dependencies": ["scan"]},
    ]
})
```

### Project Management

```python
# Create a new project from template
result = execute_mcp_tool("create_project", {
    "name": "my_project",
    "template": "ai_analysis",
    "description": "AI-assisted code analysis project",
})

# List all projects
result = execute_mcp_tool("list_projects", {})
```

## MCP Tools

This module exposes 9 tools via the `OrchestrationMCPTools` class (class-based
registration, not `@mcp_tool` auto-discovery):

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `execute_workflow` | Execute a named workflow with the orchestration engine | Safe |
| `create_workflow` | Create a new workflow with specified steps and dependencies | Safe |
| `list_workflows` | List all available workflows | Safe |
| `create_project` | Create a new project from an optional template | Safe |
| `list_projects` | List all available projects with status | Safe |
| `execute_task` | Execute a single module action as a Task | Safe |
| `get_system_status` | Get comprehensive system status report | Safe |
| `get_health_status` | Get system health status | Safe |
| `allocate_resources` | Allocate system resources for a user/session | Safe |

**Access pattern:**
```python
from codomyrmex.logistics.orchestration.project.mcp_tools import (
    get_mcp_tool_definitions,
    execute_mcp_tool,
    get_mcp_tools,          # Returns OrchestrationMCPTools instance
)
```

## PAI Algorithm Phase Mapping

| Phase | Logistics/Project Contribution |
|-------|-------------------------------|
| **OBSERVE** (1/7) | `get_system_status`, `list_projects` — assess current project state |
| **PLAN** (3/7) | `create_workflow` — codify the execution plan as a named workflow with DAG dependencies |
| **EXECUTE** (5/7) | `execute_workflow`, `execute_task` — run planned workflows; `allocate_resources` before parallel work |
| **VERIFY** (6/7) | `get_health_status` — confirm system health after workflow completion |

### Concrete PAI Usage Pattern

PAI PLAN phase uses this module to define and persist multi-step workflows:

```python
# PAI PLAN — define execution as a workflow
execute_mcp_tool("create_workflow", {
    "name": "sprint_11_execution",
    "steps": [
        {"name": "fix_bugs", "module": "coding", "action": "apply_fixes"},
        {"name": "run_tests", "module": "coding", "action": "execute_tests", "dependencies": ["fix_bugs"]},
        {"name": "update_docs", "module": "documentation", "action": "generate", "dependencies": ["run_tests"]},
    ]
})
# PAI EXECUTE — run the workflow
execute_mcp_tool("execute_workflow", {"workflow_name": "sprint_11_execution"})
```

## Architecture Role

**Service Layer** — Multi-component project and workflow orchestration. Uses
`OrchestrationEngine`, `WorkflowManager`, `TaskOrchestrator`, `ProjectManager`,
and `ResourceManager` internally. Depends on `logging_monitoring` (Foundation)
and `model_context_protocol` (Foundation) for MCP registration.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../../PAI.md](../../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../../../PAI.md](../../../../../PAI.md) — Authoritative PAI system bridge doc
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
- **Related**: [../../../orchestrator/PAI.md](../../../orchestrator/PAI.md) — Orchestrator module (uses `@mcp_tool` pattern)
