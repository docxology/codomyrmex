# Evolutionary AI Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `evolutionary_ai` module provides a comprehensive genetic algorithm framework for optimization and evolutionary discovery. It features a flexible architecture with pluggable operators for selection, crossover, and mutation, supporting both standard float-vector genomes and arbitrary genetic representations.

## Key Components

### 1. Representation (`genome` submodule)

- **`Individual[T]`** -- Base class for any evolved entity, wrapping genes of type `T` and tracking `fitness`.
- **`Genome`** -- Specialization of `Individual[list[float]]` for real-valued optimization. Includes distance metrics (`distance`), statistics (`stats`), and clamping.

### 2. Population Management (`population` submodule)

- **`Population`** -- Manages a collection of individuals.
- **`evolve()`** -- Performs generational transition using selection, crossover, and mutation operators. Supports elitism.
- **`evaluate()`** -- Applies a fitness function to all individuals.
- **`is_converged()`** -- Detects evolutionary stagnation.

### 3. Operators (`operators` submodule)

- **Mutation**: `BitFlipMutation`, `SwapMutation`, `GaussianMutation`, `ScrambleMutation`.
- **Crossover**: `SinglePointCrossover`, `TwoPointCrossover`, `UniformCrossover`, `BlendCrossover`.

### 4. Selection Strategies (`selection` submodule)

- **`TournamentSelection`** -- Selects best from a random subset.
- **`RouletteWheelSelection`** -- Fitness-proportionate selection.
- **`RankSelection`** -- Probability based on rank order.

### 5. Fitness Framework (`fitness` submodule)

- **`ScalarFitness`** -- Standard single-objective evaluation.
- **`MultiObjectiveFitness`** -- Pareto-based multi-objective optimization.
- **`ConstrainedFitness`** -- Applies penalties for constraint violations.

## Installation

```bash
uv add codomyrmex
```

## Quick Start

```python
import random
from codomyrmex.evolutionary_ai import Population, Genome, ScalarFitness

# 1. Define fitness function (maximize sum of genes)
def fitness_fn(genes):
    return sum(genes)

# 2. Create a population of 20 individuals with 10 genes each
pop = Population.random_genome_population(size=20, genome_length=10)

# 3. Evolve for 50 generations
for gen in range(50):
    pop.evaluate(fitness_fn)
    stats = pop.evolve(elitism=2)
    
    if gen % 10 == 0:
        print(f"Gen {gen}: best fitness = {stats.best_fitness:.4f}")

# 4. Get the result
best = pop.get_best()
print(f"Optimal solution: {best.genes}")
```

## Testing

The module uses strictly zero-mock tests to verify evolutionary convergence and operator correctness.

```bash
uv run pytest src/codomyrmex/tests/unit/evolutionary_ai/
```

## Navigation

- [SPEC.md](SPEC.md) - Detailed technical specification
- [AGENTS.md](AGENTS.md) - Integration instructions for AI agents
- [PAI.md](PAI.md) - Project AI Integration details
