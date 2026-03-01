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
from pathlib import Path
from typing import Any, Dict, Callable

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
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
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add evolutionary AI-specific arguments."""
        group = parser.add_argument_group("Evolution Options")
        group.add_argument(
            "--generations", "-g", type=int, default=10,
            help="Number of generations to evolve (default: 10)"
        )
        group.add_argument(
            "--population-size", "-p", type=int, default=20,
            help="Population size (default: 20)"
        )
        group.add_argument(
            "--genome-length", type=int, default=10,
            help="Length of each genome (default: 10)"
        )
        group.add_argument(
            "--mutation-rate", type=float, default=0.05,
            help="Mutation rate (default: 0.05)"
        )
        group.add_argument(
            "--elitism", type=int, default=2,
            help="Number of elite individuals to preserve (default: 2)"
        )
        group.add_argument(
            "--fitness-function", choices=["sum", "product", "peaks"],
            default="sum", help="Fitness function to use (default: sum)"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
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
            self.log_info(f"Would evolve population: {args.population_size} individuals, {args.generations} generations")
            results["dry_run"] = True
            return results

        # Import evolutionary_ai module (after dry_run check)
        from codomyrmex.evolutionary_ai import (
            Population
        )

        # Select fitness function
        fitness_fn = self._get_fitness_function(args.fitness_function)
        self.log_info(f"Using fitness function: {args.fitness_function}")

        # Create population
        self.log_info(f"\n1. Creating population: {args.population_size} individuals, genome length {args.genome_length}")
        population = Population(size=args.population_size, genome_length=args.genome_length)
        self.log_success(f"Created population with {len(population.individuals)} individuals")

        # Evolution loop
        self.log_info(f"\n2. Running evolution for {args.generations} generations")
        start_time = time.perf_counter()

        for gen in range(args.generations):
            # Evaluate
            population.evaluate(fitness_fn)
            best = population.get_best()

            # Record history
            gen_stats = {
                "generation": gen + 1,
                "best_fitness": best.fitness,
                "avg_fitness": sum(g.fitness for g in population.individuals if g.fitness) / len(population.individuals),
            }
            results["evolution_history"].append(gen_stats)

            if config.verbose:
                self.log_debug(f"Gen {gen + 1}: best={best.fitness:.4f}, avg={gen_stats['avg_fitness']:.4f}")

            # Evolve (except last generation)
            if gen < args.generations - 1:
                population.evolve(mutation_rate=args.mutation_rate, elitism=args.elitism)

        evolution_time = time.perf_counter() - start_time

        # Final evaluation
        population.evaluate(fitness_fn)
        final_best = population.get_best()

        self.log_success(f"Evolution completed in {evolution_time:.2f}s")
        self.log_info(f"Best fitness: {final_best.fitness:.6f}")

        # Test operators
        self.log_info("\n3. Testing genetic operators")
        operator_results = self._test_operators(args.genome_length, args.mutation_rate)
        results["operator_tests"] = operator_results
        self.log_success(f"Operators tested: crossover, mutation, selection")

        # Compile statistics
        results["statistics"] = {
            "evolution_time_seconds": evolution_time,
            "final_best_fitness": final_best.fitness,
            "initial_best_fitness": results["evolution_history"][0]["best_fitness"],
            "improvement": final_best.fitness - results["evolution_history"][0]["best_fitness"],
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
        def sum_fitness(genome):
            return sum(genome.genes) / len(genome.genes)

        def product_fitness(genome):
            result = 1.0
            for gene in genome.genes:
                result *= (gene + 0.1)
            return result

        def peaks_fitness(genome):
            # Multi-modal fitness landscape
            peak1 = sum((g - 0.3) ** 2 for g in genome.genes)
            peak2 = sum((g - 0.7) ** 2 for g in genome.genes)
            return 1.0 / (1.0 + min(peak1, peak2))

        functions = {
            "sum": sum_fitness,
            "product": product_fitness,
            "peaks": peaks_fitness,
        }
        return functions[name]

    def _test_operators(self, genome_length: int, mutation_rate: float) -> Dict[str, Any]:
        """Test genetic operators."""
        from codomyrmex.evolutionary_ai import Genome, crossover, mutate, tournament_selection

        results = {}

        # Test crossover
        parent1 = Genome.random(genome_length)
        parent2 = Genome.random(genome_length)
        child1, child2 = crossover(parent1, parent2)
        results["crossover"] = {
            "parent1_length": len(parent1),
            "parent2_length": len(parent2),
            "child1_length": len(child1),
            "child2_length": len(child2),
            "success": len(child1) == genome_length and len(child2) == genome_length,
        }

        # Test mutation
        original = Genome.random(genome_length)
        original_genes = original.genes.copy()
        mutated = mutate(original, rate=mutation_rate)
        changes = sum(1 for a, b in zip(original_genes, mutated.genes) if a != b)
        results["mutation"] = {
            "original_length": len(original_genes),
            "mutated_length": len(mutated.genes),
            "changes": changes,
            "mutation_rate": mutation_rate,
        }

        # Test selection
        test_population = [Genome.random(genome_length) for _ in range(10)]
        for g in test_population:
            g.fitness = sum(g.genes)
        selected = tournament_selection(test_population, tournament_size=3)
        results["selection"] = {
            "population_size": len(test_population),
            "selected_fitness": selected.fitness,
            "selection_success": selected in test_population,
        }

        return results


if __name__ == "__main__":
    script = EvolutionaryAIScript()
    sys.exit(script.execute())
