# Bio Simulation

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Bio Simulation module provides ant colony simulation with pheromone-based foraging and genomics/genetic algorithm integration. It models colony behavior with individual ant agents, environment grids with pheromone trails, and population-based genetic optimization. This module serves as both a research tool and a metaphorical foundation for the codomyrmex (ant-inspired) platform architecture.

## Architecture Overview

```
bio_simulation/
├── __init__.py              # Public API (Ant, Colony, Environment, Genome, Population)
├── ant_colony/
│   ├── ant.py               # Ant agent with state machine (AntState enum)
│   ├── colony.py            # Colony orchestrator managing ant populations
│   └── environment.py       # Grid environment with pheromone diffusion
└── genomics/
    ├── genome.py            # Genome representation for genetic algorithms
    └── population.py        # Population-based evolutionary optimization
```

## Key Classes and Functions

**`Ant`** -- Individual ant agent with state machine (SEARCHING, CARRYING, RETURNING).

**`AntState`** -- Enum defining ant behavioral states.

**`Colony`** -- Colony orchestrator managing ant populations and simulation steps.

**`Environment`** -- Grid-based environment with pheromone diffusion and evaporation.

**`Genome`** -- Genome representation for genetic algorithm optimization.

**`Population`** -- Population-based evolutionary optimization with selection, crossover, and mutation.

## Usage Examples

```python
from codomyrmex.bio_simulation import Colony, Environment

env = Environment(width=100, height=100)
colony = Colony(environment=env, num_ants=50)
for step in range(1000):
    colony.step()
```

## Related Modules

- [`simulation`](../simulation/readme.md) -- General simulation framework
- [`evolutionary_ai`](../evolutionary_ai/readme.md) -- Evolutionary algorithms

## Navigation

- **Source**: [src/codomyrmex/bio_simulation/](../../../../src/codomyrmex/bio_simulation/)
- **Parent**: [All Modules](../README.md)
