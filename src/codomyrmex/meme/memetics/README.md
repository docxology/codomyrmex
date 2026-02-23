# Memetics Submodule

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**The Core Physics of Ideas**

The `codomyrmex.meme.memetics` submodule provides the foundational classes and logic for the entire meme module. It treats memes as discrete units of cultural transmission, analogous to genes in biology, subject to variation, selection, and retention.

## Key Components

### 1. Data Models (`models.py`)

* **`Meme`**: The atomic unit. Contains content, type (Belief, Norm, Strategy, etc.), and fitness scores (Fidelity, Fecundity, Longevity).
* **`Memeplex`**: A co-adapted complex of memes (e.g., a religion, an ideology).
* **`MemeticCode`**: Represents the encoded genome of a meme/memeplex.
* **`FitnessMap`**: A mapping of memeplex IDs to their calculated fitness values.

### 2. Genetic Operators (`mutation.py`)

* **`semantic_drift`**: Evolves a meme's content by substituting synonyms or altering phrasing while retaining core meaning.
* **`recombine`**: Merges two memes or memeplexes to create offspring.
* **`splice`**: Inserts a segment of one meme into another.
* **`batch_mutate`**: Applies mutation operators to an entire population.

### 3. Fitness Functions (`fitness.py`)

* **`virality_score`**: Estimates potential for spread based on content features (emotional valence, simplicity).
* **`robustness_score`**: Measures resistance to mutation or counter-narratives.
* **`population_fitness_stats`**: Aggregates fitness metrics for a whole population.

### 4. Memetic Engine (`engine.py`)

* **`MemeticEngine`**: The central orchestrator.
  * `dissect(text)`: Breaks text into memes.
  * `synthesize(memes)`: Reassembles memes into text.
  * `evolve(population)`: Runs a genetic algorithm for N generations.
  * `select(population)`: Chooses the fittest memes for reproduction.

## Usage

```python
from codomyrmex.meme.memetics import MemeticEngine, Meme

engine = MemeticEngine()

# Create initial population
population = [
    Meme("The sky is blue.", fitness=0.5),
    Meme("The sky is green.", fitness=0.1),
    # ...
]

# Evolve for 10 generations
evolved_pop = engine.evolve(population, generations=10)

# Get best meme
best = max(evolved_pop, key=lambda m: m.fitness)
print(f"Winner: {best.content}")
```
