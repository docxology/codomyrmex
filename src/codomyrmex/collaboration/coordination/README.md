# collaboration/coordination

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Task coordination submodule. Provides task distribution, consensus protocols, and leader election algorithms for multi-agent collaboration. Includes a dependency-aware task manager with configurable scheduling strategies, a consensus builder with multiple voting mechanisms, and four leader election algorithm implementations.

## Key Exports

### Task Management

- **`SchedulingStrategy`** -- Task scheduling strategy enumeration (FIFO, priority, round-robin, etc.)
- **`TaskQueue`** -- Priority-aware task queue
- **`DependencyGraph`** -- DAG-based task dependency tracker
- **`TaskManager`** -- Distributes tasks to agents respecting dependencies and scheduling strategy

### Consensus

- **`VoteType`** -- Vote type enumeration (approve, reject, abstain)
- **`Vote`** -- Individual vote from an agent
- **`Proposal`** -- Proposal submitted for consensus voting
- **`VotingResult`** -- Aggregated voting outcome
- **`VotingMechanism`** -- Voting rule (majority, unanimous, weighted, etc.)
- **`ConsensusBuilder`** -- Orchestrates proposal submission, voting rounds, and result tallying

### Leader Election

- **`ElectionState`** -- Election lifecycle state enumeration
- **`ElectionResult`** -- Election outcome with winner and vote counts
- **`LeaderElection`** -- Base class for election algorithms
- **`BullyElection`** -- Bully algorithm; highest-priority agent wins
- **`RingElection`** -- Ring algorithm; token-passing election
- **`RandomElection`** -- Random selection among candidates
- **`RotatingLeadership`** -- Round-robin leadership rotation

## Directory Contents

- `__init__.py` - Package init; re-exports from task_manager, consensus, and leader_election
- `task_manager.py` - TaskQueue, DependencyGraph, and TaskManager
- `consensus.py` - Voting types, ConsensusBuilder, and VotingMechanism
- `leader_election.py` - Election algorithms (Bully, Ring, Random, Rotating)
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [collaboration](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
