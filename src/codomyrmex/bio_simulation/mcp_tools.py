"""MCP tool definitions for the bio_simulation module.

Exposes ant colony simulation and genomics/population evolution as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_colony():
    """Lazy import of Colony to avoid circular deps."""
    from codomyrmex.bio_simulation.ant_colony.colony import Colony

    return Colony


def _get_population():
    """Lazy import of Population to avoid circular deps."""
    from codomyrmex.bio_simulation.genomics.population import Population

    return Population


@mcp_tool(
    category="bio_simulation",
    description="Run an ant colony foraging simulation and return statistics.",
)
def bio_simulation_run_colony(
    population: int = 20,
    hours: int = 1,
    seed: int | None = None,
    food_sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run an ant colony simulation for the given number of hours.

    Args:
        population: Number of ants to spawn (default 20).
        hours: Number of hours to simulate (default 1).
        seed: Random seed for reproducibility.
        food_sources: Optional list of food sources, each with 'position' [x, y] and 'amount'.

    Returns:
        dict with status, colony stats, and step summary.
    """
    try:
        Colony = _get_colony()
        colony = Colony(population=population, seed=seed)

        if food_sources:
            for fs in food_sources:
                pos = tuple(fs["position"])
                colony.add_food_source(pos, fs.get("amount", 100.0))

        step_result = colony.step(hours=hours)
        stats = colony.stats()

        return {
            "status": "success",
            "step_summary": step_result,
            "colony_stats": stats,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="bio_simulation",
    description="Get current statistics from an ant colony simulation.",
)
def bio_simulation_colony_stats(
    population: int = 10,
    seed: int | None = None,
) -> dict[str, Any]:
    """Create a colony and return its initial statistics without running simulation.

    Args:
        population: Number of ants (default 10).
        seed: Random seed for reproducibility.

    Returns:
        dict with status and colony statistics.
    """
    try:
        Colony = _get_colony()
        colony = Colony(population=population, seed=seed)
        stats = colony.stats()

        return {
            "status": "success",
            "stats": stats,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="bio_simulation",
    description="Evolve a population of genomes using a genetic algorithm.",
)
def bio_simulation_evolve_population(
    population_size: int = 50,
    generations: int = 10,
    mutation_rate: float = 0.05,
) -> dict[str, Any]:
    """Run a genetic algorithm on a population of genomes.

    Args:
        population_size: Number of individuals in the population (default 50).
        generations: Number of generations to evolve (default 10).
        mutation_rate: Per-trait mutation probability (default 0.05).

    Returns:
        dict with status, best genome fitness, average fitness, trait distribution, and history.
    """
    try:
        Population = _get_population()
        from codomyrmex.bio_simulation.genomics.genome import Genome

        initial_genomes = [Genome.random() for _ in range(population_size)]
        pop = Population(
            genomes=initial_genomes,
            mutation_rate=mutation_rate,
        )

        pop.evolve(generations=generations)
        best = pop.get_best()

        return {
            "status": "success",
            "generations_run": generations,
            "population_size": population_size,
            "best_fitness": round(best.fitness_score(), 4),
            "average_fitness": round(pop.average_fitness(), 4),
            "trait_distribution": pop.trait_distribution(),
            "history": pop.history,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
