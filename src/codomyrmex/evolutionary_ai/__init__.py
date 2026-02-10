"""Evolutionary AI module for Codomyrmex.

Provides genetic algorithm components:
- Genome representation
- Population management
- Selection operators
- Crossover operators
- Mutation operators
"""

import random
from typing import Any, Dict, List, Optional, Tuple
from collections.abc import Callable

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Submodule exports
from . import fitness, operators, selection

# Import operators and selection types
from .operators import (
    BitFlipMutation,
    BlendCrossover,
    CrossoverOperator,
    CrossoverType,
    ElitismSelection,
    GaussianMutation,
    Individual,
    MutationOperator,
    MutationType,
    RankSelection,
    RouletteSelection,
    ScrambleMutation,
    SelectionOperator,
    SelectionType,
    SinglePointCrossover,
    SwapMutation,
    TournamentSelection,
    TwoPointCrossover,
    UniformCrossover,
    create_crossover,
    create_mutation,
    create_selection,
)

# Try optional submodules
try:
    from . import genome
except ImportError:
    genome = None

try:
    from . import population
except ImportError:
    population = None


class Genome:
    """
    A genome representing an individual's genetic material.

    Provides a simple interface for working with genetic data
    in evolutionary algorithms.
    """

    def __init__(self, genes: list[float] = None, length: int = 10):
        """
        Initialize a genome.

        Args:
            genes: List of gene values (floats 0-1)
            length: Length of genome if genes not provided
        """
        if genes is not None:
            self.genes = list(genes)
        else:
            self.genes = [random.random() for _ in range(length)]
        self.fitness: float | None = None

    @classmethod
    def random(cls, length: int = 10) -> 'Genome':
        """Create a random genome."""
        return cls(length=length)

    def __len__(self) -> int:
        return len(self.genes)

    def __getitem__(self, key):
        return self.genes[key]

    def __iter__(self):
        return iter(self.genes)

    def copy(self) -> 'Genome':
        """Create a copy of this genome."""
        new = Genome(genes=self.genes.copy())
        new.fitness = self.fitness
        return new


class Population:
    """
    A population of individuals for evolutionary algorithms.

    Manages a collection of genomes and provides methods for
    evaluation, selection, and evolution.
    """

    def __init__(self, size: int = 20, genome_length: int = 10):
        """
        Initialize a population.

        Args:
            size: Number of individuals in the population
            genome_length: Length of each genome
        """
        self.individuals: list[Genome] = [
            Genome(length=genome_length) for _ in range(size)
        ]
        self.generation = 0

    def evaluate(self, fitness_fn: Callable[[Genome], float]) -> None:
        """
        Evaluate all individuals in the population.

        Args:
            fitness_fn: Function that takes a Genome and returns fitness score
        """
        for individual in self.individuals:
            individual.fitness = fitness_fn(individual)

    def get_best(self) -> Genome:
        """Get the best individual in the population."""
        return max(self.individuals, key=lambda g: g.fitness or float('-inf'))

    def get_worst(self) -> Genome:
        """Get the worst individual in the population."""
        return min(self.individuals, key=lambda g: g.fitness or float('inf'))

    def evolve(
        self,
        mutation_rate: float = 0.05,
        crossover_rate: float = 0.8,
        elitism: int = 2,
    ) -> None:
        """
        Evolve the population by one generation.

        Args:
            mutation_rate: Probability of mutation per gene
            crossover_rate: Probability of crossover
            elitism: Number of best individuals to preserve
        """
        # Sort by fitness
        sorted_pop = sorted(
            self.individuals,
            key=lambda g: g.fitness or float('-inf'),
            reverse=True
        )

        # Keep elite individuals
        new_population = [g.copy() for g in sorted_pop[:elitism]]

        # Fill rest of population
        while len(new_population) < len(self.individuals):
            # Tournament selection
            parent1 = tournament_selection(sorted_pop)
            parent2 = tournament_selection(sorted_pop)

            # Crossover
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            # Mutation
            child1 = mutate(child1, rate=mutation_rate)
            child2 = mutate(child2, rate=mutation_rate)

            new_population.append(child1)
            if len(new_population) < len(self.individuals):
                new_population.append(child2)

        self.individuals = new_population[:len(self.individuals)]
        self.generation += 1


