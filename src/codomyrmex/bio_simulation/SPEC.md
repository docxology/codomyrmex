# Bio-Simulation — Specification

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

High-fidelity biological simulation engine for ant colony modeling, emergent behavior study, and population genomics.

## Functional Requirements

### Colony Simulation

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Colony(population)` | `Colony(population: int) → Colony` | Create a colony with N agents |
| `colony.step(hours)` | `step(hours: int) → None` | Advance simulation by hours |
| `colony.ants` | Property → `list[Ant]` | Access individual agents |

### Agent State Machine

| State | Description | Transitions |
|-------|-------------|-------------|
| `FORAGING` | Searching for food | → RETURNING (found food) |
| `RETURNING` | Carrying food to nest | → RESTING (delivered) |
| `RESTING` | Energy recovery | → FORAGING (energy restored) |

### Genomics

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Genome.random()` | `classmethod → Genome` | Generate random genome |
| `Population(genomes)` | `Population(genomes: list[Genome]) → Population` | Create population |
| `population.trait_distribution()` | `→ dict[str, float]` | Compute trait frequencies |

## Non-Functional Requirements

- **Performance**: Colony.step for 1000 agents < 100ms
- **Determinism**: Identical seed → identical results (for reproducible experiments)
- **Memory**: Colony memory < 100MB for populations up to 100,000

## Error Conditions

| Error | Trigger | Resolution |
|-------|---------|------------|
| `SimulationError` | Invalid colony parameters (e.g., `population < 0`, negative hours) | Validate all parameters are positive integers before constructing `Colony` or calling `step()` |
| `ConvergenceError` | Simulation does not reach a stable state within the configured iteration limit | Increase `max_iterations`, reduce population size, or adjust environmental parameters |
| `MemoryError` | Population size exceeds available memory (typically > 500,000 agents) | Reduce population size or use batch-processing mode with `colony.step_batched()` |
| `ValueError` | Invalid genome data (e.g., trait values outside [0.0, 1.0] range) | Validate genome data before constructing `Genome`; use `Genome.random()` for safe defaults |
| `SeedError` | Non-reproducible results due to external state mutation | Use isolated `Colony(seed=N)` instances; avoid shared mutable state across colonies |
| `StateTransitionError` | Agent attempts invalid state transition (e.g., `RESTING` -> `RETURNING`) | Only valid transitions are enforced by the state machine; check `ant.valid_transitions` before manual override |

## Data Contracts

### Colony Construction Input

```python
# Required parameters
{
    "population": int,       # Number of agents, range [1, 500_000]
    "seed": int | None,      # Random seed for reproducibility; None = random
    "environment": dict,     # Optional environment config
}

# Environment schema
{
    "width": int,            # Grid width in cells, default 100
    "height": int,           # Grid height in cells, default 100
    "food_sources": int,     # Number of food deposits, default 10
    "pheromone_decay": float # Decay rate per tick, range [0.0, 1.0], default 0.05
}
```

### Colony Step Output

```python
# colony.step(hours) mutates colony in-place, returns step summary
{
    "ticks_elapsed": int,        # Number of simulation ticks processed
    "food_collected": int,       # Total food units gathered this step
    "deaths": int,               # Agents that died this step
    "births": int,               # New agents spawned this step
    "population": int,           # Current living population count
    "state_distribution": {      # Counts per state
        "FORAGING": int,
        "RETURNING": int,
        "RESTING": int,
    }
}
```

### Ant Agent Schema

```python
# Individual ant state (colony.ants[i])
{
    "id": int,                   # Unique agent identifier
    "state": str,                # Current state: FORAGING | RETURNING | RESTING
    "position": tuple[int, int], # (x, y) grid coordinates
    "energy": float,             # Current energy level [0.0, 1.0]
    "carrying": bool,            # Whether carrying food
    "genome": Genome,            # Genetic profile
    "age_ticks": int,            # Ticks since spawning
}
```

### Genome and Population Schema

```python
# Genome instance
{
    "traits": dict[str, float],   # Trait name -> value [0.0, 1.0]
    # Standard traits: "speed", "strength", "perception", "endurance"
}

# Population trait distribution output
{
    "speed": {"mean": float, "std": float, "min": float, "max": float},
    "strength": {"mean": float, "std": float, "min": float, "max": float},
    "perception": {"mean": float, "std": float, "min": float, "max": float},
    "endurance": {"mean": float, "std": float, "min": float, "max": float},
}
```

## Performance SLOs

| Operation | Target Latency | Conditions | Notes |
|-----------|---------------|------------|-------|
| `Colony(population=1000)` | < 50ms | Default environment | Includes grid allocation and agent initialization |
| `colony.step(hours=1)` | < 100ms | 1,000 agents | Single-threaded; ticks = hours * 60 |
| `colony.step(hours=1)` | < 1s | 10,000 agents | Linear scaling with population |
| `colony.step(hours=1)` | < 10s | 100,000 agents | Consider batch mode for larger populations |
| `Genome.random()` | < 1ms | Single genome | Pseudorandom trait generation |
| `Population(genomes).trait_distribution()` | < 500ms | 100,000 genomes | NumPy-accelerated statistics |
| `colony.ants` property access | < 1ms | Any size | Returns reference, no copy |

**Memory Limits:**
- Colony memory budget: < 100 MB for 100,000 agents
- Per-agent memory: ~1 KB (state, position, genome, history)
- Environment grid: ~40 KB for 100x100 grid

## Design Constraints

1. **Determinism**: Given identical `seed`, `population`, and `environment` parameters, simulation produces bit-identical results across runs. No external randomness sources are used.
2. **Immutable History**: Past simulation states are append-only. Rewinding requires re-running from the seed.
3. **No Silent Failures**: Invalid parameters raise immediately. Out-of-bounds positions raise `SimulationError`. Dead agents are removed from `colony.ants` explicitly.
4. **State Machine Integrity**: Agent state transitions follow the declared FSM. No agent can skip states or enter undefined states.
5. **Thread Safety**: Colony instances are NOT thread-safe. Each thread must operate on its own Colony. Use `colony.clone()` for parallel experiments.
6. **Floating Point Discipline**: Trait values are clamped to [0.0, 1.0]. Energy values are clamped to [0.0, 1.0]. No NaN or Inf propagation.

## PAI Algorithm Integration

| Phase | Usage | Example |
|-------|-------|---------|
| **OBSERVE** | Read colony state to understand current simulation | `colony.ants` to inspect agent distribution and health |
| **THINK** | Analyze trait distributions to identify evolutionary trends | `population.trait_distribution()` for genetic drift analysis |
| **PLAN** | Design experiments by configuring colony parameters | `Colony(population=5000, seed=42, environment={...})` |
| **EXECUTE** | Run simulation steps and collect results | `colony.step(hours=24)` to advance one simulated day |
| **LEARN** | Store simulation outcomes for cross-experiment comparison | Feed step summaries into `agentic_memory` for pattern detection |

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
