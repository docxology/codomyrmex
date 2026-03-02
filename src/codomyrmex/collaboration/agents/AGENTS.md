# Codomyrmex Agents — src/codomyrmex/collaboration/agents

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Defines the agent hierarchy for collaborative workflows: an abstract interface (`AbstractAgent`), a concrete base (`CollaborativeAgent`) with messaging, heartbeat, and task lifecycle tracking, plus specializations for task execution (`WorkerAgent`, `SpecializedWorker`) and delegation (`SupervisorAgent`). A singleton `AgentRegistry` provides discovery, capability indexing, and health monitoring.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `base.py` | `AbstractAgent` | Abstract interface requiring `process_task`, `get_capabilities`, `get_status` |
| `base.py` | `CollaborativeAgent` | Concrete base with async inbox, heartbeat, message handlers, and task metrics |
| `worker.py` | `WorkerAgent` | Executes tasks via registered capability handlers with concurrency limits |
| `worker.py` | `SpecializedWorker` | Convenience subclass for single-capability workers |
| `supervisor.py` | `SupervisorAgent` | Delegates tasks to workers using round-robin, least-busy, or capability strategies |
| `registry.py` | `AgentRegistry` | Thread-safe singleton registry with capability index and heartbeat health checks |
| `registry.py` | `get_registry()` | Module-level accessor for the global registry instance |

## Operating Contracts

- Agents must be registered via `AgentRegistry.register()` before participating in swarm workflows.
- `CollaborativeAgent.process_task()` raises `AgentBusyError` if the agent is already processing; callers must handle this.
- `WorkerAgent._execute_task()` raises `CapabilityMismatchError` when no handler matches the task's required capabilities.
- `SupervisorAgent` retries failed delegations up to `max_retries` times before returning a failure `TaskResult`.
- `AgentRegistry` health monitoring marks agents as `AgentState.ERROR` when heartbeat exceeds `heartbeat_timeout`.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `collaboration.exceptions` (AgentBusyError, AgentNotFoundError, CapabilityMismatchError, TaskDependencyError, TaskExecutionError), `collaboration.models` (AgentStatus, SwarmStatus, Task, TaskResult, TaskStatus), `collaboration.protocols` (AgentCapability, AgentMessage, AgentState, MessageType)
- **Used by**: `collaboration.coordination` (TaskManager, ConsensusBuilder), `collaboration.communication`, `collaboration.swarm`

## Navigation

- **Parent**: [collaboration](../README.md)
- **Root**: [Root](../../../../README.md)
