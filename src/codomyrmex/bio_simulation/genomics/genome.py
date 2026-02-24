"""Genetic representation and evolutionary algorithms.

Provides a Genome class for individual genetic representation and a
Population class that manages selection, crossover, and mutation
across generations.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Genome:
    """Genetic representation for bio simulation.

    A genome is a fixed-length vector of floating-point gene values in
    the range [0, 1].  Fitness is computed as the sum of all gene
    values (higher is better) unless a custom fitness function is
    provided.

    Attributes:
        genes: List of gene values, each in [0.0, 1.0].
        length: Number of genes.
    """

    genes: list[float]
    length: int = field(init=False)

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        self.length = len(self.genes)

    @classmethod
    def random(cls, length: int) -> Genome:
        """Create a genome with random gene values.

        Args:
            length: Number of genes.

        Returns:
            A new Genome with uniform-random gene values in [0, 1].
        """
        return cls(genes=[random.random() for _ in range(length)])

    def mutate(self, rate: float) -> Genome:
        """Return a mutated copy of this genome.

        Each gene has an independent probability *rate* of being replaced
        by a new random value drawn from a Gaussian perturbation (clamped
        to [0, 1]).

        Args:
            rate: Per-gene mutation probability in [0, 1].

        Returns:
            A new Genome with mutations applied.
        """
        new_genes: list[float] = []
        for g in self.genes:
            if random.random() < rate:
                mutated = g + random.gauss(0, 0.1)
                mutated = max(0.0, min(1.0, mutated))
                new_genes.append(mutated)
            else:
                new_genes.append(g)
        return Genome(genes=new_genes)

    def crossover(self, other: Genome) -> tuple[Genome, Genome]:
        """Single-point crossover with another genome.

        A random crossover point splits both parent gene lists, and the
        halves are swapped to produce two offspring.

        Args:
            other: The second parent genome (must have the same length).

        Returns:
            A tuple of two offspring Genomes.

        Raises:
            ValueError: If the two genomes differ in length.
        """
        if self.length != other.length:
            raise ValueError(
                f"Cannot crossover genomes of different lengths "
                f"({self.length} vs {other.length})"
            )

        point = random.randint(1, self.length - 1)
        child1_genes = self.genes[:point] + other.genes[point:]
        child2_genes = other.genes[:point] + self.genes[point:]
        return Genome(genes=child1_genes), Genome(genes=child2_genes)

    def fitness_score(self) -> float:
        """Compute a fitness score for this genome.

        The default fitness function returns the mean gene value,
        yielding a score in [0, 1].  Higher is better.

        Returns:
            Fitness value as a float.
        """
        if self.length == 0:
            return 0.0
        return sum(self.genes) / self.length

    def __repr__(self) -> str:
        """Execute   Repr   operations natively."""
        preview = self.genes[:5]
        suffix = ", ..." if self.length > 5 else ""
        gene_str = ", ".join(f"{g:.3f}" for g in preview)
        return f"Genome(length={self.length}, fitness={self.fitness_score():.4f}, genes=[{gene_str}{suffix}])"


class Population:
    """A population of genomes that evolves over generations.

    Implements a simple genetic algorithm with tournament selection,
    single-point crossover, and Gaussian mutation.

    Attributes:
        size: Number of individuals in the population.
        genome_length: Length of each genome.
        generation: Current generation number.
    """

    def __init__(
        self,
        size: int,
        genome_length: int,
        mutation_rate: float = 0.05,
        tournament_size: int = 3,
    ) -> None:
        """Initialize a random population.

        Args:
            size: Number of genomes in the population.
            genome_length: Number of genes per genome.
            mutation_rate: Per-gene mutation probability.
            tournament_size: Number of candidates in tournament selection.
        """
        self.size = size
        self.genome_length = genome_length
        self.mutation_rate = mutation_rate
        self.tournament_size = min(tournament_size, size)
        self.generation: int = 0

        self._individuals: list[Genome] = [
            Genome.random(genome_length) for _ in range(size)
        ]
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
