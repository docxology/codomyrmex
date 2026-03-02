# Population Management -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Dual population management implementations: `PopulationManager` using ABC operators and `Population` using function-based operators.

## Architecture

```
population/
├── __init__.py      # DiversityMetrics, PopulationManager (Generic[T])
└── population.py    # GenerationStats, Population
```

## Key Classes

### PopulationManager (Generic[T])

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(mutation_op, crossover_op, selection_op, population_size=100, elite_count=2)` | Configure with ABC operators |
| `initialize` | `(factory: Callable[[], T]) -> None` | Create initial population via factory |
| `evolve_generation` | `(fitness_fn: FitnessFunction) -> GenerationStats` | Run one generation: evaluate, select, crossover, mutate, preserve elites |
| `get_best` | `(k: int = 1) -> list[Individual[T]]` | Return top k individuals by fitness |
| `get_diversity_metrics` | `() -> DiversityMetrics` | Compute population diversity metrics |

### DiversityMetrics

Fields: `mean_distance: float`, `min_distance: float`, `max_distance: float`, `unique_ratio: float`.

### Population

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(genomes: list[Genome])` | Initialize with list of genomes |
| `evaluate` | `(fitness_fn: Callable[[Genome], float]) -> None` | Evaluate fitness for all genomes |
| `evolve` | `(fitness_fn, mutation_rate=0.01, crossover_rate=0.8, tournament_size=3, elitism=1) -> None` | Run one generation |
| `get_best` | `() -> Genome` | Return genome with highest fitness |
| `get_worst` | `() -> Genome` | Return genome with lowest fitness |
| `mean_fitness` | `() -> float` | Average fitness across population |
| `is_converged` | `(threshold: float = 0.001) -> bool` | True if fitness std dev < threshold |
| `to_dict` | `() -> dict` | Serialize population state |

### GenerationStats

Fields: `generation: int`, `best_fitness: float`, `mean_fitness: float`, `worst_fitness: float`, `diversity: float`.

## Dependencies

- `evolutionary_ai.operators` (both ABC and function-based)
- `evolutionary_ai.fitness` (ABC implementations for `PopulationManager`)
- `evolutionary_ai.genome` (both ABC and concrete)

## Constraints

- `PopulationManager.evolve_generation()` preserves `elite_count` top individuals unchanged into the next generation.
- `Population.evolve()` defaults to tournament selection with `tournament_size=3` and `elitism=1`.
- `Population._sample_diversity()` samples a subset of pairs for efficiency on large populations.

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
