"""
Genetic operators for evolutionary AI.

Provides mutation, crossover, and selection operators for genetic algorithms.
"""

import math
import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

T = TypeVar('T')


class MutationType(Enum):
    """Types of mutation operators."""
    BIT_FLIP = "bit_flip"
    SWAP = "swap"
    SCRAMBLE = "scramble"
    INVERSION = "inversion"
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    BOUNDARY = "boundary"


class CrossoverType(Enum):
    """Types of crossover operators."""
    SINGLE_POINT = "single_point"
    TWO_POINT = "two_point"
    UNIFORM = "uniform"
    BLEND = "blend"
    ORDER = "order"
    CYCLE = "cycle"


class SelectionType(Enum):
    """Types of selection operators."""
    TOURNAMENT = "tournament"
    ROULETTE = "roulette"
    RANK = "rank"
    STEADY_STATE = "steady_state"
    ELITISM = "elitism"
    TRUNCATION = "truncation"


@dataclass
class Individual(Generic[T]):
    """An individual in the population."""
    genes: T
    fitness: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other: 'Individual') -> bool:
        """Compare individuals by fitness."""
        if self.fitness is None and other.fitness is None:
            return False
        if self.fitness is None:
            return True
        if other.fitness is None:
            return False
        return self.fitness < other.fitness


class MutationOperator(ABC, Generic[T]):
    """Abstract base class for mutation operators."""

    def __init__(self, mutation_rate: float = 0.1):
        """Execute   Init   operations natively."""
        self.mutation_rate = mutation_rate

    @abstractmethod
    def mutate(self, individual: Individual[T]) -> Individual[T]:
        """Apply mutation to an individual."""
        pass


class BitFlipMutation(MutationOperator[list[int]]):
    """Bit flip mutation for binary representations."""

    def mutate(self, individual: Individual[list[int]]) -> Individual[list[int]]:
        """Execute Mutate operations natively."""
        genes = list(individual.genes)

        for i in range(len(genes)):
            if random.random() < self.mutation_rate:
                genes[i] = 1 - genes[i]  # Flip bit

        return Individual(genes=genes, metadata=individual.metadata.copy())


class SwapMutation(MutationOperator[list[T]]):
    """Swap mutation for permutation representations."""

    def mutate(self, individual: Individual[list[T]]) -> Individual[list[T]]:
        """Execute Mutate operations natively."""
        genes = list(individual.genes)

        if random.random() < self.mutation_rate and len(genes) >= 2:
            i, j = random.sample(range(len(genes)), 2)
            genes[i], genes[j] = genes[j], genes[i]

        return Individual(genes=genes, metadata=individual.metadata.copy())


class GaussianMutation(MutationOperator[list[float]]):
    """Gaussian mutation for real-valued representations."""

    def __init__(
        self,
        mutation_rate: float = 0.1,
        sigma: float = 0.1,
        bounds: tuple[float, float] | None = None,
    ):
        """Execute   Init   operations natively."""
        super().__init__(mutation_rate)
        self.sigma = sigma
        self.bounds = bounds

    def mutate(self, individual: Individual[list[float]]) -> Individual[list[float]]:
        """Execute Mutate operations natively."""
        genes = list(individual.genes)

        for i in range(len(genes)):
            if random.random() < self.mutation_rate:
                genes[i] += random.gauss(0, self.sigma)

                if self.bounds:
                    genes[i] = max(self.bounds[0], min(self.bounds[1], genes[i]))

        return Individual(genes=genes, metadata=individual.metadata.copy())


class ScrambleMutation(MutationOperator[list[T]]):
    """Scramble mutation - scrambles a random subset of genes."""

    def mutate(self, individual: Individual[list[T]]) -> Individual[list[T]]:
        """Execute Mutate operations natively."""
        genes = list(individual.genes)

        if random.random() < self.mutation_rate and len(genes) >= 2:
            start = random.randint(0, len(genes) - 2)
            end = random.randint(start + 1, len(genes))
            subset = genes[start:end]
            random.shuffle(subset)
            genes[start:end] = subset

        return Individual(genes=genes, metadata=individual.metadata.copy())


class CrossoverOperator(ABC, Generic[T]):
    """Abstract base class for crossover operators."""

    def __init__(self, crossover_rate: float = 0.8):
        """Execute   Init   operations natively."""
        self.crossover_rate = crossover_rate

    @abstractmethod
    def crossover(
        self,
        parent1: Individual[T],
        parent2: Individual[T],
    ) -> tuple[Individual[T], Individual[T]]:
        """Create offspring from two parents."""
        pass


class SinglePointCrossover(CrossoverOperator[list[T]]):
    """Single point crossover."""

    def crossover(
        self,
        parent1: Individual[list[T]],
        parent2: Individual[list[T]],
    ) -> tuple[Individual[list[T]], Individual[list[T]]]:
        """Execute Crossover operations natively."""
        if random.random() > self.crossover_rate:
            return parent1, parent2

        length = min(len(parent1.genes), len(parent2.genes))
        point = random.randint(1, length - 1)

        child1_genes = list(parent1.genes[:point]) + list(parent2.genes[point:])
        child2_genes = list(parent2.genes[:point]) + list(parent1.genes[point:])

        return (
            Individual(genes=child1_genes),
            Individual(genes=child2_genes),
        )


