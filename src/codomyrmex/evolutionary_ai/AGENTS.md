# Agent Guidelines - Evolutionary AI

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Genetic algorithms, evolutionary optimization, and neuroevolution components.

## Key Classes

- **`Population`** — Manage populations across generations.
- **`Individual[T]`** — Base class for genetic entities.
- **`Genome`** — Specialized float-vector individual.
- **`MutationOperator`** / **`CrossoverOperator`** — Generic operator interfaces.
- **`SelectionOperator`** — Interface for selection strategies.
- **`FitnessFunction`** — Base for scalar, multi-objective, and constrained evaluation.

## Agent Instructions

1. **Define fitness clearly** — The fitness function is the primary driver of evolution. It should reward progress and penalize failure.
2. **Use diverse populations** — Maintain sufficient population size and diversity (checked via `diversity` in `GenerationStats`) to prevent premature convergence.
3. **Save checkpoints** — Evolution takes time; use `to_dict()` to save population state periodically.
4. **Tune hyperparameters** — Mutation rate, crossover rate, and elitism are critical. Start with `mutation_rate=0.1` and `elitism=2`.
5. **Parallelize evaluation** — For complex fitness functions, wrap the evaluation loop in parallel map-reduce.

## Common Patterns

```python
from codomyrmex.evolutionary_ai import (
    Population, Genome, ScalarFitness, 
    TournamentSelection, GaussianMutation, SinglePointCrossover
)

# Define fitness function
def objective(genes):
    return sum(g * g for g in genes)

# Set up operators
sel = TournamentSelection(tournament_size=3)
cross = SinglePointCrossover(crossover_rate=0.8)
mut = GaussianMutation(mutation_rate=0.1, sigma=0.05)

# Initialize population
pop = Population.random_genome_population(size=50, genome_length=20)

# Evolution loop
for gen in range(100):
    pop.evaluate(objective)
    stats = pop.evolve(
        selection_operator=sel,
        crossover_operator=cross,
        mutation_operator=mut,
        elitism=2
    )
    
    if pop.is_converged():
        print(f"Converged at generation {gen}")
        break

best = pop.get_best()
print(f"Best fitness: {best.fitness:.4f}")
```

## Testing Patterns

The `evolutionary_ai` module must be tested with **strictly zero-mock tests**. Verify convergence on simple landscapes (e.g., sphere, rastrigin) to ensure the evolutionary mechanism is functional.

```python
# Verify evolution improves fitness on a simple maximization problem
pop = Population.random_genome_population(size=10, genome_length=5)
def fit(genes): return sum(genes)

pop.evaluate(fit)
initial_best = pop.get_best().fitness

for _ in range(10):
    pop.evaluate(fit)
    pop.evolve(elitism=1)

pop.evaluate(fit)
final_best = pop.get_best().fitness
assert final_best >= initial_best
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Run evolutionary algorithms, configure Population and Operators, manage checkpoints during BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Design fitness functions, population strategies, selection/crossover/mutation operator architecture.

### QATester Agent
**Use Cases**: Unit and integration test execution, fitness convergence validation, population diversity verification.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