def crossover(parent1: Genome, parent2: Genome) -> tuple[Genome, Genome]:
    """
    Perform single-point crossover between two genomes.

    Args:
        parent1: First parent genome
        parent2: Second parent genome

    Returns:
        Tuple of two child genomes
    """
    length = min(len(parent1), len(parent2))
    if length < 2:
        return parent1.copy(), parent2.copy()

    point = random.randint(1, length - 1)

    child1 = Genome(genes=list(parent1.genes[:point]) + list(parent2.genes[point:]))
    child2 = Genome(genes=list(parent2.genes[:point]) + list(parent1.genes[point:]))

    return child1, child2


def mutate(genome: Genome, rate: float = 0.05) -> Genome:
    """
    Apply mutation to a genome.

    Args:
        genome: The genome to mutate
        rate: Probability of mutation per gene

    Returns:
        A new mutated genome
    """
    new_genes = []
    for gene in genome.genes:
        if random.random() < rate:
            # Gaussian mutation
            new_gene = gene + random.gauss(0, 0.1)
            new_gene = max(0.0, min(1.0, new_gene))  # Clamp to [0, 1]
            new_genes.append(new_gene)
        else:
            new_genes.append(gene)

    return Genome(genes=new_genes)


def tournament_selection(
    population: list[Genome],
    tournament_size: int = 3,
) -> Genome:
    """
    Select an individual using tournament selection.

    Args:
        population: List of genomes to select from
        tournament_size: Number of individuals in tournament

    Returns:
        The winning genome
    """
    tournament = random.sample(population, min(tournament_size, len(population)))
    winner = max(tournament, key=lambda g: g.fitness or float('-inf'))
    return winner.copy()


def cli_commands():
    """Return CLI commands for the evolutionary_ai module."""
    return {
        "algorithms": {
            "help": "List evolutionary algorithms",
            "handler": lambda **kwargs: print(
                "Evolutionary AI Algorithms\n"
                f"  Mutation types: {', '.join(mt.value if hasattr(mt, 'value') else str(mt) for mt in MutationType)}\n"
                f"  Crossover types: {', '.join(ct.value if hasattr(ct, 'value') else str(ct) for ct in CrossoverType)}\n"
                f"  Selection types: {', '.join(st.value if hasattr(st, 'value') else str(st) for st in SelectionType)}\n"
                "  Core: Genome, Population, crossover, mutate, tournament_selection"
            ),
        },
        "evolve": {
            "help": "Run an evolutionary algorithm",
            "handler": lambda **kwargs: print(
                "Evolutionary Run\n"
                "  Use Population(size, genome_length) to create a population.\n"
                "  Call population.evaluate(fitness_fn) then population.evolve().\n"
                "  Factory functions: create_mutation, create_crossover, create_selection"
            ),
        },
    }


__all__ = [
    # CLI integration
    "cli_commands",
    # Submodules
    "operators",
    "selection",
    "fitness",
    # Core classes
    "Genome",
    "Population",
    "Individual",
    # Convenience functions
    "crossover",
    "mutate",
    "tournament_selection",
    # Operator types
    "MutationType",
    "CrossoverType",
    "SelectionType",
    # Mutation operators
    "MutationOperator",
    "BitFlipMutation",
    "SwapMutation",
    "GaussianMutation",
    "ScrambleMutation",
    # Crossover operators
    "CrossoverOperator",
    "SinglePointCrossover",
    "TwoPointCrossover",
    "UniformCrossover",
    "BlendCrossover",
    # Selection operators
    "SelectionOperator",
    "TournamentSelection",
    "RouletteSelection",
    "RankSelection",
    "ElitismSelection",
    # Factory functions
    "create_mutation",
    "create_crossover",
    "create_selection",
]

__version__ = "0.1.0"

