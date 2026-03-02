"""Orchestrator script for Bio-Simulation.

Demonstrates the capabilities of the improved bio_simulation module:
- Colony creation and environmental configuration.
- Advancing simulation time (step method).
- Collecting and displaying simulation statistics.
- Population genomics and trait distributions.
"""

from codomyrmex.bio_simulation import Colony, Population


def main():
    print("--- Bio-Simulation Orchestrator ---")
    
    # 1. Configure the Colony
    # Using a smaller population for a quick demonstration
    colony_config = {
        "width": 150,
        "height": 150,
        "pheromone_decay": 0.08,
    }
    colony = Colony(population=500, seed=42, environment=colony_config)
    
    # Add some food sources
    colony.add_food_source((20, 20), 500.0)
    colony.add_food_source((130, 130), 500.0)
    
    print(f"Colony initialized with {colony.population_alive} ants.")
    print(f"Initial stats: {colony.stats()}")
    
    # 2. Advance the simulation (e.g., 2 hours)
    print("\nAdvancing simulation by 2 hours...")
    summary = colony.step(hours=2)
    
    print(f"Step summary: {summary}")
    print(f"Stats after 2 hours: {colony.stats()}")
    
    # 3. Population Genomics
    print("\n--- Population Genomics ---")
    
    # Collect genomes from current population
    genomes = [ant.genome for ant in colony.ants if ant.is_alive() and ant.genome]
    population = Population(genomes=genomes)
    
    # Get trait distribution
    traits = population.trait_distribution()
    print("Trait distribution of living ants:")
    for trait, stats in traits.items():
        print(f"  {trait}: mean={stats['mean']:.3f}, std={stats['std']:.3f}")
        
    # 4. Evolve the population (independent of colony for this example)
    print("\nEvolving population for 10 generations...")
    population.evolve(generations=10)
    final_traits = population.trait_distribution()
    print("Trait distribution after 10 generations of evolution:")
    for trait, stats in final_traits.items():
        print(f"  {trait}: mean={stats['mean']:.3f}, std={stats['std']:.3f}")

    print("\n--- Simulation Complete ---")


if __name__ == "__main__":
    main()
