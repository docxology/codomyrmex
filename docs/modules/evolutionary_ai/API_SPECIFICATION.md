# Evolutionary AI - API Specification

## Introduction

The Evolutionary AI module provides genetic algorithm primitives for evolving AI solutions, including genome representations, genetic operators (crossover, mutation), and population management.

## Endpoints / Functions / Interfaces

### Class: `Genome`

- **Description**: Represents an individual's genetic representation.
- **Constructor**:
    - `genes` (list | np.ndarray): Genetic information.
    - `fitness` (float, optional): Fitness score.
    - `metadata` (dict, optional): Additional metadata.
- **Methods**:

#### `copy() -> Genome`

- **Description**: Create a deep copy of the genome.
- **Returns**:
    - `Genome`: Copied genome.

#### `evaluate(fitness_func: Callable) -> float`

- **Description**: Evaluate fitness using the provided function.
- **Parameters/Arguments**:
    - `fitness_func` (Callable): Function that takes genes and returns fitness.
- **Returns**:
    - `float`: Fitness score.

#### `to_dict() -> dict`

- **Description**: Serialize genome to dictionary.
- **Returns**:
    - `dict`: Serialized genome.

#### `from_dict(data: dict) -> Genome` (classmethod)

- **Description**: Deserialize genome from dictionary.
- **Parameters/Arguments**:
    - `data` (dict): Serialized genome.
- **Returns**:
    - `Genome`: Deserialized genome.

### Class: `Population`

- **Description**: Manages a collection of `Individual` objects and evolves them generation by generation. Attributes: `individuals`, `generation` and `history` (one `GenerationStats` per generation).
- **Constructor**:
    - `individuals` (list[Individual]): Initial individuals.
- **Methods**:

#### `random_genome_population(size: int, genome_length: int, gene_low: float = 0.0, gene_high: float = 1.0) -> Population` (classmethod)

- **Description**: Create a population of random float-vector genomes.
- **Parameters/Arguments**:
    - `size` (int): Number of individuals.
    - `genome_length` (int): Number of genes per genome.
    - `gene_low` (float): Lower bound for random gene values.
    - `gene_high` (float): Upper bound for random gene values.

#### `evaluate(fitness_fn: Callable[[Individual], float]) -> None`

- **Description**: Evaluate fitness for all individuals.
- **Parameters/Arguments**:
    - `fitness_fn` (Callable): Takes an `Individual` and returns its fitness.

#### `evolve(selection_operator: SelectionOperator | None = None, crossover_operator: CrossoverOperator | None = None, mutation_operator: MutationOperator | None = None, elitism: int = 2) -> GenerationStats`

- **Description**: Perform one generation of evolution. Call it in a loop for multiple generations.
- **Parameters/Arguments**:
    - `selection_operator`: Selection operator (default: `TournamentSelection`).
    - `crossover_operator`: Crossover operator (default: `SinglePointCrossover`).
    - `mutation_operator`: Mutation operator (default: `GaussianMutation`).
    - `elitism` (int): Number of top individuals carried over unchanged.
- **Returns**:
    - `GenerationStats`: `generation`, `best_fitness`, `mean_fitness`, `median_fitness`, `worst_fitness`, `std_fitness`, `diversity` and `population_size`.

#### `get_best() -> Individual`

- **Description**: Return the individual with the highest fitness (`get_worst()` returns the lowest).

#### `is_converged(threshold: float = 1e-06, window: int = 5) -> bool`

- **Description**: True when the best fitness has not improved by more than `threshold` over the last `window` generations. `mean_fitness()` and `to_dict()` summarize the current population.

### Function: `crossover()`

- **Description**: Perform crossover between two parent genomes.
- **Parameters/Arguments**:
    - `parent1` (Genome): First parent.
    - `parent2` (Genome): Second parent.
    - `method` (str, optional): Crossover method ("single_point", "two_point", "uniform"). Default: "single_point".
    - `rate` (float, optional): Crossover rate (0-1). Default: 0.8.
- **Returns**:
    - `tuple[Genome, Genome]`: Two offspring genomes.

### Function: `mutate()`

- **Description**: Apply mutation to a genome.
- **Parameters/Arguments**:
    - `genome` (Genome): Genome to mutate.
    - `method` (str, optional): Mutation method ("gaussian", "uniform", "bit_flip"). Default: "gaussian".
    - `rate` (float, optional): Mutation rate (0-1). Default: 0.1.
    - `strength` (float, optional): Mutation strength. Default: 0.5.
- **Returns**:
    - `Genome`: Mutated genome.

### Function: `tournament_selection()`

- **Description**: Select genomes using tournament selection.
- **Parameters/Arguments**:
    - `population` (Population): Population to select from.
    - `tournament_size` (int, optional): Size of each tournament. Default: 3.
    - `n` (int, optional): Number of genomes to select. Default: 2.
- **Returns**:
    - `list[Genome]`: Selected genomes.

## Data Models

### Model: `EvolutionResult`
- `generations` (int): Number of generations evolved.
- `best_fitness` (float): Best fitness achieved.
- `best_genome` (Genome): Best genome found.
- `fitness_history` (list[float]): Best fitness per generation.
- `diversity_history` (list[float]): Population diversity per generation.

### Model: `PopulationStats`
- `size` (int): Population size.
- `mean_fitness` (float): Mean fitness.
- `std_fitness` (float): Standard deviation of fitness.
- `min_fitness` (float): Minimum fitness.
- `max_fitness` (float): Maximum fitness.
- `diversity` (float): Population diversity measure.

## Authentication & Authorization

N/A - This module operates locally.

## Rate Limiting

N/A - Computation is local and not rate-limited.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
