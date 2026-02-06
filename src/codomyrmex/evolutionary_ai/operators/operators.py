"""Genetic operators implementation."""

import random

from .genome import Genome


def crossover(parent1: Genome, parent2: Genome) -> tuple[Genome, Genome]:
    """Perform single-point crossover."""
    if len(parent1) < 2:
        return parent1, parent2
    point = random.randint(1, len(parent1) - 1)
    child1_genes = parent1.genes[:point] + parent2.genes[point:]
    child2_genes = parent2.genes[:point] + parent1.genes[point:]
    return Genome(child1_genes), Genome(child2_genes)

def mutate(genome: Genome, rate: float = 0.01, amount: float = 0.1) -> Genome:
    """Perform Gaussian mutation."""
    new_genes = []
    for gene in genome.genes:
        if random.random() < rate:
            gene += random.gauss(0, amount)
        new_genes.append(gene)
    return Genome(new_genes)

def tournament_selection(population: list[Genome], size: int = 3) -> Genome:
    """Select the best individual from a random sample."""
    sample = random.sample(population, size)
    return max(sample, key=lambda g: g.fitness if g.fitness is not None else -float('inf'))
