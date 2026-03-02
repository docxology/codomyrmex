# Codomyrmex Agents -- src/codomyrmex/meme/swarm

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Purpose

Models swarm intelligence and collective behavior using Reynolds flocking rules (separation, alignment, cohesion). Agents operate in 3D space with position and velocity vectors. Provides consensus algorithms via state-based voting, quorum sensing for local density detection, and coherence metrics for emergent pattern tracking.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `engine.py` | `SwarmEngine` | Orchestrator: create agents, advance simulation steps, compute state metrics |
| `flocking.py` | `update_flock` | Apply separation/alignment/cohesion forces; modifies agents in-place |
| `consensus.py` | `reach_consensus` | Check if agents in "positive" state exceed threshold ratio |
| `consensus.py` | `quorum_sensing` | Calculate average local neighbor density within given radius |
| `models.py` | `SwarmAgent` | 3D agent with position, velocity, state, and integrity |
| `models.py` | `FlockingParams` | Reynolds parameters: weights, max speed/force, perception radius |
| `models.py` | `SwarmState` | Swarm snapshot: centroid, average velocity, coherence metric |
| `models.py` | `EmergentPattern` | Detected collective pattern with strength and duration |
| `models.py` | `ConsensusState` | Voting process state: proposal, round, agreed ratio, status |

## Operating Contracts

- Neighbor search is O(N^2) per step; scales poorly above ~1000 agents.
- Coherence = norm of mean normalized velocity vector (0 = disordered, 1 = fully aligned).
- Consensus voting uses string matching (`state == "positive"` counts as yes).
- Force limiting caps acceleration at `max_force`; speed limiting caps velocity at `max_speed`.
- Individual agent logic should remain simple for scalability.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `numpy` (3D vector math, distance calculations)
- **Used by**: `meme.rhizome` (swarm agents traverse rhizome network edges), `meme.contagion` (contagion dynamics parameterize swarm panic thresholds)

## Navigation

- **Parent**: [meme](../README.md)
- **Root**: [Root](../../../../README.md)
