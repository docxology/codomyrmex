# Codomyrmex Agents -- evolutionary_ai/selection

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Selection strategies for evolutionary algorithms, providing abstract and concrete implementations for choosing parents from a population.

## Key Components

| Component | Role |
|-----------|------|
| `SelectionOperator` (ABC) | Abstract base with `select(population: list[Individual], k: int) -> list[Individual]` |
| `TournamentSelection` | Picks best from a random sample of `tournament_size` individuals; repeats `k` times |
| `RouletteWheelSelection` | Fitness-proportionate random selection; fitness values must be non-negative |
| `RankSelection` | Rank-proportionate selection with configurable `selection_pressure` (1.0 to 2.0) |

## Operating Contracts

- `TournamentSelection.__init__(tournament_size: int = 3)` sets the number of individuals sampled per tournament round.
- `RouletteWheelSelection.select()` computes cumulative probability from fitness values; zero total fitness returns random selections.
- `RankSelection.__init__(selection_pressure: float = 1.5)` validates pressure is in `[1.0, 2.0]`; raises `ValueError` otherwise.
- `RankSelection` sorts population by fitness ascending, assigns rank-based probabilities using linear ranking formula: `prob = (2 - sp) / n + 2 * rank * (sp - 1) / (n * (n - 1))`.
- All selection operators return `k` selected `Individual` objects (with possible duplicates).

## Integration Points

- Selection operators are consumed by `population.PopulationManager.evolve_generation()`.
- These operators overlap with the `SelectionOperator` implementations in `operators/__init__.py` (Tournament, Roulette, Rank, Elitism). This module provides an independent hierarchy focused specifically on selection.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [evolutionary_ai](../README.md)
