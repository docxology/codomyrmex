# Collaboration Protocols — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Defines the protocol layer for multi-agent collaboration: shared enums, message wire format, abstract protocol interface, and four concrete coordination strategies. The `AgentCoordinator` orchestrates message routing and protocol dispatch.

## Architecture

Two files: `__init__.py` contains the full protocol stack (enums, data types, abstract classes, coordinator, four protocol implementations), and `swarm.py` provides a simplified swarm facade (`SwarmManager`) for basic task distribution and voting.

## Key Classes

### `AgentMessage`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID auto-generated |
| `sender_id` | `str` | Sender agent ID |
| `receiver_id` | `str or None` | None = broadcast |
| `message_type` | `MessageType` | REQUEST, RESPONSE, BROADCAST, HANDOFF, STATUS, ERROR |
| `content` | `Any` | Payload |
| `metadata` | `dict` | Extensible metadata |
| `reply_to` | `str or None` | ID of message being replied to |

### `AgentCoordinator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_agent` | `agent: BaseAgent` | `None` | Add agent to routing table |
| `route_message` | `message: AgentMessage` | `None` | Deliver direct or broadcast |
| `execute_protocol` | `protocol_name: str, task: Any` | `Any` | Select agents and run protocol |
| `find_agents_with_capability` | `capability: str` | `list[BaseAgent]` | Filter by capability |

### `RoundRobinProtocol`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `select_agents` | `task, available_agents` | `list[BaseAgent]` | One agent by cyclic index |
| `execute` | `task, agents` | `Any` | Process on single agent |

### `ConsensusProtocol`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `execute` | `task, agents` | `Any` | All process; most common result returned if quorum met |

### `SwarmManager` (swarm.py)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add_agent` | `agent: AgentProxy` | `None` | Add to swarm |
| `execute` | `mission: str` | `dict[str, str]` | Distribute mission to all agents |
| `consensus_vote` | `proposal: str` | `bool` | Simple majority vote |

## Dependencies

- **Internal**: None (this is the foundational protocol layer)
- **External**: Standard library only (`asyncio`, `json`, `uuid`, `abc`, `enum`, `dataclasses`)

## Constraints

- `AgentMessage.create_reply()` swaps sender/receiver and sets `reply_to`.
- `ConsensusProtocol` uses JSON serialization for result comparison; non-serializable results use `default=str`.
- `SwarmManager.consensus_vote()` is simplified (all agents vote True); real implementations should override.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised for unknown protocol names and no-agent scenarios.
- Protocol `execute()` methods raise `ValueError` when `agents` list is empty.
- `ConsensusProtocol` raises `ValueError` when consensus not reached or all agents fail.
- All errors logged before propagation.
