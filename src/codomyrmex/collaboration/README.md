# Collaboration Module

**Version**: v0.2.1 | **Status**: Active | **Last Updated**: March 2026

## Overview

The collaboration module provides multi-agent collaboration capabilities including agent management, communication channels, task coordination, and message-passing protocols. It features a robust **Swarm** system for orchestrating complex workflows across multiple specialized agents.

## Key Components

### Swarm Management (`collaboration.swarm`)

- **`SwarmManager`** — Central orchestrator for the swarm. Integrates pool, bus, and decomposer. Supports async task execution with result waiting.
- **`AgentPool`** — Manages a collection of agents, providing capability-based routing and load balancing.
- **`MessageBus`** — In-process topic-based pub/sub for inter-agent communication. Supports wildcards and async handlers.
- **`TaskDecomposer`** — Breaks complex missions into dependency-ordered sub-tasks using role-based heuristics.
- **`ConsensusEngine`** — Resolves votes using majority, weighted, or veto strategies.

### Protocols (`collaboration.protocols`)

- **`RoundRobinProtocol`** — Distributes tasks evenly.
- **`BroadcastProtocol`** — Sends tasks to all agents.
- **`CapabilityRoutingProtocol`** — Routes based on specific agent skills.
- **`ConsensusProtocol`** — Requires agreement for task completion.

### Agents (`collaboration.agents`)

- **`WorkerAgent`** — Executes specific tasks based on capabilities.
- **`SupervisorAgent`** — Orchestrates workers and manages workflows.
- **`AgentRegistry`** — Central registry for all collaborative agents.

## Quick Start

```python
import asyncio
from codomyrmex.collaboration import (
    SwarmManager, 
    SwarmAgent, 
    AgentRole,
    SwarmMessage,
    SwarmMessageType
)

async def main():
    manager = SwarmManager()
    manager.register_agent(SwarmAgent("coder-1", AgentRole.CODER))
    
    # In a real scenario, the agent would be a separate process or object
    # subscribing to the bus. For this example, we'll just show the call.
    # results = await manager.execute_mission("Add auth and tests")
    # print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/collaboration/
```

## Documentation

- [SPEC.md](SPEC.md) — Technical specification.
- [AGENTS.md](AGENTS.md) — Guidelines for agent integration.
- [PAI.md](PAI.md) — PAI integration notes.
