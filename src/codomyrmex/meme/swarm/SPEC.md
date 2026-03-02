# Swarm -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models swarm intelligence and collective behavior using Reynolds flocking rules (separation, alignment, cohesion), consensus algorithms, and quorum sensing. Agents operate in 3D space with position and velocity vectors, and the engine tracks emergent coherence metrics across simulation steps.

## Architecture

Boids-algorithm simulation with consensus overlay. `SwarmEngine` manages a population of `SwarmAgent` objects and advances the simulation per step via `update_flock`. Each step computes separation, alignment, and cohesion forces for each agent based on neighbors within a perception radius. Consensus is reached via state-based voting with configurable thresholds. Quorum sensing calculates local density metrics.

## Key Classes

### `SwarmEngine`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `num_agents: int` | `None` | Create agent population with default FlockingParams |
| `step` | none | `SwarmState` | Advance one simulation step; compute centroid, average velocity, and coherence |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `SwarmAgent` | `id, position: np.ndarray, velocity: np.ndarray, state, integrity` | A single 3D agent with health status |
| `FlockingParams` | `separation_weight, alignment_weight, cohesion_weight, max_speed, max_force, perception_radius` | Reynolds flocking parameters |
| `SwarmState` | `agents, centroid, avg_velocity, coherence, timestamp` | Snapshot of entire swarm with coherence metric |
| `EmergentPattern` | `pattern_type, strength, duration, involved_agents` | A detected emergent collective pattern |
| `ConsensusState` | `proposal_id, round, agreed_ratio, status` | State of a consensus voting process |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `update_flock` | `agents: list[SwarmAgent], params: FlockingParams` | `None` | Apply separation/alignment/cohesion forces; modifies agents in-place |
| `reach_consensus` | `agents: list[SwarmAgent], proposal: str, threshold: float` | `bool` | Check if agents in "positive" state exceed threshold ratio |
| `quorum_sensing` | `agents: list[SwarmAgent], radius: float` | `float` | Calculate average local neighbor density within given radius |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: `numpy` (3D vector math, distance calculations, array operations)

## Constraints

- Neighbor search is O(N^2) per step (no spatial indexing); scales poorly above ~1000 agents.
- Consensus voting uses simple state string matching (`state == "positive"` counts as yes).
- Coherence is computed as the norm of the mean normalized velocity vector (0 = disordered, 1 = aligned).
- Force limiting caps acceleration at `max_force`; speed limiting caps velocity at `max_speed`.
- `SwarmAgent.position` and `velocity` accept lists and auto-convert to numpy arrays.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `update_flock` returns immediately for empty agent lists.
- `reach_consensus` returns `False` for empty agent lists (ratio defaults to 0.0).
- `quorum_sensing` returns 0.0 for empty agent lists.
- Division-by-zero protection via `1e-6` epsilon in velocity normalization.
