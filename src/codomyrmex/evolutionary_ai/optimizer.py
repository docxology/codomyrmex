"""Integrates the GA into prompt tuning and configuration spaces.

Provides `optimize_config` to cleanly map float vectors to constrained
parameter boundaries and recursively evolve to find the peak fitness.
"""

from collections.abc import Callable

from .genetic import Chromosome, GeneticAlgorithm


def optimize_config(
    param_bounds: dict[str, tuple[float, float]],
    fitness_fn: Callable[[dict[str, float]], float],
    generations: int = 50,
    pop_size: int = 20,
) -> Chromosome:
    """Optimize a configuration dictionary by mapping genes to bounded floats.

    Args:
        param_bounds: Map of param name to (min_val, max_val).
        fitness_fn: Callback taking a decoded config and returning a float score.
        generations: How many evolutionary generations to run.
        pop_size: Individuals per generation.

    Returns:
        The best Chromosome found.
    """
    keys = list(param_bounds.keys())

    def decode(genome_list: list[float]) -> dict[str, float]:
        """Scale normalized [0, 1] genes to physical config bounds."""
        config = {}
        for i, k in enumerate(keys):
            low, high = param_bounds[k]
            # Ensure genes outside [0, 1] from mutation are clamped
            normalized = max(0.0, min(1.0, genome_list[i]))
            val = low + normalized * (high - low)
            config[k] = val
        return config

    # Initialize GA over normalized [0, 1] continuous space
    ga = GeneticAlgorithm(pop_size, len(keys), mutation_rate=0.3)

    # Run generations
    for _ in range(generations):
        ga.step(
            lambda g: fitness_fn(decode(list(g.genes)))
        )  # evaluate on mapped floats

    # Final evaluation for the generation loop
    ga.population.evaluate(lambda g: fitness_fn(decode(list(g.genes))))

    best_genome = ga.population.get_best()
    best_config = decode(list(best_genome.genes))

    return Chromosome(best_genome, best_config)
