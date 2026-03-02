# Codomyrmex Agents -- evolutionary_ai/fitness

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Fitness evaluation functions for evolutionary algorithms, supporting single-objective, multi-objective (Pareto), and constraint-based fitness scoring.

## Key Components

| Component | Role |
|-----------|------|
| `FitnessResult` | Dataclass: `score: float`, `components: dict[str, float]`, `feasible: bool`, `metadata: dict` |
| `FitnessFunction` (ABC) | Abstract base with `evaluate(genome) -> FitnessResult` and `is_better(a, b) -> bool` |
| `ScalarFitness` | Single-objective evaluator wrapping a `Callable[[list], float]`; supports `maximize` flag |
| `MultiObjectiveFitness` | Multi-objective evaluator with `dominates(a, b)` Pareto comparison; aggregates via weighted sum |
| `ConstrainedFitness` | Wraps another `FitnessFunction` and applies penalty for constraint violations; marks `feasible` flag |

## Operating Contracts

- `ScalarFitness.evaluate()` calls the user-provided function with `genome.to_list()` and returns a `FitnessResult`.
- `ScalarFitness.is_better()` compares scores respecting the `maximize` flag.
- `MultiObjectiveFitness.__init__` takes a list of `(objective_fn, weight)` tuples; `evaluate()` returns weighted sum as the aggregate score with per-objective components.
- `MultiObjectiveFitness.dominates(a, b)` returns True if `a` is better on all objectives and strictly better on at least one.
- `ConstrainedFitness.__init__` takes a base `FitnessFunction` and a list of `(constraint_fn, penalty_weight)` tuples; violations subtract penalty from the base score.

## Integration Points

- `FitnessFunction` implementations are consumed by `evolutionary_ai.population.PopulationManager.evolve_generation()`.
- `FitnessResult.components` dict provides per-objective breakdown for analysis.

## Navigation

- [README](../README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
- Parent: [evolutionary_ai](../README.md)
