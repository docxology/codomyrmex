# Collaboration Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `collaboration` module enables multi-agent coordination, real-time communication, and workflow orchestration. It provides a swarm-based architecture where multiple agents can work together on missions, with task decomposition, consensus voting, and coordinated execution through dedicated submodules for agents, communication, coordination, and protocols.


## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **Swarm orchestration**: `SwarmManager` coordinates multiple agents working in parallel on shared missions
- **Agent proxying**: `AgentProxy` provides a mock-friendly proxy interface for sending tasks to individual agents
- **Task decomposition**: `TaskDecomposer` breaks down complex missions into primitive tasks for distributed execution
- **Consensus voting**: Simple majority voting mechanism among swarm agents for collaborative decision-making
- **Modular submodule architecture**: Organized into `agents`, `communication`, `coordination`, and `protocols` submodules


## Key Components

| Component | Description |
|-----------|-------------|
| `SwarmManager` | Orchestrates multiple agents working together; distributes missions and collects results across the swarm |
| `AgentProxy` | Proxy for a Codomyrmex agent with name, role, and `send_task()` interface for task dispatch |
| `TaskDecomposer` | Utility class with static `decompose()` method for breaking complex missions into primitive subtasks |
| `agents` | Submodule containing agent definitions and capabilities |
| `communication` | Submodule for inter-agent messaging and real-time communication channels |
| `coordination` | Submodule for workflow coordination and synchronization primitives |
| `protocols` | Submodule defining collaboration protocols including the swarm protocol |

## Quick Start

```python
from codomyrmex.collaboration import SwarmManager, AgentProxy, TaskDecomposer

# Create agents
engineer = AgentProxy(name="Engineer", role="implementation")
reviewer = AgentProxy(name="Reviewer", role="code_review")

# Build a swarm
swarm = SwarmManager()
swarm.add_agent(engineer)
swarm.add_agent(reviewer)

# Execute a mission across the swarm
results = swarm.execute("Implement and review authentication module")
for agent_name, result in results.items():
    print(f"{agent_name}: {result}")

# Consensus voting
approved = swarm.consensus_vote("Deploy to production?")
print(f"Approved: {approved}")

# Decompose a complex task
subtasks = TaskDecomposer.decompose("Build full-stack user management")
for task in subtasks:
    print(f"  - {task}")
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k collaboration -v
```

## Related Modules

- [agents](../agents/) - AI agent framework providing the underlying agent infrastructure
- [orchestrator](../orchestrator/) - Higher-level workflow execution and orchestration

## Navigation

- **Source**: [src/codomyrmex/collaboration/](../../../src/codomyrmex/collaboration/)
- **Parent**: [docs/modules/](../README.md)
