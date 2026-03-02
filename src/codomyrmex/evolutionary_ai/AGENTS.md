# Agent Guidelines - Evolutionary AI

**Version**: v1.2.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Genetic algorithms, evolutionary optimization, and neuroevolution components. Provides a complete evolutionary computation framework with generic `Individual[T]` and float-vector `Genome` representations, configurable mutation operators (Gaussian, bit-flip, swap, scramble), crossover operators (single-point, two-point, uniform, blend), selection strategies (tournament, roulette wheel, rank-based), and fitness evaluation (scalar, multi-objective Pareto, constrained). The `Population` class manages the full evolution cycle including evaluation, selection, reproduction, elitism, convergence detection, diversity tracking, and serialization.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports all classes: `Individual`, `Genome`, `GenomeStats`, `Population`, `GenerationStats`, all operators, selection strategies, and fitness functions |
| `genome/genome.py` | `Individual[T]` generic base, `Genome` float-vector subclass with `clone()`, `distance()`, `clamp()`, `stats()`, serialization |
| `population/population.py` | `Population` class with `evaluate()`, `evolve()`, `get_best()`, `is_converged()`, `to_dict()`, and `GenerationStats` dataclass |
| `operators/operators.py` | `MutationOperator` ABC, `BitFlipMutation`, `SwapMutation`, `GaussianMutation`, `ScrambleMutation`; `CrossoverOperator` ABC, `SinglePointCrossover`, `TwoPointCrossover`, `UniformCrossover`, `BlendCrossover` |
| `selection/selection.py` | `SelectionOperator` ABC, `TournamentSelection`, `RouletteWheelSelection`, `RankSelection` |
| `fitness/fitness.py` | `FitnessFunction` ABC, `FitnessResult` dataclass, `ScalarFitness`, `MultiObjectiveFitness` (with `dominates()`), `ConstrainedFitness` |

## Key Classes

- **Individual[T]** -- Generic base class for genetic entities with `genes`, `fitness`, and `metadata`. Supports comparison by fitness for sorting.
- **Genome** -- Float-vector individual (`Individual[list[float]]`) with `random()`, `zeros()`, `clone()`, `distance()`, `clamp()`, `stats()`, and serialization.
- **GenomeStats** -- Summary statistics dataclass: `mean`, `std`, `min_val`, `max_val`, `length`.
- **Population** -- Manages individuals across generations. Provides `evaluate()`, `evolve()`, `get_best()`, `get_worst()`, `mean_fitness()`, `is_converged()`, and `to_dict()`.
- **GenerationStats** -- Per-generation statistics: `best_fitness`, `mean_fitness`, `median_fitness`, `worst_fitness`, `std_fitness`, `diversity`, `population_size`.
- **MutationOperator[T]** -- Abstract mutation with configurable `mutation_rate`. Implementations: `GaussianMutation`, `BitFlipMutation`, `SwapMutation`, `ScrambleMutation`.
- **CrossoverOperator[T]** -- Abstract crossover with configurable `crossover_rate`. Implementations: `SinglePointCrossover`, `TwoPointCrossover`, `UniformCrossover`, `BlendCrossover`.
- **SelectionOperator[T]** -- Abstract selection. Implementations: `TournamentSelection`, `RouletteWheelSelection`, `RankSelection`.
- **FitnessFunction** -- Abstract base. `ScalarFitness` wraps a simple callable. `MultiObjectiveFitness` supports Pareto dominance. `ConstrainedFitness` adds penalty terms.
- **FitnessResult** -- Evaluation result with `value`, `feasible`, and `metadata`.

## Agent Instructions

1. **Define fitness clearly** -- The fitness function is the primary driver of evolution. It should reward progress and penalize failure.
2. **Use diverse populations** -- Maintain sufficient population size and diversity (checked via `diversity` in `GenerationStats`) to prevent premature convergence.
3. **Save checkpoints** -- Evolution takes time; use `to_dict()` to save population state periodically.
4. **Tune hyperparameters** -- Mutation rate, crossover rate, and elitism are critical. Start with `mutation_rate=0.1` and `elitism=2`.
5. **Parallelize evaluation** -- For complex fitness functions, wrap the evaluation loop in parallel map-reduce.

## Operating Contracts

- `Genome.clone()` returns a deep copy with independent gene lists -- mutating the clone does not affect the original.
- All mutation and crossover operators return **new** `Individual` instances -- they never mutate their inputs.
- `Population` must contain at least one individual -- constructing with an empty list raises `ValueError`.
- `Population.evolve()` maintains constant population size across generations. The output population has exactly the same length as the input.
- `Population.evaluate()` must be called before `evolve()`. Evolving with unevaluated individuals logs a warning and may produce incorrect selection.
- `MutationOperator.mutation_rate` must be in `[0.0, 1.0]` -- invalid values raise `ValueError` at construction.
- `CrossoverOperator.crossover_rate` must be in `[0.0, 1.0]` -- invalid values raise `ValueError` at construction.
- `TournamentSelection.tournament_size` must be >= 1.
- `RankSelection.selection_pressure` must be in `[1.0, 2.0]`.
- `Genome.distance()` raises `ValueError` if genome lengths differ.
- `MultiObjectiveFitness` requires `maximize` list length to match the number of objectives.
- **DO NOT** modify `Individual.genes` in-place after the individual has been added to a population -- use `Genome.clone()` first.
- **DO NOT** assume `Individual.fitness` is set before calling `Population.evaluate()` -- it defaults to `None`.

## Common Patterns

### Basic Evolution Loop

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

### Constrained Optimization

```python
from codomyrmex.evolutionary_ai import (
    Population, ScalarFitness, ConstrainedFitness
)

base = ScalarFitness(lambda genes: sum(genes), maximize=True)
constraints = [
    lambda genes: max(0, sum(genes) - 10.0),  # sum <= 10
    lambda genes: max(0, -min(genes)),          # all genes >= 0
]
fitness = ConstrainedFitness(base, constraints, penalty_weight=1000.0)

pop = Population.random_genome_population(size=30, genome_length=5)
pop.evaluate(lambda ind: fitness.evaluate(ind).value)
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
| **Researcher** | Read-only | Population analysis, fitness landscape study | SAFE |

### Engineer Agent
**Use Cases**: Run evolutionary algorithms, configure Population and Operators, manage checkpoints during BUILD/EXECUTE phases.

### Architect Agent
**Use Cases**: Design fitness functions, population strategies, selection/crossover/mutation operator architecture.

### QATester Agent
**Use Cases**: Unit and integration test execution, fitness convergence validation, population diversity verification.

### Researcher Agent
**Use Cases**: Analyze generation statistics, study fitness landscapes, compare operator performance across runs.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
