# orchestration - Functional Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Orchestration submodule providing workflow and project orchestration capabilities. Coordinates complex workflows involving multiple modules (e.g., "Build -> Test -> Deploy"). Manages task dependencies and execution order.

## Design Principles
- **DAG execution**: Tasks are nodes in a directed acyclic graph.
- **Resilience**: State is persisted to allow recovery from crashes.

## Functional Requirements
1.  **Workflow Definition**: Define tasks and dependencies via config/code.
2.  **Execution**: Run tasks in correct topological order.

## Interface Contracts
- `OrchestrationEngine`: The runner core.
- `TaskOrchestrator`: Manages individual unit of work.
- `WorkflowManager`: Manages workflow definitions and execution.
- `ProjectManager`: High-level project lifecycle management.
- `ResourceManager`: Manages shared resources and dependencies.

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent**: [../SPEC.md](../SPEC.md)

