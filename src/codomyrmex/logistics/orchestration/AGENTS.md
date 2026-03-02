# Logistics Orchestration -- Agent Coordination

## Purpose

Facade package that re-exports the orchestration API from the `project/` subpackage. Agents interact with this module to access workflow management, task orchestration, resource allocation, project lifecycle management, and parallel execution.

## Key Components

| Component | Source | Role |
|-----------|--------|------|
| `WorkflowManager` | `project/workflow_manager.py` | Workflow CRUD, JSON config loading, DAG creation, parallel execution |
| `TaskOrchestrator` | `project/task_orchestrator.py` | Priority-queued task scheduling with dependency resolution |
| `OrchestrationEngine` | `project/orchestration_engine.py` | Session management, health checks, metrics, event handling |
| `ProjectManager` | `project/project_manager.py` | Project lifecycle with directory scaffolding and doc generation |
| `ResourceManager` | `project/resource_manager.py` | Thread-safe resource allocation with capacity limits (11 resource types) |
| `ParallelExecutor` | `project/parallel_executor.py` | `ThreadPoolExecutor`-based parallel task execution with timeouts |
| `WorkflowDAG` | `project/workflow_dag.py` | DAG validation, cycle detection (DFS), topological sort (Kahn's algorithm) |
| `OrchestrationMCPTools` | `project/mcp_tools.py` | Class-based MCP tool exposure (10 tools) |

## Operating Contracts

- **Thread safety**: `OrchestrationEngine` uses `threading.RLock` for session state; `ResourceManager` uses `threading.Lock` for allocation. Agents may call concurrently.
- **Singletons**: Access shared instances via `get_workflow_manager()`, `get_task_orchestrator()`, `get_orchestration_engine()`, `get_resource_manager()`. Each lazily initialised on first call.
- **MCP pattern**: Uses class-based `OrchestrationMCPTools` (not `@mcp_tool` decorators). Tools are registered via `get_tool_definitions()` and dispatched through `execute_tool()`.
- **Persistence**: `WorkflowManager` reads workflow definitions from `config/workflows/production/*.json` and persists execution data to `.workflows/`.
- **DAG validation**: Agents must validate task graphs before execution -- `WorkflowDAG` detects cycles via DFS and computes topological order with Kahn's algorithm.

## Integration Points

- **Logging**: All components use `codomyrmex.logging_monitoring.core.logger_config.get_logger`.
- **Documentation**: `ProjectManager` delegates to `DocumentationGenerator` for RASP file scaffolding.
- **Events**: `OrchestrationEngine` fires events via an internal event handler registry.
- **Performance**: `ResourceManager` and `OrchestrationEngine` optionally integrate with `codomyrmex.performance` for monitoring.

## Navigation

- **Parent**: [logistics/](../README.md)
- **Children**: [project/](project/AGENTS.md)
- **Siblings**: [routing/](../routing/AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
