"""
Selection operators for evolutionary algorithms.

Provides an abstract SelectionOperator base class and concrete implementations
for tournament, roulette-wheel (fitness-proportionate), and rank-based
selection.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

# Re-use the Individual dataclass from operators to stay consistent
from ..operators import Individual

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


class TournamentSelection(SelectionOperator[T]):
    """Tournament selection with configurable tournament size.

    In each round a random subset of the population is drawn and the
    fittest individual in that subset is selected.

    Args:
        tournament_size: Number of individuals per tournament (default 3).
    """

    def __init__(self, tournament_size: int = 3) -> None:
        """Execute   Init   operations natively."""
        if tournament_size < 1:
            raise ValueError("tournament_size must be >= 1")
        self.tournament_size = tournament_size

    def select(
        self,
        population: list[Individual[T]],
        count: int,
    ) -> list[Individual[T]]:
        """Execute Select operations natively."""
        selected: list[Individual[T]] = []
        for _ in range(count):
            contestants = random.sample(
                population,
                min(self.tournament_size, len(population)),
            )
            winner = max(
                contestants,
                key=lambda ind: ind.fitness if ind.fitness is not None else float("-inf"),
            )
            selected.append(
                Individual(
                    genes=list(winner.genes) if isinstance(winner.genes, list) else winner.genes,
                    fitness=winner.fitness,
                    metadata=dict(winner.metadata),
                )
            )
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
        """Execute Select operations natively."""
        fitnesses = [ind.fitness if ind.fitness is not None else 0.0 for ind in population]
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
            for ind, sf in zip(population, shifted):
                cumulative += sf
                if cumulative >= pick:
                    selected.append(self._copy_individual(ind))
                    break
            else:
                # Fallback: select the last individual
                selected.append(self._copy_individual(population[-1]))
        return selected

    @staticmethod
    def _copy_individual(ind: Individual[T]) -> Individual[T]:
        """Execute  Copy Individual operations natively."""
        return Individual(
            genes=list(ind.genes) if isinstance(ind.genes, list) else ind.genes,
            fitness=ind.fitness,
            metadata=dict(ind.metadata),
        )


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
        """Execute   Init   operations natively."""
        if not (1.0 <= selection_pressure <= 2.0):
            raise ValueError("selection_pressure must be in [1.0, 2.0]")
        self.selection_pressure = selection_pressure

    def select(
        self,
        population: list[Individual[T]],
        count: int,
    ) -> list[Individual[T]]:
        """Execute Select operations natively."""
        sorted_pop = sorted(
            population,
            key=lambda ind: ind.fitness if ind.fitness is not None else float("-inf"),
        )
        n = len(sorted_pop)

        # Linear ranking probabilities
        sp = self.selection_pressure
        probabilities = [
            (2.0 - sp) / n + (2.0 * rank * (sp - 1.0)) / (n * (n - 1))
            for rank in range(n)
        ]
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]

        selected: list[Individual[T]] = []
        for _ in range(count):
            pick = random.random()
            cumulative = 0.0
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if cumulative >= pick:
                    ind = sorted_pop[i]
                    selected.append(
                        Individual(
                            genes=list(ind.genes) if isinstance(ind.genes, list) else ind.genes,
                            fitness=ind.fitness,
                            metadata=dict(ind.metadata),
                        )
                    )
                    break
            else:
                ind = sorted_pop[-1]
                selected.append(
                    Individual(
                        genes=list(ind.genes) if isinstance(ind.genes, list) else ind.genes,
                        fitness=ind.fitness,
                        metadata=dict(ind.metadata),
                    )
                )
        return selected


__all__ = [
    "RankSelection",
    "RouletteWheelSelection",
    "SelectionOperator",
    "TournamentSelection",
]
