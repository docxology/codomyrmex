# Bio-Simulation Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

High-fidelity biological simulation engine. Provides digital twins of ant colonies for emergent behavior study, individual agent simulation, pheromone-based communication, and genomics pipeline integration.

## Features

- **Colony Simulation**: Discrete-time simulation of large ant populations.
- **Agent State Machine**: High-fidelity behavioral states (FORAGING, RETURNING, RESTING).
- **Spatial Environment**: Grid-based world with resources, obstacles, and pheromone dynamics.
- **Genomics**: Trait-based genetic representation with mutation and crossover for evolutionary studies.
- **MCP Tools**: Easy-to-use Model Context Protocol integration for controlling and analyzing simulations.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Run biological models to explore emergent behavior | Direct Python import, `bio_simulation_run_colony` |
| **BUILD** | Configure colony simulations and genomics parameters | Direct Python import |
| **VERIFY** | Validate simulation outputs against expected distributions | Direct Python import, `bio_simulation_evolve_population` |

## Installation

```bash
uv add codomyrmex
```

## Quick Start

```python
from codomyrmex.bio_simulation import Colony, Ant, Environment, Genome, Population

# Create and run an ant colony simulation
colony = Colony(population=1000)
colony.step(hours=24)

# Access individual agent states
for ant in colony.ants[:10]:
    print(f"Ant {ant.id}: state={ant.state}, energy={ant.energy:.2f}")

# Population genomics
population = Population(genomes=[ant.genome for ant in colony.ants])
traits = population.trait_distribution()
```

## Architecture

```
bio_simulation/
├── __init__.py       # Exports: Colony, Ant, AntState, Environment, Genome, Population
├── ant_colony/       # Eusocial behavior logic, pheromone signaling
│   ├── colony.py     # Colony lifecycle and population dynamics
│   ├── ant.py        # Individual agent behavior and state machine
│   └── environment.py # Spatial environment and resource management
├── genomics/         # Gene expression and trait mapping
│   ├── genome.py     # Genome representation
│   └── population.py # Population genetics
└── tests/            # Unit tests (Zero-Mock policy)
```

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md)
