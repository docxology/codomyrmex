# Task Coordination — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides consensus mechanisms, leader election algorithms, and task scheduling for multi-agent coordination. Designed for collaborative decision-making and dependency-aware workflow execution.

## Architecture

Three independent subsystems: (1) `VotingMechanism` / `ConsensusBuilder` for agreement, (2) four `LeaderElection` implementations for coordinator selection, and (3) `TaskManager` with a `TaskQueue` (min-heap) and `DependencyGraph` (adjacency lists) for scheduling.

## Key Classes

### `VotingMechanism`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_proposal` | `title, description, proposer_id, deadline, metadata` | `Proposal` | Create a proposal for voting |
| `cast_vote` | `proposal_id, voter_id, vote: VoteType, reason` | `Vote` | Cast YES/NO/ABSTAIN vote |
| `tally_votes` | `proposal_id, total_voters: int` | `VotingResult` | Compute result using quorum and threshold |

### `ConsensusBuilder`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `propose_value` | `key, agent_id, value` | `None` | Submit a proposed value for a key |
| `check_consensus` | `key, total_agents` | `Any or None` | Returns value if convergence threshold met |
| `reach_consensus` | `key, agents, value_fn, max_rounds` | `Any or None` | Iterative rounds until consensus or limit |

### `BullyElection` / `RingElection` / `RandomElection`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `elect` | `agents: list[CollaborativeAgent]` | `ElectionResult` | Run election, return leader ID and metadata |

### `RotatingLeadership`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `rotate` | — | `CollaborativeAgent or None` | Advance to next leader in rotation |
| `get_current_leader` | — | `CollaborativeAgent or None` | Current leader without rotation |

### `TaskManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `submit` | `task: Task` | `str` | Enqueue with priority and dependency tracking |
| `get_next_task` | `agent: CollaborativeAgent` | `Task or None` | Capability-matched, dependency-ready assignment |
| `complete_task` | `result: TaskResult` | `None` | Mark complete, notify callbacks, clean graph |
| `run_workflow` | `agents, on_progress` | `dict[str, TaskResult]` | Auto-assign and execute all queued tasks |

### `DependencyGraph`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `get_ready_tasks` | `completed: set[str]` | `list[str]` | Tasks with all dependencies satisfied |
| `has_cycle` | — | `bool` | DFS cycle detection |

## Dependencies

- **Internal**: `collaboration.agents.base`, `collaboration.exceptions`, `collaboration.models`, `collaboration.protocols`
- **External**: Standard library only (`asyncio`, `heapq`, `random`, `logging`, `uuid`)

## Constraints

- `VotingMechanism` requires quorum in [0, 1] and threshold in [0, 1]; raises `ValueError` otherwise.
- `TaskQueue` uses negated priority for max-heap behavior on Python's min-heap.
- `TaskManager.max_concurrent` limits active tasks per agent.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised for invalid proposals, expired deadlines, or unknown protocols.
- `TaskNotFoundError` raised when completing an unknown task.
- `ElectionResult.success=False` with error message when no agents or no healthy agents available.
- All errors logged before propagation.
