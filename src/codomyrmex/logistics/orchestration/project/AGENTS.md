# Codomyrmex Agents — src/codomyrmex/logistics/orchestration/project

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Implements the core project orchestration module for Codomyrmex, providing task and workflow management, inter-module coordination, project templates, progress tracking, resource management, parallel execution, and error handling.

## Active Components

- `workflow_manager.py` - Workflow definitions and execution engine
- `workflow_dag.py` - DAG-based workflow dependency resolution
- `task_orchestrator.py` - Task coordination and dependency management
- `project_manager.py` - Project lifecycle and template management
- `resource_manager.py` - Resource allocation and tracking
- `orchestration_engine.py` - Central orchestration session management
- `parallel_executor.py` - Parallel task execution support
- `documentation_generator.py` - Automatic README.md and AGENTS.md generation
- `mcp_tools.py` - Model Context Protocol tool definitions
- `templates/` - Project template JSON files
- `__init__.py` - Module exports and convenience functions

## Key Classes and Functions

### workflow_manager.py
- **`WorkflowManager`** - Manages workflow definitions and execution
- **`WorkflowStep`** - Individual step in a workflow with name, module, action, parameters
- **`WorkflowStatus`** - Enum: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
- **`WorkflowExecution`** - Tracks workflow execution state and results

### task_orchestrator.py
- **`TaskOrchestrator`** - Coordinates task execution with dependency resolution
- **`Task`** - Task definition with name, module, action, dependencies, priority
- **`TaskStatus`** - Enum: PENDING, RUNNING, COMPLETED, FAILED, BLOCKED
- **`TaskPriority`** - Enum: LOW, NORMAL, HIGH, CRITICAL
- **`TaskResult`** - Contains success status, output, error, duration
- **`TaskResource`** - Resource requirements for tasks

### project_manager.py
- **`ProjectManager`** - High-level project lifecycle management
- **`Project`** - Project definition with name, description, tasks, resources
- **`ProjectTemplate`** - Reusable project structure templates
- **`ProjectType`** - Enum: WEB_APPLICATION, DATA_PIPELINE, AI_ANALYSIS, etc.
- **`ProjectStatus`** - Enum: PLANNING, ACTIVE, PAUSED, COMPLETED, ARCHIVED

### resource_manager.py
- **`ResourceManager`** - Manages shared resources and allocations
- **`Resource`** - Resource definition with type, capacity, availability
- **`ResourceType`** - Enum: CPU, MEMORY, GPU, DISK, NETWORK, API_QUOTA
- **`ResourceStatus`** - Enum: AVAILABLE, ALLOCATED, EXHAUSTED
- **`ResourceAllocation`**, **`ResourceUsage`** - Tracking structures

### orchestration_engine.py
- **`OrchestrationEngine`** - Central engine coordinating all managers
- **`OrchestrationSession`** - Active session with context and state
- **`SessionStatus`** - Enum: INITIALIZING, ACTIVE, PAUSED, COMPLETED, ERROR
- **`OrchestrationContext`** - Session context with parameters and history

### documentation_generator.py
- **`DocumentationGenerator`** - Generates documentation for projects and directories
  - Scans directories for structure analysis
  - Creates README.md with directory overview
  - Creates AGENTS.md with component documentation

### mcp_tools.py
- **`get_mcp_tools()`** - Returns available MCP tool instances
- **`get_mcp_tool_definitions()`** - Returns tool definitions for AI consumption
- **`execute_mcp_tool(tool_name, **params)`** - Executes named tool

## Operating Contracts

- All managers support lazy singleton initialization
- Tasks execute in dependency order with parallel execution where possible
- Resource allocation prevents over-subscription
- Session state persists for recovery after failures
- MCP tools follow standard Model Context Protocol format

## Signposting

- **Dependencies**: Uses `logging_monitoring`, integrates with performance monitoring
- **Parent Directory**: [orchestration](../README.md) - Parent module documentation
- **Related Modules**:
  - `templates/` - Project template definitions
  - `schedule/` - Scheduling capabilities
  - `task/` - Queue management
- **Project Root**: [../../../../../README.md](../../../../../README.md) - Main project documentation
