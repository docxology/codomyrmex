# evolutionary_ai

Evolutionary computation and genetic algorithm module.

## Overview

This module provides a framework for evolutionary AI, including genetic algorithms, neuroevolution, and generative design. It enables the optimization of parameters, architectures, and behaviors through simulated evolution.

## Key Features

- **Genetic Operators**: Optimized `crossover`, `mutate`, and `tournament_selection` implementations.
- **Genome Management**: `Genome` objects with automated gene initialization and mutation.
- **Population Control**: Robust `Population` class for managing generations and evolution cycles.
- **Fitness Evaluation**: Abstract interfaces for defining and executes fitness functions.

## Usage

```python
from codomyrmex.evolutionary_ai import Population, GeneticAlgorithm

# Define a simple fitness function
def fitness_fn(genome):
    return sum(genome.genes)

# Initialize population
pop = Population(size=100, genome_length=10)

# Run evolution
ga = GeneticAlgorithm(population=pop, fitness_fn=fitness_fn)
best_genome = ga.evolve(generations=50)

print(f"Best fitness: {best_genome.fitness}")
```

## Navigation Links

- [Functional Specification](SPEC.md)
- [Technical Documentation](AGENTS.md)
