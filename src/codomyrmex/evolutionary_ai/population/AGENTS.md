# Codomyrmex Agents -- evolutionary_ai/population

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Population management for evolutionary algorithms, including initialization, generation evolution, diversity tracking, and convergence detection.

## Key Components

| Component | Role |
|-----------|------|
| `DiversityMetrics` | Dataclass: `mean_distance`, `min_distance`, `max_distance`, `unique_ratio` |
| `PopulationManager` (Generic[T]) | ABC-operator-based population manager: `initialize()`, `evolve_generation()`, `get_best()`, `get_diversity_metrics()` |
| `GenerationStats` | Dataclass: `generation`, `best_fitness`, `mean_fitness`, `worst_fitness`, `diversity` |
| `Population` | Function-operator-based population: `evaluate()`, `evolve()`, `get_best()`, `get_worst()`, `mean_fitness()`, `is_converged()` |

## Operating Contracts

- `PopulationManager.__init__` takes `mutation_op`, `crossover_op`, `selection_op` (ABC operators), `population_size`, and `elite_count`.
- `PopulationManager.initialize(factory)` creates the initial population using a callable factory function.
- `PopulationManager.evolve_generation(fitness_fn)` evaluates fitness, selects parents, applies crossover and mutation, preserves elites.
- `Population.__init__` takes a list of `Genome` objects (from `genome/genome.py`).
- `Population.evolve(fitness_fn, ...)` runs one generation with tournament selection, crossover, and mutation using function-based operators.
- `Population.is_converged(threshold)` returns True when standard deviation of fitness values falls below threshold.
- Both classes track generation history for analysis.

## Integration Points

- `PopulationManager` consumes ABC operators from `operators/__init__.py` and fitness functions from `fitness/__init__.py`.
- `Population` consumes function-based operators from `operators/operators.py`.
- `Population` is re-exported by `bio_simulation/genomics/__init__.py`.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [evolutionary_ai](../README.md)
