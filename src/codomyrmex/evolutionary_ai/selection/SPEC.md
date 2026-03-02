# Selection Methods -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Three concrete selection strategies implementing a common `SelectionOperator` ABC, each with distinct selection pressure characteristics.

## Architecture

```
selection/
└── __init__.py   # SelectionOperator ABC, TournamentSelection, RouletteWheelSelection, RankSelection
```

## Key Classes

### SelectionOperator (ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `select` | `(population: list[Individual], k: int) -> list[Individual]` | Select k individuals from population |

### TournamentSelection

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(tournament_size: int = 3)` | Set tournament sample size |
| `select` | `(population, k) -> list[Individual]` | k rounds of tournament selection |

### RouletteWheelSelection

| Method | Signature | Description |
|--------|-----------|-------------|
| `select` | `(population, k) -> list[Individual]` | Fitness-proportionate cumulative probability selection |

Constraint: all fitness values must be non-negative. If total fitness is zero, falls back to uniform random selection.

### RankSelection

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(selection_pressure: float = 1.5)` | Set pressure; must be in [1.0, 2.0] |
| `select` | `(population, k) -> list[Individual]` | Rank-proportionate selection using linear ranking |

Linear ranking formula: `prob_i = (2 - sp) / n + 2 * rank_i * (sp - 1) / (n * (n - 1))` where `sp` is selection pressure, `n` is population size, and `rank_i` ranges from 0 (worst) to n-1 (best).

## Dependencies

- `evolutionary_ai.operators.Individual` dataclass
- Python standard library (`random`)

## Constraints

- `RankSelection` raises `ValueError` if `selection_pressure` is outside `[1.0, 2.0]`.
- All strategies may return duplicate individuals in the selected list.
- `RouletteWheelSelection` can exhibit bias toward high-fitness individuals; use `RankSelection` for more uniform pressure.

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
