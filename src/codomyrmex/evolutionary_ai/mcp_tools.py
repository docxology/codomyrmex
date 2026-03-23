"""MCP tool definitions for the evolutionary_ai module.

Exposes genetic algorithm operations as MCP tools for agent consumption.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_population():
    """Lazy import of Population."""
    from codomyrmex.evolutionary_ai.population.population import Population

    return Population


def _get_genome():
    """Lazy import of Genome."""
    from codomyrmex.evolutionary_ai.genome.genome import Genome

    return Genome


@mcp_tool(
    category="evolutionary_ai",
    description="list available genetic operators (mutation, crossover, selection strategies).",
)
def evolutionary_ai_list_operators() -> dict[str, Any]:
    """list all available genetic operators.

    Returns:
        dict with keys: status, mutation_operators, crossover_operators,
        selection_operators
    """
    try:
        return {
            "status": "success",
            "mutation_operators": [
                {
                    "name": "BitFlipMutation",
                    "description": "Flip bits in binary genomes",
                },
                {"name": "SwapMutation", "description": "Swap two gene positions"},
                {
                    "name": "GaussianMutation",
                    "description": "Add Gaussian noise to real-valued genes",
                },
                {
                    "name": "ScrambleMutation",
                    "description": "Scramble a random segment",
                },
            ],
            "crossover_operators": [
                {
                    "name": "SinglePointCrossover",
                    "description": "Split at one random point",
                },
                {
                    "name": "TwoPointCrossover",
                    "description": "Split at two random points",
                },
                {
                    "name": "UniformCrossover",
                    "description": "Gene-by-gene random parent selection",
                },
                {
                    "name": "BlendCrossover",
                    "description": "BLX-alpha for real-valued genes",
                },
            ],
            "selection_operators": [
                {
                    "name": "TournamentSelection",
                    "description": "Tournament-based selection",
                },
                {
                    "name": "RouletteWheelSelection",
                    "description": "Fitness-proportionate selection",
                },
                {"name": "RankSelection", "description": "Rank-based selection"},
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="evolutionary_ai",
    description=(
        "Create a random population of genomes and optionally run evolution "
        "for a specified number of generations."
    ),
)
def evolutionary_ai_run_evolution(
    population_size: int = 20,
    genome_length: int = 10,
    generations: int = 5,
    gene_low: float = 0.0,
    gene_high: float = 1.0,
) -> dict[str, Any]:
    """Create a population and evolve it for N generations.

    Uses sum-of-genes as the fitness function for demonstration.

    Args:
        population_size: Number of individuals (default: 20).
        genome_length: Genes per individual (default: 10).
        generations: Number of evolution cycles (default: 5).
        gene_low: Lower bound for gene initialization.
        gene_high: Upper bound for gene initialization.

    Returns:
        dict with keys: status, generations_run, best_fitness, mean_fitness,
        converged, history
    """
    if population_size < 2:
        return {"status": "error", "message": "population_size must be >= 2"}
    if genome_length < 1:
        return {"status": "error", "message": "genome_length must be >= 1"}
    if generations < 0:
        return {"status": "error", "message": "generations must be >= 0"}

    try:
        PopClass = _get_population()
        pop = PopClass.random_genome_population(
            size=population_size,
            genome_length=genome_length,
            gene_low=gene_low,
            gene_high=gene_high,
        )

        # Simple fitness: sum of genes
        def fitness_fn(ind):
            return sum(ind.genes)

        pop.evaluate(fitness_fn)

        for _ in range(generations):
            pop.evolve()
            pop.evaluate(fitness_fn)

        best = pop.get_best()
        return {
            "status": "success",
            "generations_run": generations,
            "best_fitness": best.fitness,
            "mean_fitness": pop.mean_fitness(),
            "converged": pop.is_converged(),
            "population_size": len(pop.individuals),
            "history": [
                {
                    "generation": s.generation,
                    "best_fitness": s.best_fitness,
                    "mean_fitness": s.mean_fitness,
                    "diversity": s.diversity,
                }
                for s in pop.history
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="evolutionary_ai",
    description="Create a random genome and return its statistics.",
)
def evolutionary_ai_genome_stats(
    genome_length: int = 10,
    gene_low: float = 0.0,
    gene_high: float = 1.0,
) -> dict[str, Any]:
    """Create a random genome and compute its statistics.

    Args:
        genome_length: Number of genes (default: 10).
        gene_low: Lower bound for gene values.
        gene_high: Upper bound for gene values.

    Returns:
        dict with keys: status, length, mean, std, min_val, max_val, genes
    """
    if genome_length < 1:
        return {"status": "error", "message": "genome_length must be >= 1"}
    try:
        GenomeClass = _get_genome()
        genome = GenomeClass.random(genome_length, low=gene_low, high=gene_high)
        stats = genome.stats()
        return {
            "status": "success",
            "length": stats.length,
            "mean": stats.mean,
            "std": stats.std,
            "min_val": stats.min_val,
            "max_val": stats.max_val,
            "genes": genome.genes,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
