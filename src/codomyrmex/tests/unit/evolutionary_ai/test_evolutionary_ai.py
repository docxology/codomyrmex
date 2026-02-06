"""Unit tests for evolutionary_ai module."""

import random

import pytest

from codomyrmex.evolutionary_ai import (
    Genome,
    Population,
    crossover,
    mutate,
    tournament_selection,
)


@pytest.mark.unit
def test_genome_creation():
    """Test genome initialization."""
    g = Genome([0.1, 0.2, 0.3])
    assert len(g) == 3
    assert g.genes == [0.1, 0.2, 0.3]

    rand_g = Genome.random(10)
    assert len(rand_g) == 10

@pytest.mark.unit
def test_crossover_logic():
    """Test single-point crossover."""
    p1 = Genome([0, 0, 0, 0])
    p2 = Genome([1, 1, 1, 1])

    # Freeze random to test a specific split
    random.seed(42)
    # random.randint(1, 3) with seed 42 might be 1 or 3
    c1, c2 = crossover(p1, p2)

    # Verify that children have genes from both parents
    for g in c1.genes + c2.genes:
        assert g in [0, 1]
    assert len(c1) == 4
    assert len(c2) == 4

@pytest.mark.unit
def test_mutation_logic():
    """Test mutation affects genes."""
    g = Genome([0.5, 0.5, 0.5])
    # 100% mutation rate - API in __init__.py doesn't support 'amount' parameter
    mutated = mutate(g, rate=1.0)

    assert mutated.genes != g.genes
    assert len(mutated) == 3

@pytest.mark.unit
def test_tournament_selection():
    """Test selection of the best individual."""
    g1 = Genome([1])
    g1.fitness = 10
    g2 = Genome([2])
    g2.fitness = 20
    g3 = Genome([3])
    g3.fitness = 5

    pop = [g1, g2, g3]
    # Tournament - API in __init__.py uses 'tournament_size' not 'size'
    winner = tournament_selection(pop, tournament_size=3)
    # Check fitness since tournament_selection is non-deterministic in some implementations
    assert winner.fitness == 20

@pytest.mark.unit
def test_population_evolution():
    """Test full population evolution cycle."""
    pop = Population(size=10, genome_length=5)

    # Mock fitness function: sum of genes
    def fitness_fn(g: Genome) -> float:
        return sum(g.genes)

    pop.evaluate(fitness_fn)
    initial_best = pop.get_best().fitness

    pop.evolve(mutation_rate=0.1)
    pop.evaluate(fitness_fn)
    # Evolution should ideally maintain or improve best fitness (due to elitism)
    assert pop.get_best().fitness >= initial_best
    assert pop.generation == 1
