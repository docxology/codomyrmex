# Genomics -- Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Genetic algorithm primitives providing individual genome representation and population-level evolutionary simulation with tournament selection, single-point crossover, Gaussian mutation, and single-individual elitism.

## Architecture

```
bio_simulation/genomics/
├── __init__.py    # Exports Genome, Population
└── genome.py      # Genome dataclass and Population class
```

## Key Classes

### Genome (genome.py)

| Method | Signature | Description |
|--------|-----------|-------------|
| `random` | `(cls, length: int) -> Genome` | Class method; create genome with uniform-random genes in [0, 1] |
| `mutate` | `(rate: float) -> Genome` | Return mutated copy; per-gene probability `rate` of Gaussian perturbation (sigma=0.1, clamped [0, 1]) |
| `crossover` | `(other: Genome) -> tuple[Genome, Genome]` | Single-point crossover producing two offspring; raises `ValueError` if lengths differ |
| `fitness_score` | `() -> float` | Mean gene value in [0, 1]; returns 0.0 for empty genomes |

**Fields**: `genes: list[float]`, `length: int` (computed in `__post_init__`)

### Population (genome.py)

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(size: int, genome_length: int, mutation_rate: float = 0.05, tournament_size: int = 3)` | Initialize random population |
| `evolve` | `(generations: int) -> list[Genome]` | Run GA for N generations; returns final population sorted by fitness (best first) |
| `select_parents` | `(count: int) -> list[Genome]` | Tournament selection of `count` parents |
| `get_best` | `() -> Genome` | Return the genome with highest fitness |
| `average_fitness` | `() -> float` | Mean fitness across all individuals |

**Properties**: `individuals: list[Genome]` (read-only copy), `history: list[dict]` (per-generation best/avg fitness records)

**Evolutionary loop** (inside `evolve`):
1. Select `size` parents via tournament selection.
2. Pair parents and apply crossover to produce offspring.
3. Mutate all offspring at `mutation_rate`.
4. Elitism: replace worst offspring with best individual from previous generation.
5. Record generation stats to `_history`.

## Dependencies

- Python `random`, `dataclasses` (standard library only)

## Constraints

- Crossover requires both genomes to have identical `length`; mismatched lengths raise `ValueError`.
- `tournament_size` is capped at `size` (population size).
- Odd population sizes carry the last unpaired parent forward as a mutated individual.
- Gene values are always clamped to [0.0, 1.0] after mutation.

## Error Handling

| Error | When |
|-------|------|
| `ValueError` | Crossover between genomes of different lengths |

## Navigation

- **Parent**: [bio_simulation/SPEC.md](../SPEC.md)
- **Siblings**: [AGENTS.md](AGENTS.md), [README.md](README.md), [PAI.md](PAI.md)
