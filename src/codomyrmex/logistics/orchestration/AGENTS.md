# Codomyrmex Agents — src/codomyrmex/logistics/orchestration

## Signposting
- **Parent**: [logistics](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [project](project/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Orchestration submodule providing workflow and project orchestration capabilities. Manages complex workflows involving multiple modules, task dependencies, and execution order.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Module initialization
- `project/` – Project orchestration submodule

## Key Classes and Functions

### Core Classes
- `WorkflowManager` – Manages workflow definitions and execution
- `TaskOrchestrator` – Coordinates individual tasks and dependencies
- `ProjectManager` – High-level project lifecycle management
- `ResourceManager` – Manages shared resources and dependencies
- `OrchestrationEngine` – Core orchestration engine
- `DocumentationGenerator` – Generates README.md and AGENTS.md files

### Data Classes
- `WorkflowStep` – Workflow step definition
- `WorkflowStatus` – Workflow status enumeration
- `WorkflowExecution` – Workflow execution context
- `Task` – Task definition
- `TaskStatus` – Task status enumeration
- `TaskPriority` – Task priority enumeration
- `TaskResult` – Task execution result
- `Project` – Project definition
- `ProjectTemplate` – Project template definition
- `Resource` – Resource definition
- `ResourceType` – Resource type enumeration
- `ResourceStatus` – Resource status enumeration

### Convenience Functions
- `get_workflow_manager() -> WorkflowManager` – Get default workflow manager
- `get_task_orchestrator() -> TaskOrchestrator` – Get default task orchestrator
- `get_project_manager() -> ProjectManager` – Get default project manager
- `get_resource_manager() -> ResourceManager` – Get default resource manager
- `get_orchestration_engine() -> OrchestrationEngine` – Get default orchestration engine
- `execute_workflow(name: str, **params)` – Execute a workflow
- `execute_task(task: Task)` – Execute a single task

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [logistics](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation

