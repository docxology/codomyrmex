#!/usr/bin/env python3
"""Evolutionary AI Module - Comprehensive Usage Script.

Demonstrates genetic algorithms with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --generations 20         # More generations
    python basic_usage.py --population-size 50     # Larger population
    python basic_usage.py --verbose                # Verbose output
"""

import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util

script_base_path = (
    project_root / "src" / "codomyrmex" / "utils" / "process" / "script_base.py"
)
if not script_base_path.exists():
    # Try alternate location if project structure differs
    script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"

spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class EvolutionaryAIScript(ScriptBase):
    """Comprehensive evolutionary AI module demonstration."""

    def __init__(self):
        super().__init__(
            name="evolutionary_ai_usage",
            description="Demonstrate and test evolutionary algorithms",
            version="1.1.0",
        )

    def add_arguments(self, parser):
        """Add evolutionary AI-specific arguments."""
        group = parser.add_argument_group("Evolution Options")
        group.add_argument(
            "--generations",
            "-g",
            type=int,
            default=10,
            help="Number of generations to evolve (default: 10)",
        )
        group.add_argument(
            "--population-size",
            "-p",
            type=int,
            default=20,
            help="Population size (default: 20)",
        )
        group.add_argument(
            "--genome-length",
            type=int,
            default=10,
            help="Length of each genome (default: 10)",
        )
        group.add_argument(
            "--mutation-rate",
            type=float,
            default=0.1,
            help="Mutation rate (default: 0.1)",
        )
        group.add_argument(
            "--elitism",
            type=int,
            default=2,
            help="Number of elite individuals to preserve (default: 2)",
        )
        group.add_argument(
            "--fitness-function",
            choices=["sum", "product", "peaks"],
            default="sum",
            help="Fitness function to use (default: sum)",
        )

    def run(self, args, config: ScriptConfig) -> dict[str, Any]:
        """Execute evolutionary algorithm demonstrations."""
        results = {
            "config": {
                "generations": args.generations,
                "population_size": args.population_size,
                "genome_length": args.genome_length,
                "mutation_rate": args.mutation_rate,
            },
            "evolution_history": [],
            "final_population": {},
            "statistics": {},
        }

        if config.dry_run:
            self.log_info(
                f"Would evolve population: {args.population_size} individuals, {args.generations} generations"
            )
            results["dry_run"] = True
            return results

        # Import improved evolutionary_ai module
        from codomyrmex.evolutionary_ai import (
            GaussianMutation,
            Population,
            SinglePointCrossover,
            TournamentSelection,
        )

        # Select fitness function
        fitness_fn = self._get_fitness_function(args.fitness_function)
        self.log_info(f"Using fitness function: {args.fitness_function}")

        # Set up operators
        sel = TournamentSelection(tournament_size=3)
        cross = SinglePointCrossover(crossover_rate=0.8)
        mut = GaussianMutation(mutation_rate=args.mutation_rate, sigma=0.05)

        # Create population
        self.log_info(
            f"\n1. Creating population: {args.population_size} individuals, genome length {args.genome_length}"
        )
        population = Population.random_genome_population(
            size=args.population_size, genome_length=args.genome_length
        )
        self.log_success(
            f"Created population with {len(population.individuals)} individuals"
        )

        # Evolution loop
        self.log_info(f"\n2. Running evolution for {args.generations} generations")
        start_time = time.perf_counter()

        for gen in range(args.generations):
            # Evaluate
            population.evaluate(fitness_fn)
            best = population.get_best()
            mean_fit = population.mean_fitness()

            # Record history
            gen_stats = {
                "generation": gen + 1,
                "best_fitness": best.fitness,
                "avg_fitness": mean_fit,
            }
            results["evolution_history"].append(gen_stats)

            if config.verbose:
                self.log_debug(
                    f"Gen {gen + 1}: best={best.fitness:.4f}, avg={mean_fit:.4f}"
                )

            # Evolve (except last generation)
            if gen < args.generations - 1:
                population.evolve(
                    selection_operator=sel,
                    crossover_operator=cross,
                    mutation_operator=mut,
                    elitism=args.elitism,
                )

        evolution_time = time.perf_counter() - start_time

        # Final evaluation
        population.evaluate(fitness_fn)
        final_best = population.get_best()

        self.log_success(f"Evolution completed in {evolution_time:.2f}s")
        self.log_info(f"Best fitness: {final_best.fitness:.6f}")

        # Compile statistics
        results["statistics"] = {
            "evolution_time_seconds": evolution_time,
            "final_best_fitness": final_best.fitness,
            "initial_best_fitness": results["evolution_history"][0]["best_fitness"],
            "improvement": final_best.fitness
            - results["evolution_history"][0]["best_fitness"],
            "generations_per_second": args.generations / evolution_time,
        }

        results["final_population"] = {
            "best_genome": final_best.genes,
            "best_fitness": final_best.fitness,
            "population_size": len(population.individuals),
        }

        # Metrics
        self.add_metric("best_fitness", final_best.fitness)
        self.add_metric("evolution_time", evolution_time)
        self.add_metric("improvement", results["statistics"]["improvement"])

        return results

    def _get_fitness_function(self, name: str) -> Callable:
        """Get fitness function by name."""

        def sum_fitness(genes):
            return sum(genes) / len(genes)

        def product_fitness(genes):
            result = 1.0
            for gene in genes:
                result *= gene + 0.1
            return result

        def peaks_fitness(genes):
            # Multi-modal fitness landscape
            peak1 = sum((g - 0.3) ** 2 for g in genes)
            peak2 = sum((g - 0.7) ** 2 for g in genes)
            return 1.0 / (1.0 + min(peak1, peak2))

        functions = {
            "sum": sum_fitness,
            "product": product_fitness,
            "peaks": peaks_fitness,
        }
        return lambda ind: functions[name](ind.genes)

    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "evolutionary_ai"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/evolutionary_ai/config.yaml")


if __name__ == "__main__":
    script = EvolutionaryAIScript()
    sys.exit(script.execute())