class TwoPointCrossover(CrossoverOperator[list[T]]):
    """Two point crossover."""

    def crossover(
        self,
        parent1: Individual[list[T]],
        parent2: Individual[list[T]],
    ) -> tuple[Individual[list[T]], Individual[list[T]]]:
        """Execute Crossover operations natively."""
        if random.random() > self.crossover_rate:
            return parent1, parent2

        length = min(len(parent1.genes), len(parent2.genes))
        point1, point2 = sorted(random.sample(range(1, length), 2))

        child1_genes = (
            list(parent1.genes[:point1]) +
            list(parent2.genes[point1:point2]) +
            list(parent1.genes[point2:])
        )
        child2_genes = (
            list(parent2.genes[:point1]) +
            list(parent1.genes[point1:point2]) +
            list(parent2.genes[point2:])
        )

        return (
            Individual(genes=child1_genes),
            Individual(genes=child2_genes),
        )


class UniformCrossover(CrossoverOperator[list[T]]):
    """Uniform crossover with mixing ratio."""

    def __init__(self, crossover_rate: float = 0.8, mixing_ratio: float = 0.5):
        """Execute   Init   operations natively."""
        super().__init__(crossover_rate)
        self.mixing_ratio = mixing_ratio

    def crossover(
        self,
        parent1: Individual[list[T]],
        parent2: Individual[list[T]],
    ) -> tuple[Individual[list[T]], Individual[list[T]]]:
        """Execute Crossover operations natively."""
        if random.random() > self.crossover_rate:
            return parent1, parent2

        length = min(len(parent1.genes), len(parent2.genes))
        child1_genes = []
        child2_genes = []

        for i in range(length):
            if random.random() < self.mixing_ratio:
                child1_genes.append(parent1.genes[i])
                child2_genes.append(parent2.genes[i])
            else:
                child1_genes.append(parent2.genes[i])
                child2_genes.append(parent1.genes[i])

        return (
            Individual(genes=child1_genes),
            Individual(genes=child2_genes),
        )


class BlendCrossover(CrossoverOperator[list[float]]):
    """BLX-alpha crossover for real-valued representations."""

    def __init__(self, crossover_rate: float = 0.8, alpha: float = 0.5):
        """Execute   Init   operations natively."""
        super().__init__(crossover_rate)
        self.alpha = alpha

    def crossover(
        self,
        parent1: Individual[list[float]],
        parent2: Individual[list[float]],
    ) -> tuple[Individual[list[float]], Individual[list[float]]]:
        """Execute Crossover operations natively."""
        if random.random() > self.crossover_rate:
            return parent1, parent2

        child1_genes = []
        child2_genes = []

        for g1, g2 in zip(parent1.genes, parent2.genes):
            min_val = min(g1, g2)
            max_val = max(g1, g2)
            diff = max_val - min_val

            low = min_val - self.alpha * diff
            high = max_val + self.alpha * diff

            child1_genes.append(random.uniform(low, high))
            child2_genes.append(random.uniform(low, high))

        return (
            Individual(genes=child1_genes),
            Individual(genes=child2_genes),
        )


class SelectionOperator(ABC, Generic[T]):
    """Abstract base class for selection operators."""

    @abstractmethod
    def select(
        self,
        population: list[Individual[T]],
        num_selected: int,
    ) -> list[Individual[T]]:
        """Select individuals from the population."""
        pass


class TournamentSelection(SelectionOperator[T]):
    """Tournament selection."""

    def __init__(self, tournament_size: int = 3):
        """Execute   Init   operations natively."""
        self.tournament_size = tournament_size

    def select(
        self,
        population: list[Individual[T]],
        num_selected: int,
    ) -> list[Individual[T]]:
        """Execute Select operations natively."""
        selected = []

        for _ in range(num_selected):
            tournament = random.sample(population, min(self.tournament_size, len(population)))
            winner = max(tournament, key=lambda ind: ind.fitness or float('-inf'))
            selected.append(Individual(
                genes=list(winner.genes) if isinstance(winner.genes, list) else winner.genes,
                fitness=winner.fitness,
                metadata=winner.metadata.copy(),
            ))

        return selected


