# collaboration/protocols

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Multi-agent coordination protocols. Provides protocols and utilities for agent collaboration and swarm behavior, including message passing, capability-based routing, round-robin task distribution, broadcast fan-out, and consensus-driven decision-making.

## Key Exports

### Enums

- **`AgentState`** -- States an agent can be in: `IDLE`, `BUSY`, `WAITING`, `ERROR`, `TERMINATED`
- **`MessageType`** -- Types of inter-agent messages: `REQUEST`, `RESPONSE`, `BROADCAST`, `HANDOFF`, `STATUS`, `ERROR`

### Data Classes

- **`AgentMessage`** -- Message passed between agents with sender/receiver IDs, content, metadata, and reply support via `create_reply()`
- **`AgentCapability`** -- Describes a capability an agent possesses, including optional input/output JSON schemas

### Abstract Base Classes

- **`AgentProtocol`** -- ABC for coordination protocols; subclasses implement `execute()` and `select_agents()`
- **`BaseAgent`** -- ABC for collaborative agents with inbox queue, capability tracking, and `process_task()` interface

### Coordination Infrastructure

- **`AgentCoordinator`** -- Central coordinator that manages agent registration, message routing (direct and broadcast), protocol execution, and capability-based agent discovery

### Protocol Implementations

- **`RoundRobinProtocol`** -- Distributes tasks to agents in sequential round-robin fashion, one agent per task
- **`BroadcastProtocol`** -- Fans out tasks to all available agents via `asyncio.gather` and collects all results
- **`CapabilityRoutingProtocol`** -- Routes tasks to agents matching a required capability, preferring idle agents
- **`ConsensusProtocol`** -- Requires quorum-based consensus among agents; uses JSON-serialized result voting with configurable quorum threshold (default 50%)

## Directory Contents

- `__init__.py` - Protocol classes, agent base classes, coordinator, and all enum/dataclass definitions (329 lines)
- `swarm.py` - Extended swarm behavior implementations
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [collaboration](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
