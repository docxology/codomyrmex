# Bio-Simulation — Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

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

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../SPEC.md)
