"""Population representation for genomics in bio simulation.

Provides a Population class that manages selection, crossover, and mutation
across generations of Genome instances.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .genome import Genome


class Population:
    """A population of genomes that evolves over generations.

    Implements a simple genetic algorithm with tournament selection,
    single-point crossover, and Gaussian mutation.

    Attributes:
        size: Number of individuals in the population.
        generation: Current generation number.
    """

    def __init__(
        self,
        genomes: list[Genome] | None = None,
        mutation_rate: float = 0.05,
        tournament_size: int = 3,
    ) -> None:
        """Initialize a random population or from provided genomes.

        Args:
            genomes: Initial list of Genome instances.
            mutation_rate: Per-trait mutation probability.
            tournament_size: Number of candidates in tournament selection.
        """
        from .genome import Genome  # Local import to avoid circular dependency

        if genomes:
            self._individuals = list(genomes)
            self.size = len(self._individuals)
        else:
            self.size = 100
            self._individuals = [Genome.random() for _ in range(self.size)]

        self.mutation_rate = mutation_rate
        self.tournament_size = min(tournament_size, self.size)
        self.generation: int = 0
        self._history: list[dict] = []

    def evolve(self, generations: int) -> list[Genome]:
        """Run the genetic algorithm for a number of generations.

        Args:
            generations: How many generations to simulate.

        Returns:
            The final population sorted by fitness (best first).
        """
        for _ in range(generations):
            self.generation += 1
            parents = self.select_parents(self.size)
            offspring: list[Genome] = []

            for i in range(0, len(parents) - 1, 2):
                child1, child2 = parents[i].crossover(parents[i + 1])
                offspring.append(child1.mutate(self.mutation_rate))
                offspring.append(child2.mutate(self.mutation_rate))

            # If odd number, carry forward the last parent mutated
            if len(parents) % 2 == 1:
                offspring.append(parents[-1].mutate(self.mutation_rate))

            # Elitism: keep the best individual from previous generation
            best_prev = self.get_best()
            self._individuals = offspring[: self.size]
            worst_idx = min(
                range(len(self._individuals)),
                key=lambda i: self._individuals[i].fitness_score(),
            )
            self._individuals[worst_idx] = best_prev

            self._history.append(
                {
                    "generation": self.generation,
                    "best_fitness": self.get_best().fitness_score(),
                    "avg_fitness": self.average_fitness(),
                }
            )

        return sorted(self._individuals, key=lambda g: g.fitness_score(), reverse=True)

    def select_parents(self, count: int) -> list[Genome]:
        """Select parents via tournament selection.

        Args:
            count: Number of parents to select.

        Returns:
            List of selected Genome instances.
        """
        selected: list[Genome] = []
        for _ in range(count):
            tournament = random.sample(self._individuals, self.tournament_size)
            winner = max(tournament, key=lambda g: g.fitness_score())
            selected.append(winner)
        return selected

    def trait_distribution(self) -> dict[str, dict[str, float]]:
        """Compute trait frequencies and statistics.

        Returns:
            Dictionary with trait stats (mean, std, min, max).
        """
        stats = {}
        all_traits = set()
        for g in self._individuals:
            all_traits.update(g.traits.keys())

        for trait in all_traits:
            values = [g.traits.get(trait, 0.0) for g in self._individuals]
            if not values:
                continue

            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            std = variance ** 0.5

            stats[trait] = {
                "mean": round(mean, 4),
                "std": round(std, 4),
                "min": round(min(values), 4),
                "max": round(max(values), 4),
            }
        return stats

    def get_best(self) -> Genome:
        """Return the genome with the highest fitness score."""
        return max(self._individuals, key=lambda g: g.fitness_score())

    def average_fitness(self) -> float:
        """Return the mean fitness across all individuals."""
        if not self._individuals:
            return 0.0
        return sum(g.fitness_score() for g in self._individuals) / len(self._individuals)

    @property
    def individuals(self) -> list[Genome]:
        """Read-only access to current individuals."""
        return list(self._individuals)

    @property
    def history(self) -> list[dict]:
        """Evolutionary history (best/avg fitness per generation)."""
        return list(self._history)
