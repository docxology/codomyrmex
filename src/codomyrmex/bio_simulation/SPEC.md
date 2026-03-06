# Bio-Simulation — Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Purpose

High-fidelity biological simulation engine for ant colony modeling, emergent behavior study, and population genomics.

## Functional Requirements

### Colony Simulation

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Colony(population)` | `Colony(population: int, seed: int | None, environment: dict | None) → Colony` | Create a colony with N agents |
| `colony.step(hours)` | `step(hours: int) → dict` | Advance simulation by hours, returns step summary |
| `colony.ants` | Property → `list[Ant]` | Access living agents |
| `colony.stats()` | `stats() → dict` | Return current simulation statistics |

### Agent State Machine

| State | Description | Transitions |
|-------|-------------|-------------|
| `FORAGING` | Searching for food | → RETURNING (found food) |
| `RETURNING` | Carrying food to nest | → RESTING (delivered) |
| `RESTING` | Energy recovery | → FORAGING (energy restored) |
| `IDLE` | Waiting state | → FORAGING (randomly) |

### Genomics

| Interface | Signature | Description |
|-----------|-----------|-------------|
| `Genome.random()` | `classmethod → Genome` | Generate random genome with standard traits |
| `Population(genomes)` | `Population(genomes: list[Genome] | None) → Population` | Create population |
| `population.trait_distribution()` | `→ dict[str, dict[str, float]]` | Compute trait frequencies (mean, std, min, max) |
| `population.evolve(gens)` | `evolve(generations: int) → list[Genome]` | Run GA for N generations |

## Standard Traits

- **speed**: Multiplier for movement distance.
- **strength**: Multiplier for carrying capacity.
- **perception**: Multiplier for food detection radius.
- **endurance**: Multiplier for energy depletion rate and recovery.

## Error Conditions

- `ValueError`: If population or hours are negative.
- `SimulationError`: For invalid environment configurations.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
