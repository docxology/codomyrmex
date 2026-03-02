# Agent Guidelines - Evolutionary AI

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Genetic algorithms, neural evolution, and evolutionary optimization.

## Key Classes

- **GeneticAlgorithm** — Classic GA with selection, crossover, mutation
- **NEATEvolver** — NeuroEvolution of Augmenting Topologies
- **PopulationManager** — Manage populations across generations
- **FitnessEvaluator** — Parallel fitness evaluation

## Agent Instructions

1. **Define fitness clearly** — Fitness function drives evolution
2. **Use diverse populations** — Prevent premature convergence
3. **Save checkpoints** — Evolution takes time, save progress
4. **Tune hyperparameters** — Mutation rate, population size matter
5. **Parallelize evaluation** — Use `FitnessEvaluator` for speed

## Common Patterns

```python
from codomyrmex.evolutionary_ai import (
    GeneticAlgorithm, PopulationManager, FitnessEvaluator
)

# Define fitness function
def fitness(individual):
    return evaluate_performance(individual)

# Set up GA
ga = GeneticAlgorithm(
    population_size=100,
    mutation_rate=0.1,
    crossover_rate=0.7
)

# Evolve
for generation in range(100):
    population = ga.evolve(fitness)
    best = ga.get_best()
    print(f"Gen {generation}: fitness={best.fitness:.4f}")

# Parallel evaluation
evaluator = FitnessEvaluator(workers=8)
evaluated = evaluator.evaluate_batch(population, fitness)
```

## Testing Patterns

```python
# Verify evolution improves fitness
ga = GeneticAlgorithm(population_size=10)
initial_fitness = ga.get_best().fitness
for _ in range(10):
    ga.evolve(lambda x: sum(x.genes))
assert ga.get_best().fitness >= initial_fitness
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Run evolutionary algorithms, configure GeneticAlgorithm and NEATEvolver, manage populations during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Design fitness functions, population strategies, selection/crossover/mutation operator architecture

### QATester Agent
**Use Cases**: Unit and integration test execution, fitness convergence validation, population diversity verification

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
