# Agent Guidelines - Collaboration

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Multi-agent collaboration, shared state, and coordination patterns.

## Module Overview

Multi-agent collaboration framework for distributed task coordination, shared state management, and
swarm orchestration. Provides `SwarmManager` as central orchestrator, `MessageBus` for inter-agent
messaging, and `ConsensusEngine` for voting-based decisions. Three MCP tools (`swarm_submit_task`,
`pool_status`, `list_agents`) expose swarm operations to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `SwarmManager`, `SwarmAgent`, `AgentRole`, `MessageBus`, `ConsensusEngine` |
| `swarm_manager.py` | `SwarmManager` — central orchestrator for agent pool |
| `swarm_agent.py` | `SwarmAgent` — agent participating in the swarm |
| `message_bus.py` | `MessageBus` — pub/sub inter-agent messaging |
| `consensus.py` | `ConsensusEngine` — voting and consensus building |
| `mcp_tools.py` | MCP tools: `swarm_submit_task`, `pool_status`, `list_agents` |

## Swarm Management

The **`SwarmManager`** is the central orchestrator for agent collaboration. It manages the agent pool, coordinates messages, and handles task decomposition.

### Key Classes

- **`SwarmManager`** — Central orchestrator for the swarm.
- **`SwarmAgent`** — An agent participating in the swarm.
- **`AgentRole`** — Role of an agent (ARCHITECT, CODER, TESTER, etc.).
- **`MessageBus`** — Inter-agent messaging system.
- **`SwarmMessageType`** — Types of messages (TASK_ASSIGNMENT, RESULT, etc.).
- **`ConsensusEngine`** — Voting and consensus builder.

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `swarm_submit_task` | Submit a task to the agent swarm for distributed execution | Safe |
| `pool_status` | Get the current status of the collaboration swarm pool and protocols | Safe |
| `list_agents` | List available agent capabilities and coordination protocols | Safe |

## Agent Instructions

1. **Register as a SwarmAgent** — Use the correct `AgentRole` to receive appropriate tasks.
2. **Subscribe to Topics** — Listen on `tasks.role.{your_role}` for assignments.
3. **Report Results** — Publish results back to `results.agent.{your_id}` so the `SwarmManager` can collect them.
4. **Use Async Handlers** — Prefer `async` functions for message bus subscribers to avoid blocking.
5. **Respect Load Balancing** — The `AgentPool` tracks your active tasks based on assignments and releases.

## Common Patterns

### Mission Execution Flow

1. `SwarmManager` decomposes mission into tasks.
2. `SwarmManager` assigns task to an agent via `MessageBus`.
3. Agent processes task and publishes `SwarmMessageType.RESULT` back to the bus.
4. `SwarmManager` collects the result and proceeds to the next task.

### Example Agent Implementation

```python
async def on_task(message: SwarmMessage):
    if message.message_type == SwarmMessageType.TASK_ASSIGNMENT:
        # Process task...
        # Publish result back
        await manager.bus.publish(
            f"results.agent.{agent_id}",
            SwarmMessage(
                message_type=SwarmMessageType.RESULT,
                sender=agent_id,
                payload={"task_id": task_id, "result": {"status": "success"}}
            )
        )
```

## Operating Contracts

- Agents must subscribe to `tasks.role.{your_role}` topic BEFORE the `SwarmManager` starts dispatching
- `MessageBus` is async — all publish/subscribe operations must be `await`ed
- `SwarmManager.collect_result()` blocks until all task results are received — set a timeout
- `ConsensusEngine` requires at least 2 participating agents to produce a valid consensus
- **DO NOT** use `SwarmAgent` outside of a `SwarmManager` context — lifecycle depends on manager

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `swarm_submit_task`, `pool_status`, `list_agents` | TRUSTED |
| **Architect** | Read + Design | `pool_status`, `list_agents` — swarm architecture review, agent topology design | OBSERVED |
| **QATester** | Validation | `pool_status`, `list_agents` — swarm health verification, agent availability checks | OBSERVED |
| **Researcher** | Read-only | `pool_status`, `list_agents` — inspect swarm state and agent capabilities | SAFE |

### Engineer Agent
**Use Cases**: Submitting tasks to the swarm during EXECUTE, monitoring pool status, managing agent coordination workflows.

### Architect Agent
**Use Cases**: Designing swarm topologies, reviewing agent role assignments, planning coordination patterns.

### QATester Agent
**Use Cases**: Verifying swarm health during VERIFY, confirming agent availability and task completion.

### Researcher Agent
**Use Cases**: Inspecting swarm pool status and agent capabilities for research analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
