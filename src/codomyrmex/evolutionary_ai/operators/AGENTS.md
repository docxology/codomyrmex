# Codomyrmex Agents -- evolutionary_ai/operators

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Genetic operators for evolutionary algorithms: mutation, crossover, and selection, provided as both ABC hierarchies with concrete implementations and standalone functions.

## Key Components

| Component | Role |
|-----------|------|
| **Enums** | `MutationType` (BIT_FLIP, SWAP, GAUSSIAN, SCRAMBLE), `CrossoverType` (SINGLE_POINT, TWO_POINT, UNIFORM, BLEND), `SelectionType` (TOURNAMENT, ROULETTE, RANK, ELITISM) |
| **Data** | `Individual` dataclass: `genome`, `fitness: float`, `metadata: dict` |
| `MutationOperator` (ABC) | `mutate(genome) -> genome`; 4 implementations: `BitFlipMutation`, `SwapMutation`, `GaussianMutation`, `ScrambleMutation` |
| `CrossoverOperator` (ABC) | `crossover(parent1, parent2) -> tuple[genome, genome]`; 4 implementations: `SinglePointCrossover`, `TwoPointCrossover`, `UniformCrossover`, `BlendCrossover` |
| `SelectionOperator` (ABC) | `select(population, k) -> list[Individual]`; 4 implementations: `TournamentSelection`, `RouletteSelection`, `RankSelection`, `ElitismSelection` |
| Factory functions | `create_mutation(type)`, `create_crossover(type)`, `create_selection(type)` |
| Function-based (`operators.py`) | `crossover()`, `two_point_crossover()`, `uniform_crossover()`, `mutate()`, `uniform_mutate()`, `swap_mutate()`, `tournament_selection()`, `roulette_selection()`, `rank_selection()` |

## Operating Contracts

- ABC-based operators work with the abstract `Genome` from `genome/__init__.py` and `Individual` dataclass.
- Function-based operators in `operators.py` work with the concrete `Genome` from `genome/genome.py`.
- `GaussianMutation.__init__(sigma, mutation_rate)` applies Gaussian noise to each gene with probability `mutation_rate`.
- `BlendCrossover.__init__(alpha)` blends parent genes: `child = p1 + alpha * (p2 - p1)`.
- `TournamentSelection.__init__(tournament_size)` samples `tournament_size` individuals and picks the best by fitness.
- `ElitismSelection.select(population, k)` returns the top `k` individuals sorted by fitness descending.

## Integration Points

- ABC operators are consumed by `population.PopulationManager`.
- Function-based operators are consumed by `population.Population` and the parent `evolutionary_ai.__init__.py`.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [evolutionary_ai](../README.md)
