"""Population management and evolution cycle.

Provides a ``Population`` class that manages a collection of genomes,
tracks generational statistics, detects convergence, and supports
configurable selection/crossover/mutation strategies.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..genome.genome import Genome
from ..operators.operators import (
    _fitness_key,
    crossover,
    mutate,
    tournament_selection,
)

logger = get_logger(__name__)


@dataclass
class GenerationStats:
    """Statistics for a single generation."""

    generation: int
    best_fitness: float
    mean_fitness: float
    worst_fitness: float
    diversity: float  # mean pairwise distance (sampled)
    population_size: int


class Population:
    """Manages a collection of genomes and their evolution.

    Attributes:
        individuals: Current list of genomes.
        generation: Current generation number.
        history: List of per-generation statistics.
    """

    def __init__(
        self,
        size: int,
        genome_length: int,
        gene_low: float = 0.0,
        gene_high: float = 1.0,
    ) -> None:
        """Initialize a random population.

        Args:
            size: Number of individuals.
            genome_length: Number of genes per genome.
            gene_low: Lower bound for random gene initialization.
            gene_high: Upper bound for random gene initialization.
        """
        self.individuals = [
            Genome.random(genome_length, low=gene_low, high=gene_high)
            for _ in range(size)
        ]
        self.generation: int = 0
        self.history: list[GenerationStats] = []

    # ── Evaluation ──────────────────────────────────────────────────

    def evaluate(self, fitness_fn: Callable[[Genome], float]) -> None:
        """Evaluate fitness for all individuals in the population.

        Args:
            fitness_fn: Callable that takes a Genome and returns a float fitness.
        """
        for ind in self.individuals:
            ind.fitness = fitness_fn(ind)

    # ── Evolution ───────────────────────────────────────────────────

    def evolve(
        self,
        mutation_rate: float = 0.05,
        elitism: int = 2,
        selection_fn: Callable[[list[Genome]], Genome] | None = None,
        crossover_fn: Callable[
            [Genome, Genome], tuple[Genome, Genome]
        ] | None = None,
        mutation_fn: Callable[[Genome], Genome] | None = None,
    ) -> GenerationStats:
        """Perform one generation of evolution.

        Args:
            mutation_rate: Per-gene probability of mutation (used by default mutator).
            elitism: Number of top individuals carried over unchanged.
            selection_fn: Custom selection operator (default: tournament_selection).
            crossover_fn: Custom crossover operator (default: single-point crossover).
            mutation_fn: Custom mutation operator (default: Gaussian mutate).

        Returns:
            GenerationStats for this generation.
        """
        select = selection_fn or tournament_selection
        cross = crossover_fn or crossover
        mut = mutation_fn or (lambda g: mutate(g, rate=mutation_rate))

        # Sort by fitness (best first)
        self.individuals.sort(key=_fitness_key, reverse=True)

        # Elitism — carry over top individuals
        new_population = [ind.clone() for ind in self.individuals[:elitism]]

        # Fill remaining slots
        target_size = len(self.individuals)
        while len(new_population) < target_size:
            p1 = select(self.individuals)
            p2 = select(self.individuals)
            c1, c2 = cross(p1, p2)
            new_population.append(mut(c1))
            if len(new_population) < target_size:
                new_population.append(mut(c2))

        self.individuals = new_population
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

    def get_best(self) -> Genome:
        """Return the individual with the highest fitness."""
        return max(self.individuals, key=_fitness_key)

    def get_worst(self) -> Genome:
        """Return the individual with the lowest fitness."""
        return min(self.individuals, key=_fitness_key)

    def mean_fitness(self) -> float:
        """Return the mean fitness of the current population."""
        fitnesses = [g.fitness for g in self.individuals if g.fitness is not None]
        return sum(fitnesses) / len(fitnesses) if fitnesses else 0.0

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
            "individuals": [ind.to_dict() for ind in self.individuals],
            "history": [
                {
                    "generation": s.generation,
                    "best_fitness": s.best_fitness,
                    "mean_fitness": s.mean_fitness,
                    "worst_fitness": s.worst_fitness,
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
            g.fitness for g in self.individuals if g.fitness is not None
        ]
        if not fitnesses:
            return GenerationStats(
                generation=self.generation,
                best_fitness=0.0,
                mean_fitness=0.0,
                worst_fitness=0.0,
                diversity=0.0,
                population_size=len(self.individuals),
            )

        diversity = self._sample_diversity(max_pairs=50)

        return GenerationStats(
            generation=self.generation,
            best_fitness=max(fitnesses),
            mean_fitness=sum(fitnesses) / len(fitnesses),
            worst_fitness=min(fitnesses),
            diversity=diversity,
            population_size=len(self.individuals),
        )

    def _sample_diversity(self, max_pairs: int = 50) -> float:
        """Estimate population diversity by sampling pairwise distances."""
        import random as _rand

        n = len(self.individuals)
        if n < 2:
            return 0.0

        distances: list[float] = []
        pairs_to_check = min(max_pairs, n * (n - 1) // 2)
        attempts = 0
        while len(distances) < pairs_to_check and attempts < pairs_to_check * 3:
            i, j = _rand.sample(range(n), 2)
            try:
                distances.append(self.individuals[i].distance(self.individuals[j]))
            except ValueError as e:
                logger.debug("Distance calculation failed for individuals %d and %d: %s", i, j, e)
                pass
            attempts += 1

        return sum(distances) / len(distances) if distances else 0.0