class RouletteSelection(SelectionOperator[T]):
    """Roulette wheel (fitness proportionate) selection."""

    def select(
        self,
        population: list[Individual[T]],
        num_selected: int,
    ) -> list[Individual[T]]:
        """Execute Select operations natively."""
        # Handle negative fitness by shifting
        min_fitness = min(ind.fitness or 0 for ind in population)
        shift = abs(min_fitness) + 1 if min_fitness < 0 else 0

        total_fitness = sum((ind.fitness or 0) + shift for ind in population)

        if total_fitness == 0:
            return random.sample(population, min(num_selected, len(population)))

        selected = []
        for _ in range(num_selected):
            pick = random.uniform(0, total_fitness)
            current = 0

            for ind in population:
                current += (ind.fitness or 0) + shift
                if current >= pick:
                    selected.append(Individual(
                        genes=list(ind.genes) if isinstance(ind.genes, list) else ind.genes,
                        fitness=ind.fitness,
                        metadata=ind.metadata.copy(),
                    ))
                    break

        return selected


class RankSelection(SelectionOperator[T]):
    """Rank-based selection."""

    def __init__(self, selection_pressure: float = 2.0):
        """Execute   Init   operations natively."""
        self.selection_pressure = selection_pressure

    def select(
        self,
        population: list[Individual[T]],
        num_selected: int,
    ) -> list[Individual[T]]:
        """Execute Select operations natively."""
        # Sort by fitness
        sorted_pop = sorted(population, key=lambda ind: ind.fitness or float('-inf'))
        n = len(sorted_pop)

        # Assign ranks
        probabilities = []
        for rank in range(n):
            prob = (2 - self.selection_pressure) / n + \
                   (2 * rank * (self.selection_pressure - 1)) / (n * (n - 1))
            probabilities.append(max(0, prob))

        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]

        # Select based on rank probabilities
        selected = []
        for _ in range(num_selected):
            pick = random.random()
            cumulative = 0

            for i, prob in enumerate(probabilities):
                cumulative += prob
                if cumulative >= pick:
                    ind = sorted_pop[i]
                    selected.append(Individual(
                        genes=list(ind.genes) if isinstance(ind.genes, list) else ind.genes,
                        fitness=ind.fitness,
                        metadata=ind.metadata.copy(),
                    ))
                    break

        return selected


class ElitismSelection(SelectionOperator[T]):
    """Elitism selection - always keeps the best individuals."""

    def __init__(self, elite_count: int = 2, base_selector: SelectionOperator | None = None):
        """Execute   Init   operations natively."""
        self.elite_count = elite_count
        self.base_selector = base_selector or TournamentSelection()

    def select(
        self,
        population: list[Individual[T]],
        num_selected: int,
    ) -> list[Individual[T]]:
        """Execute Select operations natively."""
        sorted_pop = sorted(population, key=lambda ind: ind.fitness or float('-inf'), reverse=True)

        elite = sorted_pop[:min(self.elite_count, num_selected)]
        remaining = num_selected - len(elite)

        if remaining > 0:
            rest = self.base_selector.select(population, remaining)
            return elite + rest

        return elite


def create_mutation(
    mutation_type: MutationType,
    **kwargs
) -> MutationOperator:
    """Factory function for mutation operators."""
    operators = {
        MutationType.BIT_FLIP: BitFlipMutation,
        MutationType.SWAP: SwapMutation,
        MutationType.GAUSSIAN: GaussianMutation,
        MutationType.SCRAMBLE: ScrambleMutation,
    }

    op_class = operators.get(mutation_type)
    if not op_class:
        raise ValueError(f"Unknown mutation type: {mutation_type}")

    return op_class(**kwargs)


def create_crossover(
    crossover_type: CrossoverType,
    **kwargs
) -> CrossoverOperator:
    """Factory function for crossover operators."""
    operators = {
        CrossoverType.SINGLE_POINT: SinglePointCrossover,
        CrossoverType.TWO_POINT: TwoPointCrossover,
        CrossoverType.UNIFORM: UniformCrossover,
        CrossoverType.BLEND: BlendCrossover,
    }

    op_class = operators.get(crossover_type)
    if not op_class:
        raise ValueError(f"Unknown crossover type: {crossover_type}")

    return op_class(**kwargs)


def create_selection(
    selection_type: SelectionType,
    **kwargs
) -> SelectionOperator:
    """Factory function for selection operators."""
    operators = {
        SelectionType.TOURNAMENT: TournamentSelection,
        SelectionType.ROULETTE: RouletteSelection,
        SelectionType.RANK: RankSelection,
        SelectionType.ELITISM: ElitismSelection,
    }

    op_class = operators.get(selection_type)
    if not op_class:
        raise ValueError(f"Unknown selection type: {selection_type}")

    return op_class(**kwargs)


__all__ = [
    "MutationType",
    "CrossoverType",
    "SelectionType",
    "Individual",
    "MutationOperator",
    "BitFlipMutation",
    "SwapMutation",
    "GaussianMutation",
    "ScrambleMutation",
    "CrossoverOperator",
    "SinglePointCrossover",
    "TwoPointCrossover",
    "UniformCrossover",
    "BlendCrossover",
    "SelectionOperator",
    "TournamentSelection",
    "RouletteSelection",
    "RankSelection",
    "ElitismSelection",
    "create_mutation",
    "create_crossover",
    "create_selection",
]
