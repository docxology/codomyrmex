# Multi-Agent Coordination — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides the agent class hierarchy and lifecycle management for multi-agent collaboration. Agents are identified by UUID, possess typed capabilities, and communicate through async message queues. A singleton registry enables discovery and health monitoring.

## Architecture

Layered inheritance: `AbstractAgent` (interface) -> `CollaborativeAgent` (base with inbox, heartbeat, metrics) -> `WorkerAgent` / `SupervisorAgent` (specializations). The `AgentRegistry` singleton uses a capability index (capability name -> set of agent IDs) for O(1) lookups and runs an async background health-check loop.

## Key Classes

### `CollaborativeAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `process_task` | `task: Task` | `TaskResult` | Tracks state (IDLE->BUSY->IDLE), delegates to `_execute_task`, records metrics |
| `start` | — | `None` | Sets `_running=True`, transitions to IDLE |
| `stop` | — | `None` | Sets `_running=False`, transitions to TERMINATED |
| `process_messages` | — | `None` | Async loop consuming inbox with registered MessageType handlers |
| `add_message` | `message: AgentMessage` | `None` | Enqueues a message to the async inbox |
| `register_handler` | `message_type: MessageType, handler: Callable` | `None` | Binds a handler to a message type |

### `WorkerAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_handler` | `capability_name: str, handler: Callable, description: str` | `None` | Registers a task handler and adds the capability |
| `can_handle_task` | `task: Task` | `bool` | Checks all required capabilities are present |
| `execute_batch` | `tasks: list[Task]` | `list[TaskResult]` | Runs tasks respecting `max_concurrent_tasks` via semaphore |

### `SupervisorAgent`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `delegate` | `task: Task` | `TaskResult` | Selects worker via strategy, retries on failure up to `max_retries` |
| `delegate_batch` | `tasks: list[Task], parallel: bool` | `list[TaskResult]` | Parallel or sequential batch delegation |
| `execute_workflow` | `tasks: list[Task], on_progress: Callable` | `dict[str, TaskResult]` | Dependency-aware execution with progress callbacks |

### `AgentRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `agent: CollaborativeAgent` | `str` | Adds agent, updates capability index, notifies listeners |
| `unregister` | `agent_id: str` | `bool` | Removes agent and cleans capability index |
| `find_by_capability` | `capability: str` | `list[CollaborativeAgent]` | O(1) lookup via index |
| `find_by_capabilities` | `capabilities: list[str]` | `list[CollaborativeAgent]` | Set intersection across capabilities |
| `start_health_monitoring` | — | `None` | Launches async heartbeat checker |
| `get_swarm_status` | — | `SwarmStatus` | Returns total/active/idle counts and uptime |

## Dependencies

- **Internal**: `collaboration.exceptions`, `collaboration.models`, `collaboration.protocols`
- **External**: Standard library only (`asyncio`, `uuid`, `threading`, `logging`, `datetime`)

## Constraints

- `AgentRegistry` is a thread-safe singleton; call `reset()` in tests to clear state.
- `SupervisorAgent` delegation strategies: `"round_robin"`, `"least_busy"`, `"capability"` (default).
- Zero-mock: real data only, `NotImplementedError` for unimplemented `_execute_task`.

## Error Handling

- `AgentBusyError` raised when `process_task` called on a BUSY agent.
- `AgentNotFoundError` raised by `AgentRegistry.get()` for unknown IDs.
- `CapabilityMismatchError` raised when no worker can handle required capabilities.
- `TaskExecutionError` raised after exhausting retries in `SupervisorAgent.delegate()`.
- `TaskDependencyError` raised on circular dependencies in `execute_workflow`.
- All errors logged before propagation.
