"""
Selection operators for evolutionary algorithms.

Provides an abstract SelectionOperator base class and concrete implementations
for tournament, roulette-wheel (fitness-proportionate), and rank-based
selection.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from codomyrmex.evolutionary_ai.genome.genome import Individual

T = TypeVar("T")


class SelectionOperator(ABC, Generic[T]):
    """Abstract base class for selection operators.

    A selection operator chooses a subset of individuals from a population,
    typically biased toward higher-fitness individuals, for reproduction.
    """

    @abstractmethod
    def select(
        self,
        population: list[Individual[T]],
        count: int,
    ) -> list[Individual[T]]:
        """Select *count* individuals from the population.

        Args:
            population: The full set of candidate individuals.  Each
                        individual must have a non-None ``fitness`` value.
            count: Number of individuals to select.

        Returns:
            A list of selected individuals (copies).
        """

    @staticmethod
    def _copy_individual(ind: Individual[T]) -> Individual[T]:
        """Create a copy of an individual, preserving its actual class."""
        new_genes = list(ind.genes) if isinstance(ind.genes, list) else ind.genes
        return ind.__class__(
            genes=new_genes,
            fitness=ind.fitness,
            metadata=dict(ind.metadata),
        )


class TournamentSelection(SelectionOperator[T]):
    """Tournament selection with configurable tournament size.

    In each round a random subset of the population is drawn and the
    fittest individual in that subset is selected.

    Args:
        tournament_size: Number of individuals per tournament (default 3).
    """

    def __init__(self, tournament_size: int = 3) -> None:
        if tournament_size < 1:
            raise ValueError("tournament_size must be >= 1")
        self.tournament_size = tournament_size

    def select(
        self,
        population: list[Individual[T]],
        count: int,
    ) -> list[Individual[T]]:
        """Select."""
        selected: list[Individual[T]] = []
        for _ in range(count):
            contestants = random.sample(
                population,
                min(self.tournament_size, len(population)),
            )
            # Find winner — highest fitness
            winner = max(
                contestants,
                key=lambda ind: (
                    ind.fitness if ind.fitness is not None else -float("inf")
                ),
            )

            # Copy to preserve original and preserve class
            selected.append(self._copy_individual(winner))
        return selected


class RouletteWheelSelection(SelectionOperator[T]):
    """Fitness-proportionate (roulette wheel) selection.

    Each individual's selection probability is proportional to its fitness.
    Negative fitness values are handled by shifting all values so the
    minimum becomes a small positive number.
    """

    def select(
        self,
        population: list[Individual[T]],
        count: int,
    ) -> list[Individual[T]]:
        """Select."""
        if not population:
            return []

        fitnesses = [
            ind.fitness if ind.fitness is not None else 0.0 for ind in population
        ]
        min_f = min(fitnesses)
        shift = abs(min_f) + 1.0 if min_f <= 0 else 0.0
        shifted = [f + shift for f in fitnesses]
        total = sum(shifted)

        if total == 0:
            return [
                self._copy_individual(ind)
                for ind in random.choices(population, k=count)
            ]

        selected: list[Individual[T]] = []
        for _ in range(count):
            pick = random.uniform(0, total)
            cumulative = 0.0
            for ind, sf in zip(population, shifted, strict=False):
                cumulative += sf
                if cumulative >= pick:
                    selected.append(self._copy_individual(ind))
                    break
            else:
                # Fallback: select the last individual
                selected.append(self._copy_individual(population[-1]))
        return selected


class RankSelection(SelectionOperator[T]):
    """Rank-based selection.

    Individuals are ranked by fitness and selection probability is
    proportional to rank rather than raw fitness, reducing the effect of
    super-fit outliers.

    Args:
        selection_pressure: Controls rank scaling.  Must be in [1.0, 2.0].
            1.0 gives uniform selection; 2.0 gives maximum bias toward
            top-ranked individuals.
    """

    def __init__(self, selection_pressure: float = 1.5) -> None:
        if not (1.0 <= selection_pressure <= 2.0):
            raise ValueError("selection_pressure must be in [1.0, 2.0]")
        self.selection_pressure = selection_pressure

    def select(
        self,
        population: list[Individual[T]],
        count: int,
    ) -> list[Individual[T]]:
        """Select."""
        if not population:
            return []

        sorted_pop = sorted(
            population,
            key=lambda ind: ind.fitness if ind.fitness is not None else -float("inf"),
        )
        n = len(sorted_pop)

        # Linear ranking probabilities
        # prob(i) = (2-sp)/n + 2*rank(i)*(sp-1)/(n*(n-1))
        # where rank is from 0 to n-1
        sp = self.selection_pressure
        if n == 1:
            return [self._copy_individual(sorted_pop[0]) for _ in range(count)]

        probabilities = [
            (2.0 - sp) / n + (2.0 * rank * (sp - 1.0)) / (n * (n - 1))
            for rank in range(n)
        ]

        selected: list[Individual[T]] = []
        for _ in range(count):
            pick = random.random()
            cumulative = 0.0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if cumulative >= pick:
                    selected.append(self._copy_individual(sorted_pop[i]))
                    break
            else:
                selected.append(self._copy_individual(sorted_pop[-1]))
        return selected


__all__ = [
    "RankSelection",
    "RouletteWheelSelection",
    "SelectionOperator",
    "TournamentSelection",
]
