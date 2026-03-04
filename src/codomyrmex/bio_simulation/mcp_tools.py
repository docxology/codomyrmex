"""MCP tools for the bio_simulation module.

Exposes tools for running colony simulations and evolving
populations via genetic algorithms.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="bio_simulation",
    description=(
        "Run an ant colony simulation for a specified number of hours "
        "and return a statistical summary of the colony's final state."
    ),
)
def bio_simulation_run_colony(population: int, hours: int) -> dict[str, Any]:
    """Run a colony simulation and return its final statistics.

    Args:
        population: Number of ants to simulate.
        hours: Number of hours to simulate.

    Returns:
        A dictionary containing the simulation statistics.
    """
    from codomyrmex.bio_simulation import Colony

    colony = Colony(population=population)
    colony.step(hours=hours)
    return colony.stats()


@mcp_tool(
    category="bio_simulation",
    description=(
        "Evolve a population of genomes for a specified number of generations "
        "and return the final trait distribution."
    ),
)
def bio_simulation_evolve_population(
    generations: int, size: int
) -> dict[str, dict[str, float]]:
    """Evolve a population and return trait distributions.

    Args:
        generations: Number of generations to evolve.
        size: Size of the population.

    Returns:
        A dictionary mapping traits to their statistical distributions.
    """
    from codomyrmex.bio_simulation import Genome, Population

    # Initialize a population with random genomes
    genomes = [Genome.random() for _ in range(size)]
    population = Population(genomes=genomes)
    population.evolve(generations=generations)

    return population.trait_distribution()
