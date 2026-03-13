"""Unit tests for the Evolutionary Synthesis genetic algorithm components.

Zero-Mock Policy: Tests use concrete mathematical optimization functions to
verify that the evolutionary engine correctly explores and selects over generations.
"""

import pytest

from codomyrmex.evolutionary_ai.genetic import Chromosome, GeneticAlgorithm
from codomyrmex.evolutionary_ai.optimizer import optimize_config


@pytest.mark.unit
def test_chromosome_initialization():
    """Verify Chromosome wrapping maps a genome correctly."""
    from codomyrmex.evolutionary_ai.genome.genome import Genome

    g = Genome([0.5, 0.2])
    g.fitness = 42.0
    c = Chromosome(g, {"param1": 10.0, "param2": 5.0})

    assert c.fitness == 42.0
    assert c.config["param1"] == 10.0


@pytest.mark.unit
def test_genetic_algorithm_step():
    """Verify generational looping strictly increases or maintains fitness."""
    ga = GeneticAlgorithm(pop_size=10, gene_length=2, mutation_rate=0.1)

    # Simple fitness: maximize the sum of genes
    def fitness(genome) -> float:
        return sum(genome.genes)

    ga.step(fitness)
    first_gen_best = ga.population.get_best().fitness

    # Run a few more generations
    for _ in range(5):
        ga.step(fitness)

    final_gen_best = ga.population.get_best().fitness

    assert final_gen_best is not None
    assert first_gen_best is not None
    # Elitism ensures the best fitness never decreases
    assert final_gen_best >= first_gen_best


@pytest.mark.unit
def test_optimize_config_convergence():
    """Verify optimize_config maps abstract floats to bounds and converges.

    Test maximizes a quadratic equation: f(x, y) = -(x - 5)^2 - (y - 10)^2 + 100
    The maximum is exactly 100 at x=5, y=10.
    """
    bounds = {
        "x": (0.0, 10.0),
        "y": (0.0, 20.0),
    }

    def evaluate(config: dict[str, float]) -> float:
        x = config["x"]
        y = config["y"]
        return float(-(x - 5.0)**2 - (y - 10.0)**2 + 100.0)

    # Run for 30 generations
    best_chromosome = optimize_config(
        param_bounds=bounds,
        fitness_fn=evaluate,
        generations=30,
        pop_size=30,
    )

    # It won't hit it exactly, but it should converge close to 100
    assert best_chromosome.fitness is not None
    assert best_chromosome.fitness > 90.0

    # X and Y should be close to 5 and 10
    config = best_chromosome.config
    assert 4.0 < config["x"] < 6.0
    assert 8.0 < config["y"] < 12.0
