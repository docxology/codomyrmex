# Swarm Orchestration — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a self-contained swarm orchestration framework with six agent roles, a topic-routed message bus, capability-based agent pooling, DAG task decomposition with topological ordering, and three consensus strategies. Each component operates independently and composes through shared protocol types.

## Architecture

Five modules: `protocol.py` (shared vocabulary: roles, messages, task types), `pool.py` (agent registry with load-balanced assignment), `message_bus.py` (pub/sub with wildcard topics), `decomposer.py` (keyword heuristic DAG decomposition + Kahn's topological sort), `consensus.py` (majority/weighted/veto voting).

## Key Classes

### `SwarmAgent`

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | `str` | Unique identifier |
| `role` | `AgentRole` | CODER, REVIEWER, ARCHITECT, TESTER, DOCUMENTER, DEVOPS |
| `capabilities` | `set[str]` | Capability tags (e.g., "python", "security") |
| `active_tasks` | `int` | Currently assigned task count |
| `max_concurrent` | `int` | Concurrency limit (default 3) |
| `load` (property) | `float` | `active_tasks / max_concurrent` |
| `available` (property) | `bool` | `active_tasks < max_concurrent` |

### `AgentPool`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `agent: SwarmAgent` | `None` | Add agent to pool |
| `assign` | `task: TaskAssignment` | `SwarmAgent` | Filter by role+caps, select least-loaded |
| `release` | `agent_id: str` | `None` | Decrement active_tasks |
| `agents_by_role` | `role: AgentRole` | `list[SwarmAgent]` | Filter agents by role |
| `status` | — | `dict` | Pool summary: total, available, by-role counts |

### `MessageBus`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `subscribe` | `subscriber_id, topic, handler` | `None` | Add topic subscription |
| `unsubscribe` | `subscriber_id, topic` | `int` | Remove subscriptions; returns count removed |
| `publish` | `topic: str, message: SwarmMessage` | `int` | Deliver to matching subscribers; returns count |
| `recent_messages` | `limit: int` | `list[SwarmMessage]` | Last N messages from history |

### `TaskDecomposer`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `decompose` | `task: str` | `list[SubTask]` | Keyword heuristic decomposition into role-based sub-tasks |
| `execution_order` | `subtasks: list[SubTask]` | `list[SubTask]` | Kahn's topological sort |
| `leaf_tasks` | `subtasks: list[SubTask]` | `list[SubTask]` | Terminal tasks with no dependents |

### `ConsensusEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `resolve` | `votes: list[Vote], strategy: str, threshold: float` | `ConsensusResult` | Dispatch to majority/weighted/veto strategy |

## Dependencies

- **Internal**: `codomyrmex.logging_monitoring`
- **External**: Standard library only (`uuid`, `time`, `enum`, `dataclasses`, `collections.deque`)

## Constraints

- `MessageBus` history limit: 1000 messages, halved on overflow.
- `TaskDecomposer._PHASE_MAP` maps keyword sets to roles with sequential dependency edges.
- Default decomposition (no keyword match): CODER -> TESTER -> REVIEWER chain.
- `ConsensusEngine` deadlock threshold: score exactly at threshold boundary.
- `AgentPool` least-loaded selection: `min(candidates, key=lambda a: a.load)`.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `AssignmentError` raised when no agent matches role/capability requirements.
- `CyclicDependencyError` raised when topological sort detects fewer results than inputs.
- `ConsensusResult.decision == Decision.DEADLOCK` when no votes cast.
- `ConsensusResult.decision == Decision.VETOED` when any agent rejects in veto mode.
- All errors logged before propagation.
