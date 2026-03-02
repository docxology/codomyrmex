#!/usr/bin/env python3
"""
Evolutionary AI utilities.

Usage:
    python evolution_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import random


def create_population(size: int, genome_length: int = 10) -> list:
    """Create initial population."""
    return [[random.randint(0, 1) for _ in range(genome_length)] for _ in range(size)]


def evaluate_fitness(genome: list) -> float:
    """Simple fitness function (count ones)."""
    return sum(genome) / len(genome)


def select_parents(population: list, fitnesses: list, count: int = 2) -> list:
    """Tournament selection."""
    parents = []
    for _ in range(count):
        candidates = random.sample(list(zip(population, fitnesses)), min(3, len(population)))
        winner = max(candidates, key=lambda x: x[1])
        parents.append(winner[0])
    return parents


def crossover(parent1: list, parent2: list) -> list:
    """Single-point crossover."""
    point = random.randint(1, len(parent1) - 1)
    return parent1[:point] + parent2[point:]


def mutate(genome: list, rate: float = 0.1) -> list:
    """Bit-flip mutation."""
    return [1 - g if random.random() < rate else g for g in genome]


def run_evolution(generations: int = 10, pop_size: int = 20) -> dict:
    """Run evolutionary algorithm."""
    population = create_population(pop_size)
    history = []
    
    for gen in range(generations):
        fitnesses = [evaluate_fitness(g) for g in population]
        best_fitness = max(fitnesses)
        avg_fitness = sum(fitnesses) / len(fitnesses)
        history.append({"gen": gen, "best": best_fitness, "avg": avg_fitness})
        
        # Create new population
        new_pop = []
        while len(new_pop) < pop_size:
            parents = select_parents(population, fitnesses)
            child = crossover(parents[0], parents[1])
            child = mutate(child)
            new_pop.append(child)
        
        population = new_pop
    
    return {"generations": generations, "history": history, "final_best": max(fitnesses)}


def main():
    parser = argparse.ArgumentParser(description="Evolutionary AI utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Run command
    run = subparsers.add_parser("run", help="Run evolution")
    run.add_argument("--generations", "-g", type=int, default=10)
    run.add_argument("--population", "-p", type=int, default=20)
    
    # Demo command
    subparsers.add_parser("demo", help="Demo evolution operators")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🧬 Evolutionary AI Utilities\n")
        print("Commands:")
        print("  run  - Run evolutionary algorithm")
        print("  demo - Demo evolution operators")
        return 0
    
    if args.command == "run":
        print(f"🧬 Running Evolution\n")
        print(f"   Generations: {args.generations}")
        print(f"   Population: {args.population}\n")
        
        result = run_evolution(args.generations, args.population)
        
        print("   Progress:")
        for h in result["history"][::max(1, len(result["history"])//5)]:
            bar = "█" * int(h["best"] * 20)
            print(f"   Gen {h['gen']:3d}: {bar} {h['best']:.2f}")
        
        print(f"\n   Final best: {result['final_best']:.2f}")
    
    elif args.command == "demo":
        print("🧬 Evolution Demo\n")
        
        print("   Create population:")
        pop = create_population(3, 8)
        for i, g in enumerate(pop):
            print(f"      {i}: {''.join(map(str, g))}")
        
        print("\n   Crossover:")
        child = crossover(pop[0], pop[1])
        print(f"      P1: {''.join(map(str, pop[0]))}")
        print(f"      P2: {''.join(map(str, pop[1]))}")
        print(f"      C:  {''.join(map(str, child))}")
        
        print("\n   Mutation:")
        mutated = mutate(child, 0.3)
        print(f"      Before: {''.join(map(str, child))}")
        print(f"      After:  {''.join(map(str, mutated))}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
