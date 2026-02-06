"""Population management and evolution cycle."""

import logging
from collections.abc import Callable

from .genome import Genome
from .operators import crossover, mutate, tournament_selection

logger = logging.getLogger(__name__)

class Population:
    """Manages a collection of genomes and their evolution."""

    def __init__(self, size: int, genome_length: int):
        self.individuals = [Genome.random(genome_length) for _ in range(size)]
        self.generation = 0

    def evaluate(self, fitness_fn: Callable[[Genome], float]):
        """Evaluate fitness for all individuals."""
        for ind in self.individuals:
            ind.fitness = fitness_fn(ind)

    def evolve(self, mutation_rate: float = 0.05, elitism: int = 2):
        """Perform one generation of evolution."""
        # Sort by fitness
        self.individuals.sort(key=lambda g: g.fitness if g.fitness is not None else -float('inf'), reverse=True)

        new_population = self.individuals[:elitism]

        while len(new_population) < len(self.individuals):
            p1 = tournament_selection(self.individuals)
            p2 = tournament_selection(self.individuals)

            c1, c2 = crossover(p1, p2)
            new_population.append(mutate(c1, rate=mutation_rate))
            if len(new_population) < len(self.individuals):
                new_population.append(mutate(c2, rate=mutation_rate))

        self.individuals = new_population
        self.generation += 1
        logger.info(f"Generation {self.generation} complete. Best fitness: {self.individuals[0].fitness}")

    def get_best(self) -> Genome:
        """Return the best individual in the current population."""
        return max(self.individuals, key=lambda g: g.fitness if g.fitness is not None else -float('inf'))
