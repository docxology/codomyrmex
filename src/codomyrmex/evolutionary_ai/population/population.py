"""Population management and evolution cycle.

Provides a ``Population`` class that manages a collection of individuals,
tracks generational statistics, detects convergence, and supports
configurable selection/crossover/mutation strategies.
"""

from __future__ import annotations

import random
import statistics
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from codomyrmex.evolutionary_ai.genome.genome import Genome, Individual
from codomyrmex.evolutionary_ai.operators.operators import (
    CrossoverOperator,
    GaussianMutation,
    MutationOperator,
    SinglePointCrossover,
)
from codomyrmex.evolutionary_ai.selection.selection import (
    SelectionOperator,
    TournamentSelection,
)
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class GenerationStats:
    """Statistics for a single generation."""

    generation: int
    best_fitness: float
    mean_fitness: float
    median_fitness: float
    worst_fitness: float
    std_fitness: float
    diversity: float  # mean pairwise distance (sampled)
    population_size: int


class Population:
    """Manages a collection of individuals and their evolution.

    Attributes:
        individuals: Current list of individuals.
        generation: Current generation number.
        history: List of per-generation statistics.
    """

    def __init__(
        self,
        individuals: list[Individual[Any]],
    ) -> None:
        """Initialize a population with a given set of individuals.

        Args:
            individuals: List of individuals to manage.
        """
        if not individuals:
            raise ValueError("Population must contain at least one individual.")
        self.individuals = individuals
        self.generation: int = 0
        self.history: list[GenerationStats] = []

    @classmethod
    def random_genome_population(
        cls,
        size: int,
        genome_length: int,
        gene_low: float = 0.0,
        gene_high: float = 1.0,
    ) -> Population:
        """Create a population of random float-vector genomes.

        Args:
            size: Number of individuals.
            genome_length: Number of genes per genome.
            gene_low: Lower bound for random gene initialization.
            gene_high: Upper bound for random gene initialization.
        """
        individuals = [
            Genome.random(genome_length, low=gene_low, high=gene_high)
            for _ in range(size)
        ]
        return cls(individuals)

    # ── Evaluation ──────────────────────────────────────────────────

    def evaluate(self, fitness_fn: Callable[[Individual[Any]], float]) -> None:
        """Evaluate fitness for all individuals in the population.

        Args:
            fitness_fn: Callable that takes an Individual and returns a float fitness.
        """
        for ind in self.individuals:
            ind.fitness = fitness_fn(ind)

    # ── Evolution ───────────────────────────────────────────────────

    def evolve(
        self,
        selection_operator: SelectionOperator[Any] | None = None,
        crossover_operator: CrossoverOperator[Any] | None = None,
        mutation_operator: MutationOperator[Any] | None = None,
        elitism: int = 2,
    ) -> GenerationStats:
        """Perform one generation of evolution.

        Args:
            selection_operator: Custom selection operator (default: TournamentSelection).
            crossover_operator: Custom crossover operator (default: SinglePointCrossover).
            mutation_operator: Custom mutation operator (default: GaussianMutation).
            elitism: Number of top individuals carried over unchanged.

        Returns:
            GenerationStats for this generation.
        """
        # Default operators
        sel_op = selection_operator or TournamentSelection()
        cross_op = crossover_operator or SinglePointCrossover()
        mut_op = mutation_operator or GaussianMutation()

        # Check if evaluated
        if any(ind.fitness is None for ind in self.individuals):
            logger.warning("Evolving population with unevaluated individuals.")

        # Sort by fitness (best first)
        self.individuals.sort(reverse=True)

        # Elitism — carry over top individuals
        new_population: list[Individual[Any]] = []
        elite_count = min(elitism, len(self.individuals))
        for i in range(elite_count):
            ind = self.individuals[i]
            # Deepish copy of the individual, preserving class
            new_genes = list(ind.genes) if isinstance(ind.genes, list) else ind.genes
            new_population.append(
                ind.__class__(
                    genes=new_genes,
                    fitness=ind.fitness,
                    metadata=dict(ind.metadata),
                )
            )

        # Fill remaining slots
        target_size = len(self.individuals)
        while len(new_population) < target_size:
            # Select parents
            parents = sel_op.select(self.individuals, 2)
            p1, p2 = parents[0], parents[1]

            # Crossover
            c1, c2 = cross_op.crossover(p1, p2)

            # Mutate and add to new population
            new_population.append(mut_op.mutate(c1))
            if len(new_population) < target_size:
                new_population.append(mut_op.mutate(c2))

        self.individuals = new_population[:target_size]
        self.generation += 1

        stats = self._compute_stats()
        self.history.append(stats)
        logger.info(
            "Generation %d: best=%.4f mean=%.4f diversity=%.4f",
            stats.generation,
            stats.best_fitness,
            stats.mean_fitness,
            stats.diversity,
        )
        return stats

    # ── Queries ──────────────────────────────────────────────────────

    def get_best(self) -> Individual[Any]:
        """Return the individual with the highest fitness."""
        return max(self.individuals)

    def get_worst(self) -> Individual[Any]:
        """Return the individual with the lowest fitness."""
        return min(self.individuals)

    def mean_fitness(self) -> float:
        """Return the mean fitness of the current population."""
        fitnesses = [ind.fitness for ind in self.individuals if ind.fitness is not None]
        return statistics.mean(fitnesses) if fitnesses else 0.0

    def is_converged(self, threshold: float = 1e-6, window: int = 5) -> bool:
        """Check if evolution has converged.

        Returns True if the best fitness has not improved by more than
        ``threshold`` over the last ``window`` generations.
        """
        if len(self.history) < window:
            return False
        recent = self.history[-window:]
        best_range = max(s.best_fitness for s in recent) - min(
            s.best_fitness for s in recent
        )
        return best_range < threshold

    # ── Serialization ───────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Serialize the population state."""
        return {
            "generation": self.generation,
            "individuals": [
                {
                    "genes": ind.genes,
                    "fitness": ind.fitness,
                    "metadata": ind.metadata,
                }
                for ind in self.individuals
            ],
            "history": [
                {
                    "generation": s.generation,
                    "best_fitness": s.best_fitness,
                    "mean_fitness": s.mean_fitness,
                    "median_fitness": s.median_fitness,
                    "worst_fitness": s.worst_fitness,
                    "std_fitness": s.std_fitness,
                    "diversity": s.diversity,
                    "population_size": s.population_size,
                }
                for s in self.history
            ],
        }

    # ── Internal ────────────────────────────────────────────────────

    def _compute_stats(self) -> GenerationStats:
        """Compute statistics for the current generation."""
        fitnesses = [
            ind.fitness for ind in self.individuals if ind.fitness is not None
        ]
        if not fitnesses:
            return GenerationStats(
                generation=self.generation,
                best_fitness=0.0,
                mean_fitness=0.0,
                median_fitness=0.0,
                worst_fitness=0.0,
                std_fitness=0.0,
                diversity=0.0,
                population_size=len(self.individuals),
            )

        diversity = self._sample_diversity(max_pairs=50)

        return GenerationStats(
            generation=self.generation,
            best_fitness=max(fitnesses),
            mean_fitness=statistics.mean(fitnesses),
            median_fitness=statistics.median(fitnesses),
            worst_fitness=min(fitnesses),
            std_fitness=statistics.stdev(fitnesses) if len(fitnesses) > 1 else 0.0,
            diversity=diversity,
            population_size=len(self.individuals),
        )

    def _sample_diversity(self, max_pairs: int = 50) -> float:
        """Estimate population diversity by sampling pairwise distances.

        Only works for Genome individuals (float vectors).
        """
        n = len(self.individuals)
        if n < 2:
            return 0.0

        # Check if we can compute distance — check first few
        can_dist = True
        for i in range(min(n, 5)):
            if not isinstance(self.individuals[i], Genome):
                can_dist = False
                break
        
        if not can_dist:
            return 0.0

        distances: list[float] = []
        pairs_to_check = min(max_pairs, n * (n - 1) // 2)
        attempts = 0
        while len(distances) < pairs_to_check and attempts < pairs_to_check * 3:
            i, j = random.sample(range(n), 2)
            try:
                ind1, ind2 = self.individuals[i], self.individuals[j]
                if isinstance(ind1, Genome) and isinstance(ind2, Genome):
                    distances.append(ind1.distance(ind2))
            except (ValueError, AttributeError) as e:
                logger.debug("Distance calculation failed: %s", e)
                pass
            attempts += 1

        return sum(distances) / len(distances) if distances else 0.0
