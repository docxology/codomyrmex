# logistics/orchestration

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Orchestration submodule for logistics. Provides workflow and project orchestration capabilities including task management, resource allocation, project lifecycle, and MCP tool integration. Re-exports all functionality from the `project` submodule.

## Key Exports

### Core Manager Classes

- **`WorkflowManager`** -- Manages workflow definitions, step sequencing, and execution tracking
- **`TaskOrchestrator`** -- Orchestrates task scheduling, execution, and result collection
- **`ProjectManager`** -- Manages project lifecycle from creation through completion
- **`ResourceManager`** -- Tracks and allocates resources across tasks and projects
- **`OrchestrationEngine`** -- Top-level engine coordinating workflows, tasks, projects, and resources
- **`DocumentationGenerator`** -- Generates documentation from orchestration artifacts

### Workflow Types

- **`WorkflowStep`** -- A single step in a workflow definition
- **`WorkflowStatus`** -- Status enum for workflows
- **`WorkflowExecution`** -- Tracks the execution state of a workflow instance

### Task Types

- **`Task`** -- A unit of work with dependencies and resource requirements
- **`TaskStatus`** -- Status enum for tasks
- **`TaskPriority`** -- Priority levels for task scheduling
- **`TaskResult`** -- Outcome of task execution
- **`TaskResource`** -- Resource requirements for a task

### Project Types

- **`Project`** -- A project containing multiple tasks and workflows
- **`ProjectTemplate`** -- Reusable project templates
- **`ProjectType`** -- Classification enum for projects
- **`ProjectStatus`** -- Status enum for project lifecycle

### Resource Types

- **`Resource`** -- A manageable resource (compute, storage, etc.)
- **`ResourceType`** -- Classification enum for resources
- **`ResourceStatus`** -- Availability status for resources
- **`ResourceAllocation`** -- Tracks resource assignment to tasks
- **`ResourceUsage`** -- Resource consumption metrics

### Session and Engine Types

- **`OrchestrationSession`** -- A session encapsulating an orchestration run
- **`SessionStatus`** -- Status enum for sessions
- **`OrchestrationContext`** -- Context passed through orchestration steps

### MCP Tool Integration

- **`get_mcp_tools()`** -- Get available MCP tool instances
- **`get_mcp_tool_definitions()`** -- Get MCP tool JSON schema definitions
- **`execute_mcp_tool()`** -- Execute an MCP tool by name with arguments

### Convenience Functions

- **`create_workflow_steps()`** -- Create a list of workflow steps from configuration
- **`create_task()`** -- Create a new task instance
- **`create_project()`** -- Create a new project instance
- **`execute_workflow()`** -- Execute a workflow end-to-end
- **`execute_task()`** -- Execute a single task
- **`get_workflow_manager()`** -- Get or create the WorkflowManager singleton
- **`get_task_orchestrator()`** -- Get or create the TaskOrchestrator singleton
- **`get_project_manager()`** -- Get or create the ProjectManager singleton
- **`get_resource_manager()`** -- Get or create the ResourceManager singleton
- **`get_orchestration_engine()`** -- Get or create the OrchestrationEngine singleton

## Directory Contents

- `__init__.py` - Re-exports from the project submodule (95 lines)
- `project/` - Core implementation directory containing workflow, task, project, and resource managers
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [logistics](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
