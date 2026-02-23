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

- **Description**: Manages a population of genomes.
- **Constructor**:
    - `size` (int): Population size.
    - `genome_factory` (Callable, optional): Factory for creating genomes.
    - `genomes` (list[Genome], optional): Initial genomes.
- **Methods**:

#### `initialize(genome_factory: Callable) -> None`

- **Description**: Initialize population with random genomes.
- **Parameters/Arguments**:
    - `genome_factory` (Callable): Factory that creates random genomes.

#### `evaluate(fitness_func: Callable) -> None`

- **Description**: Evaluate fitness for all genomes.
- **Parameters/Arguments**:
    - `fitness_func` (Callable): Fitness evaluation function.

#### `evolve(generations: int, operators: dict) -> EvolutionResult`

- **Description**: Evolve the population for multiple generations.
- **Parameters/Arguments**:
    - `generations` (int): Number of generations.
    - `operators` (dict): Genetic operators configuration.
- **Returns**:
    - `EvolutionResult`: Evolution statistics.

#### `get_best(n: int = 1) -> list[Genome]`

- **Description**: Get the best n genomes by fitness.
- **Parameters/Arguments**:
    - `n` (int): Number of genomes to return.
- **Returns**:
    - `list[Genome]`: Best genomes.

#### `get_statistics() -> PopulationStats`

- **Description**: Get population statistics.
- **Returns**:
    - `PopulationStats`: Statistics (mean, std, min, max fitness).

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
