"""
Population management for evolutionary algorithms.

Provides a PopulationManager that handles initialization, generational
evolution, best-individual tracking, and diversity metrics.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from ..operators import (
    CrossoverOperator,
    Individual,
    MutationOperator,
    SelectionOperator,
)

T = TypeVar("T")


@dataclass
class DiversityMetrics:
    """Population diversity statistics.

    Attributes:
        unique_fitness_count: Number of distinct fitness values.
        fitness_std_dev: Standard deviation of fitness values.
        fitness_min: Minimum fitness in the population.
        fitness_max: Maximum fitness in the population.
        fitness_mean: Mean fitness of the population.
        population_size: Total number of individuals.
    """
    unique_fitness_count: int
    fitness_std_dev: float
    fitness_min: float
    fitness_max: float
    fitness_mean: float
    population_size: int


class PopulationManager(Generic[T]):
    """Manages a population of individuals through evolutionary generations.

    Handles initialization, fitness evaluation, selection, crossover,
    mutation, and provides inspection utilities like best-individual
    retrieval and diversity metrics.

    Args:
        selection: The selection operator used to choose parents.
        crossover: The crossover operator for recombination.
        mutation: The mutation operator applied to offspring.
        elitism_count: Number of top individuals to carry forward unchanged
                       into the next generation (default 1).
    """

    def __init__(
        self,
        selection: SelectionOperator[T],
        crossover: CrossoverOperator[T],
        mutation: MutationOperator[T],
        elitism_count: int = 1,
    ) -> None:
        """Execute   Init   operations natively."""
        self._selection = selection
        self._crossover = crossover
        self._mutation = mutation
        self._elitism_count = elitism_count
        self._population: list[Individual[T]] = []
        self._generation: int = 0

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def initialize(
        self,
        size: int,
        genome_factory: Callable[[], T],
    ) -> list[Individual[T]]:
        """Create the initial population using a genome factory.

        Args:
            size: Number of individuals in the population.
            genome_factory: A callable that returns a new random genome
                            each time it is called.

        Returns:
            The newly created population.
        """
        self._population = [
            Individual(genes=genome_factory())
            for _ in range(size)
        ]
        self._generation = 0
        return list(self._population)

    # ------------------------------------------------------------------
    # Evolution
    # ------------------------------------------------------------------

    def evolve_generation(
        self,
        fitness_fn: Callable[[T], float] | None = None,
    ) -> list[Individual[T]]:
        """Advance the population by one generation.

        Steps:
        1. Evaluate fitness if *fitness_fn* is provided and any individual
           has a None fitness.
        2. Carry elite individuals forward.
        3. Select parents, apply crossover and mutation to fill the rest.

        Args:
            fitness_fn: Optional callable ``(genome) -> float``.  If supplied,
                        it is used to fill in missing fitness values before
                        selection.

        Returns:
            The new population after one generation.

        Raises:
            RuntimeError: If the population has not been initialized.
        """
        if not self._population:
            raise RuntimeError("Population not initialized. Call initialize() first.")

        # Evaluate fitness where needed
        if fitness_fn is not None:
            for ind in self._population:
                if ind.fitness is None:
                    ind.fitness = fitness_fn(ind.genes)

        # Sort descending by fitness for elitism
        evaluated = sorted(
            self._population,
            key=lambda ind: ind.fitness if ind.fitness is not None else float("-inf"),
            reverse=True,
        )

        target_size = len(self._population)
        new_population: list[Individual[T]] = []

        # Elitism
        elite_count = min(self._elitism_count, target_size)
        for ind in evaluated[:elite_count]:
            new_population.append(
                Individual(
                    genes=list(ind.genes) if isinstance(ind.genes, list) else ind.genes,
                    fitness=ind.fitness,
                    metadata=dict(ind.metadata),
                )
            )

        # Fill remaining via selection + crossover + mutation
        while len(new_population) < target_size:
            parents = self._selection.select(evaluated, 2)
            child1, child2 = self._crossover.crossover(parents[0], parents[1])
            child1 = self._mutation.mutate(child1)
            child2 = self._mutation.mutate(child2)
            new_population.append(child1)
            if len(new_population) < target_size:
                new_population.append(child2)

        self._population = new_population[:target_size]
        self._generation += 1
        return list(self._population)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def get_best(self) -> Individual[T] | None:
        """Return the individual with the highest fitness.

        Returns:
            The best Individual, or None if the population is empty or
            no individual has been evaluated.
        """
        evaluated = [ind for ind in self._population if ind.fitness is not None]
        if not evaluated:
            return None
        return max(evaluated, key=lambda ind: ind.fitness)  # type: ignore[arg-type]

    def get_diversity_metrics(self) -> DiversityMetrics:
        """Compute diversity statistics for the current population.

        Returns:
            A DiversityMetrics dataclass summarising the population.

        Raises:
            RuntimeError: If the population is empty.
        """
        if not self._population:
            raise RuntimeError("Population is empty.")

        fitnesses = [
            ind.fitness if ind.fitness is not None else 0.0
            for ind in self._population
        ]
        n = len(fitnesses)
        mean = sum(fitnesses) / n
        variance = sum((f - mean) ** 2 for f in fitnesses) / n
        std_dev = math.sqrt(variance)

        return DiversityMetrics(
            unique_fitness_count=len(set(fitnesses)),
            fitness_std_dev=std_dev,
            fitness_min=min(fitnesses),
            fitness_max=max(fitnesses),
            fitness_mean=mean,
            population_size=n,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def population(self) -> list[Individual[T]]:
        """The current population."""
        return list(self._population)

    @property
    def generation(self) -> int:
        """The current generation number (0-indexed)."""
        return self._generation

    def __len__(self) -> int:
        """Execute   Len   operations natively."""
        return len(self._population)

    def __repr__(self) -> str:
        """Execute   Repr   operations natively."""
        best = self.get_best()
        best_fit = best.fitness if best else None
        return (
            f"PopulationManager(size={len(self._population)}, "
            f"generation={self._generation}, best_fitness={best_fit})"
        )


__all__ = [
    "DiversityMetrics",
    "PopulationManager",
]
