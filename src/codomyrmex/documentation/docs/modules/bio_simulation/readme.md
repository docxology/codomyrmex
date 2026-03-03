# Bio-Simulation Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

High-fidelity biological simulation engine. Provides digital twins of ant colonies for emergent behavior study, individual agent simulation, pheromone-based communication, and genomics pipeline integration.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **THINK** | Run biological models to explore emergent behavior | Direct Python import |
| **BUILD** | Configure colony simulations and genomics parameters | Direct Python import |
| **VERIFY** | Validate simulation outputs against expected distributions | Direct Python import |

PAI agents access this module via direct Python import through the MCP bridge. The Engineer agent uses it during BUILD phase to configure simulation parameters, and during THINK phase to run colony models and analyze emergent patterns.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

### Ant Colony Simulation

| Export | Type | Purpose |
|--------|------|---------|
| `Colony` | Class | Ant colony simulation environment with population dynamics |
| `Ant` | Class | Individual agent in simulation with state machine behavior |
| `AntState` | Enum | Agent state: FORAGING, RETURNING, RESTING, etc. |
| `Environment` | Class | Spatial environment with resources and obstacles |

### Genomics

| Export | Type | Purpose |
|--------|------|---------|
| `Genome` | Class | Gene sequence representation with expression modeling |
| `Population` | Class | Population genetics simulation and trait mapping |

## Quick Start

```python
from codomyrmex.bio_simulation import Colony, Ant, Environment, Genome, Population

# Create and run an ant colony simulation
colony = Colony(population=1000)
colony.step(hours=24)

# Access individual agent states
for ant in colony.ants[:10]:
    print(f"Ant {ant.id}: state={ant.state}, food={ant.carrying}")

# Population genomics
population = Population(genomes=[Genome.random() for _ in range(100)])
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

- **Extended Docs**: [docs/modules/bio_simulation/](../../../docs/modules/bio_simulation/)
- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
