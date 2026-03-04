"""MCP tools for the bio_simulation module.

Exposes tools for initializing and running ant colony simulations,
as well as analyzing population genetics over generations.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="bio_simulation",
    description=(
        "Simulate an ant colony with a given population size for a specified number of hours. "
        "Returns the final colony statistics."
    ),
)
def bio_simulate_colony(population: int, hours: int) -> dict[str, Any]:
    """Run an ant colony simulation and return its final state statistics.

    Args:
        population: The initial number of ants in the colony.
        hours: The number of hours to simulate (each hour is 60 ticks).

    Returns:
        A dictionary containing colony statistics (e.g., tick, alive, dead,
        food_collected, etc.).
    """
    from codomyrmex.bio_simulation import Colony

    colony = Colony(population=population)
    colony.step(hours=hours)
    return colony.stats()


@mcp_tool(
    category="bio_simulation",
    description=(
        "Analyze the genetics of a population of ants over a specified number of generations. "
        "Returns the distribution of genetic traits after evolution."
    ),
)
def bio_analyze_genetics(
    population_size: int, generations: int
) -> dict[str, dict[str, float]]:
    """Evolve a population and return the resulting genetic trait distribution.

    Args:
        population_size: The number of individuals in the population.
        generations: The number of generations to simulate evolution.

    Returns:
        A dictionary mapping trait names to their statistics (mean, std, min, max).
    """
    from codomyrmex.bio_simulation import Genome, Population

    genomes = [Genome.random() for _ in range(population_size)]
    population = Population(genomes=genomes)
    population.evolve(generations=generations)
    return population.trait_distribution()
