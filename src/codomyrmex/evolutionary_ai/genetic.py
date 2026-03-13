"""Core functional genetic logic representation and wrapping.

Adapts the base evolutionary population mechanisms for specifically
tuning prompt templates and configuration dicts via Chromosomes.
"""

from collections.abc import Callable
from typing import Any

from codomyrmex.evolutionary_ai.genome.genome import Genome
from codomyrmex.evolutionary_ai.operators.operators import (
    GaussianMutation,
    SinglePointCrossover,
)
from codomyrmex.evolutionary_ai.population.population import Population
from codomyrmex.evolutionary_ai.selection.selection import TournamentSelection


class Chromosome:
    """Evaluated representation of a candidate solution (e.g., config dict)."""

    def __init__(self, raw_genome: Genome, config: dict[str, Any]) -> None:
        self.genome = raw_genome
        self.config = config
        self.fitness: float | None = raw_genome.fitness


class GeneticAlgorithm:
    """Engine driving crossover, mutate, and selection via standard operators."""

    def __init__(
        self, pop_size: int, gene_length: int, mutation_rate: float = 0.2
    ) -> None:
        self.population = Population.random_genome_population(pop_size, gene_length)
        self.selection = TournamentSelection(tournament_size=3)
        self.crossover = SinglePointCrossover()
        self.mutation = GaussianMutation(sigma=0.1, mutation_rate=mutation_rate)

    def step(self, fitness_callback: Callable[[Genome], float]) -> None:
        """Advance the population by one generation.

        Evaluates the current generation then applies survival mechanics.
        """
        self.population.evaluate(fitness_callback)
        self.population.evolve(
            selection_operator=self.selection,
            crossover_operator=self.crossover,
            mutation_operator=self.mutation,
            elitism=1,
        )
