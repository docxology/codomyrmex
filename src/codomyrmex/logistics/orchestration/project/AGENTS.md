# Orchestration Project -- Agent Coordination

## Purpose

Core implementation of the Codomyrmex orchestration system. Provides workflow management, task scheduling, resource allocation, parallel execution, DAG validation, project lifecycle management, and MCP tool exposure for AI-driven orchestration.

## Key Components

| Component | File | Role |
|-----------|------|------|
| `OrchestrationEngine` | `orchestration_engine.py` | Central coordinator: sessions (thread-safe `RLock`), health checks, metrics, event dispatch |
| `WorkflowManager` | `workflow_manager.py` | Workflow CRUD, JSON config loading from `config/workflows/production/`, DAG + parallel execution |
| `TaskOrchestrator` | `task_orchestrator.py` | Priority queue scheduler (5 levels), background daemon thread, dependency + resource checks |
| `ResourceManager` | `resource_manager.py` | Thread-safe capacity allocation (11 `ResourceType` values), usage tracking, burst limits |
| `ParallelExecutor` | `parallel_executor.py` | `ThreadPoolExecutor` runner with dependency resolution, timeouts, context manager protocol |
| `WorkflowDAG` | `workflow_dag.py` | DAG validation, DFS cycle detection, Kahn's topological sort, Mermaid visualisation |
| `ProjectManager` | `project_manager.py` | Project lifecycle (7 `ProjectType` values), directory scaffolding, `DocumentationGenerator` integration |
| `DocumentationGenerator` | `documentation_generator.py` | Template-based RASP doc generation with `{{variable}}` substitution |
| `OrchestrationMCPTools` | `mcp_tools.py` | Class-based MCP exposure (see below) |

## MCP Tool Integration (Class-Based Pattern)

This module uses a **class-based MCP pattern** instead of `@mcp_tool` decorators. `OrchestrationMCPTools` provides:

| MCP Tool | Description |
|----------|-------------|
| `execute_workflow` | Execute a named workflow with parameters and optional session tracking |
| `create_workflow` | Create a workflow from a list of step definitions |
| `list_workflows` | List all registered workflow names |
| `create_project` | Create a new project with template and directory scaffolding |
| `list_projects` | List all active projects |
| `execute_task` | Submit and execute a single task with priority and dependencies |
| `get_system_status` | Aggregate status across all orchestration subsystems |
| `get_health_status` | Component-level health including uptime and error counts |
| `allocate_resources` | Allocate compute/memory/disk/network resources by user ID |
| `create_complex_workflow` | Create and execute a multi-step workflow with dependency graph |

Tools are registered via `get_tool_definitions()` and dispatched through `execute_tool(tool_name, arguments)`.

## Operating Contracts

- **Singleton access**: Use `get_orchestration_engine()`, `get_workflow_manager()`, `get_task_orchestrator()`, `get_resource_manager()`, `get_project_manager()` for shared instances.
- **Thread safety**: `OrchestrationEngine` guards session state with `RLock`; `ResourceManager` guards allocations with `Lock`; `TaskOrchestrator` uses `ThreadPoolExecutor` for background processing.
- **Zero-mock policy**: `OrchestrationMCPTools.__init__` raises `RuntimeError` if `codomyrmex.model_context_protocol` is not importable.
- **Workflow persistence**: Workflow definitions loaded from `config/workflows/production/*.json`; execution state stored in `.workflows/`.
- **DAG uniqueness**: Task names must be unique within a `WorkflowDAG`. Cycles raise `CycleDetectedError`.

## Navigation

- **Parent**: [orchestration/](../AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
