"""
Unit tests for evolutionary_ai module — Zero-Mock compliant.
"""

import pytest

import codomyrmex.evolutionary_ai as eai

@pytest.mark.unit
class TestEvolutionaryAIModuleExports:
    def test_core_exports(self):
        assert hasattr(eai, 'Individual')
        assert hasattr(eai, 'Genome')
        assert hasattr(eai, 'Population')

    def test_operator_exports(self):
        assert hasattr(eai, 'SinglePointCrossover')
        assert hasattr(eai, 'GaussianMutation')
        assert hasattr(eai, 'TournamentSelection')

    def test_fitness_exports(self):
        assert hasattr(eai, 'ScalarFitness')
        assert hasattr(eai, 'MultiObjectiveFitness')
        assert hasattr(eai, 'ConstrainedFitness')

@pytest.mark.unit
class TestEvolutionEndToEnd:
    def test_sphere_function_convergence(self):
        # Sphere function: f(x) = sum(x_i^2). We want to minimize, so fitness is -sum(x_i^2).
        def objective(ind):
            return -sum(x**2 for x in ind.genes)

        # Small population for fast test
        pop = eai.Population.random_genome_population(size=20, genome_length=3, gene_low=-5, gene_high=5)
        
        pop.evaluate(objective)
        initial_best = pop.get_best().fitness
        
        # Evolve for some generations
        for _ in range(50):
            pop.evaluate(objective)
            pop.evolve(
                selection_operator=eai.TournamentSelection(3),
                crossover_operator=eai.SinglePointCrossover(0.8),
                mutation_operator=eai.GaussianMutation(0.1, 0.2),
                elitism=2
            )
        
        pop.evaluate(objective)
        final_best = pop.get_best().fitness
        
        # Should have improved (increased, since negative)
        assert final_best >= initial_best
        # Should be closer to zero
        assert final_best > -5.0
