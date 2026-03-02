# Genetic Operators -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Dual-track operator implementations: ABC hierarchies with factory functions (`__init__.py`) and standalone functions (`operators.py`).

## Architecture

```
operators/
├── __init__.py     # Enums, Individual, 3 ABC hierarchies, 12 implementations, 3 factories
└── operators.py    # 9 standalone operator functions using concrete Genome
```

## ABC-Based Operators (`__init__.py`)

### Mutation Operators

| Class | Parameters | Behavior |
|-------|-----------|----------|
| `BitFlipMutation` | `mutation_rate: float` | Flip each bit with probability `mutation_rate` |
| `SwapMutation` | `num_swaps: int` | Perform `num_swaps` random position swaps |
| `GaussianMutation` | `sigma: float, mutation_rate: float` | Add `N(0, sigma)` noise with probability `mutation_rate` per gene |
| `ScrambleMutation` | `segment_length: int` | Shuffle a random segment of given length |

### Crossover Operators

| Class | Parameters | Behavior |
|-------|-----------|----------|
| `SinglePointCrossover` | None | Split at one random point, swap tails |
| `TwoPointCrossover` | None | Split at two random points, swap middle segment |
| `UniformCrossover` | `swap_prob: float` | Each gene swapped independently with probability `swap_prob` |
| `BlendCrossover` | `alpha: float` | `child = p1 + alpha * (p2 - p1)` per gene |

### Selection Operators

| Class | Parameters | Behavior |
|-------|-----------|----------|
| `TournamentSelection` | `tournament_size: int` | Random subset, pick best by fitness |
| `RouletteSelection` | None | Probability proportional to fitness (fitness must be positive) |
| `RankSelection` | None | Probability proportional to rank position |
| `ElitismSelection` | None | Top-k by fitness descending |

### Factory Functions

```python
create_mutation(MutationType.GAUSSIAN, sigma=0.1, mutation_rate=0.05)
create_crossover(CrossoverType.UNIFORM, swap_prob=0.5)
create_selection(SelectionType.TOURNAMENT, tournament_size=3)
```

## Function-Based Operators (`operators.py`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `crossover` | `(p1: Genome, p2: Genome) -> tuple[Genome, Genome]` | Single-point crossover |
| `two_point_crossover` | `(p1, p2) -> tuple[Genome, Genome]` | Two-point crossover |
| `uniform_crossover` | `(p1, p2, rate=0.5) -> tuple[Genome, Genome]` | Per-gene swap at rate |
| `mutate` | `(genome, rate=0.01, sigma=0.1) -> Genome` | Gaussian mutation |
| `uniform_mutate` | `(genome, rate=0.1, low=0.0, high=1.0) -> Genome` | Uniform random replacement |
| `swap_mutate` | `(genome) -> Genome` | Single random position swap |
| `tournament_selection` | `(population, tournament_size=3) -> Genome` | Tournament selection |
| `roulette_selection` | `(population) -> Genome` | Fitness-proportionate selection |
| `rank_selection` | `(population) -> Genome` | Rank-proportionate selection |

## Dependencies

- Python standard library (`random`, `math`)

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
