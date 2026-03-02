# Fitness Evaluation -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Fitness evaluation framework providing single-objective, multi-objective, and constrained fitness functions for evolutionary computation.

## Architecture

```
fitness/
└── __init__.py   # FitnessResult, FitnessFunction ABC, ScalarFitness, MultiObjectiveFitness, ConstrainedFitness
```

## Key Classes

### FitnessResult

| Field | Type | Description |
|-------|------|-------------|
| `score` | `float` | Aggregate fitness score |
| `components` | `dict[str, float]` | Per-objective or per-component scores |
| `feasible` | `bool` | Whether all constraints are satisfied |
| `metadata` | `dict[str, Any]` | Arbitrary evaluation metadata |

### FitnessFunction (ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `evaluate` | `(genome) -> FitnessResult` | Compute fitness for a genome |
| `is_better` | `(a: FitnessResult, b: FitnessResult) -> bool` | Compare two results |

### ScalarFitness

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(func: Callable[[list], float], maximize: bool = True)` | Wrap a scalar function |
| `evaluate` | `(genome) -> FitnessResult` | Call func on `genome.to_list()` |
| `is_better` | `(a, b) -> bool` | Compare respecting `maximize` flag |

### MultiObjectiveFitness

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(objectives: list[tuple[Callable, float]])` | List of (objective_fn, weight) |
| `evaluate` | `(genome) -> FitnessResult` | Weighted sum of objectives; components dict has per-objective scores |
| `dominates` | `(a: FitnessResult, b: FitnessResult) -> bool` | Pareto dominance check |

### ConstrainedFitness

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(base: FitnessFunction, constraints: list[tuple[Callable, float]])` | Wrap base with penalty constraints |
| `evaluate` | `(genome) -> FitnessResult` | Base score minus penalty; `feasible=True` when no violations |

## Dependencies

- No external dependencies; uses Python standard library only.

## Constraints

- All fitness functions expect genomes implementing `to_list() -> list`.
- `MultiObjectiveFitness.dominates()` compares the `components` dict values; both results must have the same keys.

## Navigation

- [README](../README.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
