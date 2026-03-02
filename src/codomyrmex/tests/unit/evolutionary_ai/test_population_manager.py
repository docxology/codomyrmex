"""
Unit tests for evolutionary_ai.population — Zero-Mock compliant.
"""

import pytest

from codomyrmex.evolutionary_ai.genome.genome import Genome, Individual
from codomyrmex.evolutionary_ai.population.population import Population, GenerationStats
from codomyrmex.evolutionary_ai.operators.operators import (
    SinglePointCrossover,
    GaussianMutation,
)
from codomyrmex.evolutionary_ai.selection.selection import TournamentSelection

@pytest.mark.unit
class TestPopulation:
    def test_population_init(self):
        inds = [Individual(genes=[1.0]), Individual(genes=[2.0])]
        pop = Population(inds)
        assert len(pop.individuals) == 2
        assert pop.generation == 0

    def test_population_empty_init_raises(self):
        with pytest.raises(ValueError):
            Population([])

    def test_random_genome_population(self):
        pop = Population.random_genome_population(size=10, genome_length=5)
        assert len(pop.individuals) == 10
        assert all(len(ind.genes) == 5 for ind in pop.individuals)
        assert all(isinstance(ind, Genome) for ind in pop.individuals)

    def test_evaluate(self):
        pop = Population.random_genome_population(size=5, genome_length=3)
        pop.evaluate(lambda ind: sum(ind.genes))
        assert all(ind.fitness is not None for ind in pop.individuals)

    def test_evolve(self):
        pop = Population.random_genome_population(size=20, genome_length=5)
        pop.evaluate(lambda ind: sum(ind.genes))
        initial_best = pop.get_best().fitness
        
        stats = pop.evolve(elitism=2)
        
        assert pop.generation == 1
        assert len(pop.individuals) == 20
        assert stats.generation == 1
        assert len(pop.history) == 1
        
        pop.evaluate(lambda ind: sum(ind.genes))
        assert pop.get_best().fitness >= initial_best

    def test_evolve_custom_operators(self):
        pop = Population.random_genome_population(size=10, genome_length=5)
        sel = TournamentSelection(tournament_size=2)
        cross = SinglePointCrossover(crossover_rate=0.5)
        mut = GaussianMutation(mutation_rate=0.2)
        
        pop.evaluate(lambda ind: sum(ind.genes))
        pop.evolve(selection_operator=sel, crossover_operator=cross, mutation_operator=mut)
        assert pop.generation == 1

    def test_get_best_worst(self):
        inds = [
            Individual(genes=[1.0], fitness=1.0),
            Individual(genes=[5.0], fitness=5.0),
            Individual(genes=[3.0], fitness=3.0),
        ]
        pop = Population(inds)
        assert pop.get_best().fitness == 5.0
        assert pop.get_worst().fitness == 1.0

    def test_mean_fitness(self):
        inds = [
            Individual(genes=[1.0], fitness=1.0),
            Individual(genes=[5.0], fitness=5.0),
        ]
        pop = Population(inds)
        assert pop.mean_fitness() == 3.0

    def test_is_converged(self):
        pop = Population.random_genome_population(size=5, genome_length=2)
        # Manually add history
        pop.history = [
            GenerationStats(0, 10.0, 5.0, 5.0, 5.0, 0.0, 0.1, 5),
            GenerationStats(1, 10.0000001, 5.1, 5.1, 5.1, 0.1, 0.1, 5),
            GenerationStats(2, 10.0000002, 5.2, 5.2, 5.2, 0.2, 0.1, 5),
        ]
        assert pop.is_converged(threshold=1e-5, window=3) is True
        assert pop.is_converged(threshold=1e-9, window=3) is False

    def test_to_dict(self):
        pop = Population.random_genome_population(size=2, genome_length=2)
        pop.evaluate(lambda g: sum(g.genes))
        pop.evolve()
        data = pop.to_dict()
        assert data["generation"] == 1
        assert len(data["individuals"]) == 2
        assert len(data["history"]) == 1

    def test_sample_diversity(self):
        pop = Population.random_genome_population(size=10, genome_length=5)
        div = pop._sample_diversity()
        assert div >= 0.0
