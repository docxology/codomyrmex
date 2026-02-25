"""Genetic operators: crossover, mutation, and selection strategies.

Provides pluggable operators for evolutionary algorithms:
- Crossover: single-point, two-point, uniform
- Mutation: gaussian, uniform, swap
- Selection: tournament, roulette-wheel, rank-based
"""

from __future__ import annotations

import random

from ..genome.genome import Genome

# ─── Crossover Operators ────────────────────────────────────────────────


def crossover(parent1: Genome, parent2: Genome) -> tuple[Genome, Genome]:
    """Perform single-point crossover between two parents.

    If either parent has fewer than 2 genes, returns clones of both parents.
    """
    if len(parent1) < 2:
        return parent1.clone(), parent2.clone()
    point = random.randint(1, len(parent1) - 1)
    child1_genes = parent1.genes[:point] + parent2.genes[point:]
    child2_genes = parent2.genes[:point] + parent1.genes[point:]
    return Genome(child1_genes), Genome(child2_genes)


def two_point_crossover(parent1: Genome, parent2: Genome) -> tuple[Genome, Genome]:
    """Perform two-point crossover.

    Swaps the segment between two randomly chosen cut points.
    """
    n = len(parent1)
    if n < 3:
        return crossover(parent1, parent2)
    p1, p2 = sorted(random.sample(range(1, n), 2))
    c1_genes = parent1.genes[:p1] + parent2.genes[p1:p2] + parent1.genes[p2:]
    c2_genes = parent2.genes[:p1] + parent1.genes[p1:p2] + parent2.genes[p2:]
    return Genome(c1_genes), Genome(c2_genes)


def uniform_crossover(
    parent1: Genome, parent2: Genome, swap_prob: float = 0.5
) -> tuple[Genome, Genome]:
    """Perform uniform crossover — each gene swapped independently.

    Args:
        parent1: First parent genome.
        parent2: Second parent genome.
        swap_prob: Probability of swapping each gene position.
    """
    c1, c2 = [], []
    for g1, g2 in zip(parent1.genes, parent2.genes):
        if random.random() < swap_prob:
            c1.append(g2)
            c2.append(g1)
        else:
            c1.append(g1)
            c2.append(g2)
    return Genome(c1), Genome(c2)


# ─── Mutation Operators ─────────────────────────────────────────────────


def mutate(genome: Genome, rate: float = 0.01, amount: float = 0.1) -> Genome:
    """Perform Gaussian mutation on each gene independently.

    Args:
        genome: The genome to mutate.
        rate: Per-gene probability of mutation.
        amount: Standard deviation of the Gaussian noise.
    """
    new_genes = []
    for gene in genome.genes:
        if random.random() < rate:
            gene += random.gauss(0, amount)
        new_genes.append(gene)
    return Genome(new_genes)


def uniform_mutate(
    genome: Genome, rate: float = 0.01, low: float = 0.0, high: float = 1.0
) -> Genome:
    """Replace genes with uniform random values at the given mutation rate.

    Args:
        genome: Source genome.
        rate: Per-gene probability of replacement.
        low: Lower bound for replacement values.
        high: Upper bound for replacement values.
    """
    new_genes = [
        random.uniform(low, high) if random.random() < rate else g
        for g in genome.genes
    ]
    return Genome(new_genes)


def swap_mutate(genome: Genome) -> Genome:
    """Swap two randomly chosen gene positions."""
    if len(genome) < 2:
        return genome.clone()
    genes = list(genome.genes)
    i, j = random.sample(range(len(genes)), 2)
    genes[i], genes[j] = genes[j], genes[i]
    return Genome(genes)


# ─── Selection Operators ────────────────────────────────────────────────


def _fitness_key(g: Genome) -> float:
    """Safe fitness accessor — unevaluated genomes sort last."""
    return g.fitness if g.fitness is not None else -float("inf")


def tournament_selection(population: list[Genome], size: int = 3) -> Genome:
    """Select the best individual from a random sample (tournament).

    Args:
        population: List of genomes to select from.
        size: Number of individuals in the tournament.
    """
    sample = random.sample(population, min(size, len(population)))
    return max(sample, key=_fitness_key)


def roulette_selection(population: list[Genome]) -> Genome:
    """Fitness-proportionate (roulette wheel) selection.

    All fitnesses must be non-negative. Unevaluated genomes
    are assigned fitness 0 for selection purposes.

    Raises:
        ValueError: If the population is empty.
    """
    if not population:
        raise ValueError("Cannot select from empty population")
    fitnesses = [max(0.0, g.fitness or 0.0) for g in population]
    total = sum(fitnesses)
    if total == 0:
        return random.choice(population)
    pick = random.uniform(0, total)
    current = 0.0
    for genome, fit in zip(population, fitnesses):
        current += fit
        if current >= pick:
            return genome
    return population[-1]  # pragma: no cover — floating point guard


def rank_selection(population: list[Genome]) -> Genome:
    """Rank-based selection — probability proportional to rank, not fitness.

    This avoids domination by super-fit individuals and works with
    negative fitness values.

    Args:
        population: List of genomes (must be non-empty).
    """
    if not population:
        raise ValueError("Cannot select from empty population")
    ranked = sorted(population, key=_fitness_key)
    n = len(ranked)
    # Rank weights: 1, 2, 3, ..., n
    total = n * (n + 1) // 2
    pick = random.randint(1, total)
    current = 0
    for rank, genome in enumerate(ranked, start=1):
        current += rank
        if current >= pick:
            return genome
    return ranked[-1]  # pragma: no cover
