# Codomyrmex Agents — src/codomyrmex/logistics/orchestration

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides workflow and project orchestration capabilities for coordinating complex multi-module operations. This module re-exports functionality from the project submodule and serves as the main entry point for orchestration features.

## Active Components

- `project/` - Core orchestration implementation subdirectory
- `__init__.py` - Re-exports all orchestration functionality
- `SPEC.md` - Module specification
- `README.md` - Module documentation

## Key Classes and Functions (Re-exported from project/)

### Core Managers
- **`WorkflowManager`** - Manages workflow definitions and execution
- **`TaskOrchestrator`** - Coordinates individual tasks and dependencies
- **`ProjectManager`** - High-level project lifecycle management
- **`ResourceManager`** - Manages shared resources and dependencies
- **`OrchestrationEngine`** - Central engine for orchestration sessions
- **`DocumentationGenerator`** - Generates README.md and AGENTS.md files

### Data Classes
- **`WorkflowStep`**, **`WorkflowStatus`**, **`WorkflowExecution`** - Workflow structures
- **`Task`**, **`TaskStatus`**, **`TaskPriority`**, **`TaskResult`**, **`TaskResource`** - Task structures
- **`Project`**, **`ProjectTemplate`**, **`ProjectType`**, **`ProjectStatus`** - Project structures
- **`Resource`**, **`ResourceType`**, **`ResourceStatus`**, **`ResourceAllocation`**, **`ResourceUsage`** - Resource structures
- **`OrchestrationSession`**, **`SessionStatus`**, **`OrchestrationContext`** - Session structures

### Convenience Functions
- **`create_workflow_steps(name, steps)`** - Creates new workflow with steps
- **`create_task(name, module, action, **kwargs)`** - Creates task instance
- **`create_project(name, description, template)`** - Creates project instance
- **`execute_workflow(name, **params)`** - Executes named workflow
- **`execute_task(task)`** - Executes single task
- **`get_*_manager()`** - Factory functions for singleton manager instances

### MCP Tools
- **`get_mcp_tools()`**, **`get_mcp_tool_definitions()`**, **`execute_mcp_tool()`** - MCP integration

## Operating Contracts

- All orchestration classes use lazy initialization for singleton instances
- MCP tools are available for AI-driven orchestration
- Integrates with logging_monitoring for all logging
- Coordinates with all other Codomyrmex modules

## Signposting

- **Implementation**: All functionality implemented in `project/` subdirectory
- **Parent Directory**: [logistics](../README.md) - Parent module documentation
- **Related Modules**:
  - `schedule/` - Advanced scheduling with cron and recurring patterns
  - `task/` - Task queue management and job scheduling
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
