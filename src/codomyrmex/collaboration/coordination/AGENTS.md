# Codomyrmex Agents — src/codomyrmex/collaboration/coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Provides three coordination subsystems for multi-agent workflows: (1) consensus and voting via `VotingMechanism` and `ConsensusBuilder`, (2) leader election with bully, ring, random, and rotating strategies, and (3) task scheduling via `TaskManager` with a priority queue, dependency graph, and load-balanced assignment.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `consensus.py` | `VotingMechanism` | Proposal creation, vote casting, and tally with configurable quorum and threshold |
| `consensus.py` | `ConsensusBuilder` | Iterative value convergence across agents with configurable threshold |
| `consensus.py` | `Proposal`, `Vote`, `VotingResult` | Data classes for voting workflow |
| `leader_election.py` | `LeaderElection` | Abstract base for election protocols with history tracking |
| `leader_election.py` | `BullyElection` | Highest-priority agent wins; filters unhealthy agents |
| `leader_election.py` | `RingElection` | Simulated ring traversal election |
| `leader_election.py` | `RandomElection` | Random selection from healthy agents |
| `leader_election.py` | `RotatingLeadership` | Round-robin leadership rotation with term tracking |
| `task_manager.py` | `TaskManager` | Priority scheduling, dependency resolution, agent assignment, and workflow execution |
| `task_manager.py` | `TaskQueue` | Heap-based priority queue with lazy removal |
| `task_manager.py` | `DependencyGraph` | Tracks task dependencies with topological ordering and cycle detection |

## Operating Contracts

- `VotingMechanism.cast_vote()` raises `ValueError` if the proposal is not active or the deadline has passed.
- `VotingMechanism.tally_votes()` removes the proposal from active state and records the result.
- All election implementations filter out agents in `AgentState.ERROR` before selecting a leader.
- `TaskManager.get_next_task()` respects both dependency ordering and agent capability matching.
- `TaskManager.cancel()` cannot cancel running tasks; only queued tasks are cancellable.
- `DependencyGraph.has_cycle()` uses DFS with a recursion stack to detect cycles.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `collaboration.agents.base` (CollaborativeAgent), `collaboration.exceptions` (TaskNotFoundError), `collaboration.models` (Task, TaskResult, TaskStatus), `collaboration.protocols` (AgentState)
- **Used by**: `collaboration.agents.supervisor` (SupervisorAgent.execute_workflow), higher-level orchestration modules

## Navigation

- **Parent**: [collaboration](../README.md)
- **Root**: [Root](../../../../README.md)
