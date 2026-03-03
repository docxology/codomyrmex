# Collaboration

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Collaboration module provides multi-agent collaboration capabilities including agent management, communication channels, task coordination, consensus protocols, leader election, and swarm behavior. It enables multiple AI agents to work together on complex tasks through structured communication and task decomposition.

## Architecture Overview

```
collaboration/
├── __init__.py              # Public API (40+ exports)
├── models.py                # Task, TaskResult, TaskPriority, TaskStatus, AgentStatus, SwarmStatus
├── exceptions.py            # CollaborationError hierarchy (12 exception types)
├── mcp_tools.py             # MCP tools (swarm_submit_task, pool_status, list_agents)
├── agents/                  # Agent management (workers, supervisors, registry)
├── communication/           # Channels, broadcasting, direct messaging
├── coordination/            # Task management, consensus, leader election
├── protocols/               # Message passing, swarm behavior, routing protocols
└── swarm/                   # SwarmManager, AgentPool, MessageBus, TaskDecomposer
```

## Key Classes and Functions

**`SwarmManager`** -- High-level swarm orchestration managing agent pools and task distribution.

**`AgentPool`** -- Pool of agents with load balancing.

**`MessageBus`** -- Inter-agent message bus for communication.

**`TaskDecomposer`** -- Breaks complex tasks into subtasks for parallel execution.

**Protocol classes:** `RoundRobinProtocol`, `BroadcastProtocol`, `CapabilityRoutingProtocol`, `ConsensusProtocol`.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `swarm_submit_task` | Submit a task to the swarm for execution | `task: dict` | Safe |
| `pool_status` | Get current agent pool status | (none) | Safe |
| `list_agents` | List agents in the collaboration system | (none) | Safe |

## Related Modules

- [`agents`](../agents/readme.md) -- Individual agent implementations
- [`orchestrator`](../orchestrator/readme.md) -- Workflow orchestration

## Navigation

- **Source**: [src/codomyrmex/collaboration/](../../../../src/codomyrmex/collaboration/)
- **Parent**: [All Modules](../README.md)
