# Codomyrmex Agents — src/codomyrmex/collaboration/protocols

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Defines the foundational protocol vocabulary for multi-agent collaboration: state enums, message types, capability descriptors, an abstract coordination protocol interface, and four concrete protocol implementations (round-robin, broadcast, capability-routing, and consensus). Also includes `AgentCoordinator` for message routing and protocol execution, plus `AgentProxy`/`SwarmManager`/`TaskDecomposer` in `swarm.py` for simplified swarm orchestration.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `AgentState` | Enum: IDLE, BUSY, WAITING, ERROR, TERMINATED |
| `__init__.py` | `MessageType` | Enum: REQUEST, RESPONSE, BROADCAST, HANDOFF, STATUS, ERROR |
| `__init__.py` | `AgentMessage` | Dataclass for inter-agent messages with reply support |
| `__init__.py` | `AgentCapability` | Capability descriptor with optional input/output schemas |
| `__init__.py` | `AgentProtocol` | Abstract base requiring `execute()` and `select_agents()` |
| `__init__.py` | `BaseAgent` | Abstract agent with inbox, capabilities, and message sending |
| `__init__.py` | `AgentCoordinator` | Message router and protocol executor for registered agents |
| `__init__.py` | `RoundRobinProtocol` | Distributes tasks cyclically across agents |
| `__init__.py` | `BroadcastProtocol` | Sends task to all agents, collects results via `asyncio.gather` |
| `__init__.py` | `CapabilityRoutingProtocol` | Routes to agents matching a required capability |
| `__init__.py` | `ConsensusProtocol` | All agents process task; most-common result wins if quorum met |
| `swarm.py` | `AgentProxy` | Lightweight proxy for swarm task dispatch |
| `swarm.py` | `SwarmManager` | Simple swarm executor with majority-vote consensus |
| `swarm.py` | `TaskDecomposer` | Splits compound missions on " and " delimiters |

## Operating Contracts

- `AgentCoordinator.route_message()` delivers to specific agent if `receiver_id` is set; broadcasts to all others if `None`.
- `ConsensusProtocol` serializes results via `json.dumps` for comparison; quorum defaults to 0.5.
- All protocol `execute()` methods set agent state to BUSY during work and restore IDLE in `finally`.
- `AgentCoordinator.execute_protocol()` raises `ValueError` for unregistered protocol names.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library (`asyncio`, `json`, `uuid`, `logging`)
- **Used by**: `collaboration.agents` (imports AgentState, MessageType, AgentMessage, AgentCapability), `collaboration.communication`, `collaboration.coordination`

## Navigation

- **Parent**: [collaboration](../README.md)
- **Root**: [Root](../../../../README.md)
