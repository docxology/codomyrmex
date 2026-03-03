"""
Genetic operators for evolutionary algorithms.

Provides mutation and crossover operators for genetic algorithms.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from codomyrmex.evolutionary_ai.genome.genome import Individual

T = TypeVar("T")


# ─── Mutation Operators ─────────────────────────────────────────────────


class MutationOperator(ABC, Generic[T]):
    """Abstract base class for mutation operators."""

    def __init__(self, mutation_rate: float = 0.1):
        if not (0.0 <= mutation_rate <= 1.0):
            raise ValueError("mutation_rate must be in [0.0, 1.0]")
        self.mutation_rate = mutation_rate

    @abstractmethod
    def mutate(self, individual: Individual[T]) -> Individual[T]:
        """Apply mutation to an individual.

        Args:
            individual: The individual to mutate.

        Returns:
            A new mutated Individual.
        """
        pass


class BitFlipMutation(MutationOperator[list[int]]):
    """Bit flip mutation for binary representations.

    Flips each bit with probability ``mutation_rate``.
    """

    def mutate(self, individual: Individual[list[int]]) -> Individual[list[int]]:
        """Mutate binary genome."""
        genes = list(individual.genes)

        for i in range(len(genes)):
            if random.random() < self.mutation_rate:
                genes[i] = 1 - genes[i]  # Flip bit

        # Return same class as input to preserve specialized methods (e.g. Genome.distance)
        return individual.__class__(genes=genes, metadata=individual.metadata.copy())


class SwapMutation(MutationOperator[list[Any]]):
    """Swap mutation for permutation representations.

    Swaps two randomly chosen gene positions with probability ``mutation_rate``.
    """

    def mutate(self, individual: Individual[list[Any]]) -> Individual[list[Any]]:
        """Mutate by swapping two genes."""
        genes = list(individual.genes)

        if len(genes) >= 2 and random.random() < self.mutation_rate:
            i, j = random.sample(range(len(genes)), 2)
            genes[i], genes[j] = genes[j], genes[i]

        return individual.__class__(genes=genes, metadata=individual.metadata.copy())


class GaussianMutation(MutationOperator[list[float]]):
    """Gaussian mutation for real-valued representations.

    Adds Gaussian noise to each gene with probability ``mutation_rate``.

    Args:
        mutation_rate: Per-gene probability of mutation.
        sigma: Standard deviation of the Gaussian noise.
        bounds: Optional (min, max) bounds to clamp gene values.
    """

    def __init__(
        self,
        mutation_rate: float = 0.1,
        sigma: float = 0.1,
        bounds: tuple[float, float] | None = None,
    ):
        super().__init__(mutation_rate)
        self.sigma = sigma
        self.bounds = bounds

    def mutate(self, individual: Individual[list[float]]) -> Individual[list[float]]:
        """Mutate genes with Gaussian noise."""
        genes = list(individual.genes)

        for i in range(len(genes)):
            if random.random() < self.mutation_rate:
                genes[i] += random.gauss(0, self.sigma)

                if self.bounds:
                    genes[i] = max(self.bounds[0], min(self.bounds[1], genes[i]))

        return individual.__class__(genes=genes, metadata=individual.metadata.copy())


class ScrambleMutation(MutationOperator[list[Any]]):
    """Scramble mutation for permutation representations.

    Selects a random segment and reorders its elements.
    """

    def mutate(self, individual: Individual[list[Any]]) -> Individual[list[Any]]:
        """Mutate by scrambling a subset of genes."""
        genes = list(individual.genes)

        if len(genes) >= 2 and random.random() < self.mutation_rate:
            start = random.randint(0, len(genes) - 2)
            end = random.randint(start + 2, len(genes))
            subset = genes[start:end]
            random.shuffle(subset)
            genes[start:end] = subset

        return individual.__class__(genes=genes, metadata=individual.metadata.copy())


# ─── Crossover Operators ────────────────────────────────────────────────


class CrossoverOperator(ABC, Generic[T]):
    """Abstract base class for crossover operators."""

    def __init__(self, crossover_rate: float = 0.8):
        if not (0.0 <= crossover_rate <= 1.0):
            raise ValueError("crossover_rate must be in [0.0, 1.0]")
        self.crossover_rate = crossover_rate

    @abstractmethod
    def crossover(
        self,
        parent1: Individual[T],
        parent2: Individual[T],
    ) -> tuple[Individual[T], Individual[T]]:
        """Create offspring from two parents.

        Args:
            parent1: First parent.
            parent2: Second parent.

        Returns:
            A tuple of two child Individuals.
        """
        pass

    def _should_crossover(self) -> bool:
        """Decide whether to perform crossover based on rate."""
        return random.random() < self.crossover_rate

    def _copy_parent(self, parent: Individual[T]) -> Individual[T]:
        """Create a copy of a parent, preserving its class."""
        return parent.__class__(
            genes=(
                list(parent.genes) if isinstance(parent.genes, list) else parent.genes
            ),
            fitness=parent.fitness,
            metadata=dict(parent.metadata),
        )


class SinglePointCrossover(CrossoverOperator[list[Any]]):
    """Single point crossover.

    Splits parents at a random point and swaps the segments.
    """

    def crossover(
        self,
        parent1: Individual[list[Any]],
        parent2: Individual[list[Any]],
    ) -> tuple[Individual[list[Any]], Individual[list[Any]]]:
        """Perform single point crossover."""
        if not self._should_crossover():
            return self._copy_parent(parent1), self._copy_parent(parent2)

        length = min(len(parent1.genes), len(parent2.genes))
        if length < 2:
            return self._copy_parent(parent1), self._copy_parent(parent2)

        point = random.randint(1, length - 1)

        child1_genes = list(parent1.genes[:point]) + list(parent2.genes[point:])
        child2_genes = list(parent2.genes[:point]) + list(parent1.genes[point:])

        return (
            parent1.__class__(genes=child1_genes),
            parent1.__class__(genes=child2_genes),
        )


class TwoPointCrossover(CrossoverOperator[list[Any]]):
    """Two point crossover.

    Selects two random points and swaps the segment between them.
    """

    def crossover(
        self,
        parent1: Individual[list[Any]],
        parent2: Individual[list[Any]],
    ) -> tuple[Individual[list[Any]], Individual[list[Any]]]:
        """Perform two point crossover."""
        if not self._should_crossover():
            return self._copy_parent(parent1), self._copy_parent(parent2)

        length = min(len(parent1.genes), len(parent2.genes))
        if length < 3:
            # Fall back to single point if too short
            return SinglePointCrossover(self.crossover_rate).crossover(parent1, parent2)

        point1, point2 = sorted(random.sample(range(1, length), 2))

        child1_genes = (
            list(parent1.genes[:point1])
            + list(parent2.genes[point1:point2])
            + list(parent1.genes[point2:])
        )
        child2_genes = (
            list(parent2.genes[:point1])
            + list(parent1.genes[point1:point2])
            + list(parent2.genes[point2:])
        )

        return (
            parent1.__class__(genes=child1_genes),
            parent1.__class__(genes=child2_genes),
        )


class UniformCrossover(CrossoverOperator[list[Any]]):
    """Uniform crossover.

    Each gene is independently inherited from either parent with probability ``mixing_ratio``.

    Args:
        crossover_rate: Probability of performing crossover.
        mixing_ratio: Probability of selecting from parent1 (default 0.5).
    """

    def __init__(self, crossover_rate: float = 0.8, mixing_ratio: float = 0.5):
        super().__init__(crossover_rate)
        if not (0.0 <= mixing_ratio <= 1.0):
            raise ValueError("mixing_ratio must be in [0.0, 1.0]")
        self.mixing_ratio = mixing_ratio

    def crossover(
        self,
        parent1: Individual[list[Any]],
        parent2: Individual[list[Any]],
    ) -> tuple[Individual[list[Any]], Individual[list[Any]]]:
        """Perform uniform crossover."""
        if not self._should_crossover():
            return self._copy_parent(parent1), self._copy_parent(parent2)

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
            parent1.__class__(genes=child1_genes),
            parent1.__class__(genes=child2_genes),
        )


class BlendCrossover(CrossoverOperator[list[float]]):
    """BLX-alpha crossover for real-valued representations.

    Offspring genes are chosen uniformly from [min - alpha*diff, max + alpha*diff].

    Args:
        crossover_rate: Probability of performing crossover.
        alpha: Blend factor (default 0.5).
    """

    def __init__(self, crossover_rate: float = 0.8, alpha: float = 0.5):
        super().__init__(crossover_rate)
        self.alpha = alpha

    def crossover(
        self,
        parent1: Individual[list[float]],
        parent2: Individual[list[float]],
    ) -> tuple[Individual[list[float]], Individual[list[float]]]:
        """Perform blend crossover."""
        if not self._should_crossover():
            return self._copy_parent(parent1), self._copy_parent(parent2)

        child1_genes = []
        child2_genes = []

        for g1, g2 in zip(parent1.genes, parent2.genes, strict=False):
            min_val = min(g1, g2)
            max_val = max(g1, g2)
            diff = max_val - min_val

            low = min_val - self.alpha * diff
            high = max_val + self.alpha * diff

            child1_genes.append(random.uniform(low, high))
            child2_genes.append(random.uniform(low, high))

        return (
            parent1.__class__(genes=child1_genes),
            parent1.__class__(genes=child2_genes),
        )


__all__ = [
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
]
