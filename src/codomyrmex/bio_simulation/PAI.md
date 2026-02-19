# Personal AI Infrastructure -- Bio-Simulation Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Bio-Simulation module provides a **digital twin of an ant colony** for studying emergent behavior, foraging dynamics, and population-level phenomena. It models individual agents with state machines (foraging, returning, defending, idle) and energy-based lifecycle management, enabling observation of collective intelligence patterns.

## PAI Capabilities

### Colony Simulation

Run discrete-step biological simulations with configurable population sizes:

```python
from codomyrmex.bio_simulation import Colony

colony = Colony(population_size=1000)
for _ in range(100):
    colony.step()

census = colony.get_census()
print(census)  # {AntState.FORAGING: 250, AntState.IDLE: 750, ...}
```

### Visual State Inspection

Render real-time scatter plots of ant spatial distribution:

```python
from codomyrmex.bio_simulation.visualization import render_colony_state

plot = render_colony_state(colony)
# Returns a ScatterPlot of ant x/y positions
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Colony` | Class | Ant colony simulation environment with tick-based stepping |
| `Ant` | Dataclass | Individual biological agent with state, energy, and position |
| `AntState` | Enum | Behavioral states: FORAGING, RETURNING, DEFENDING, IDLE |
| `render_colony_state()` | Function | Scatter plot visualization of colony spatial state |

## PAI Algorithm Phase Mapping

| Phase | Bio-Simulation Contribution |
|-------|---------------------------|
| **OBSERVE** | Colony simulation models biological phenomena for empirical observation of emergent behavior |
| **PLAN** | Census data and population dynamics inform resource allocation strategies |
| **EXECUTE** | `colony.step()` drives simulation forward for hypothesis testing |
| **VERIFY** | `get_census()` and scatter plots verify expected population distributions |
| **LEARN** | Emergent patterns from simulation runs provide insights into collective intelligence |

## Architecture Role

**Application Layer** -- Domain-specific simulation module. Depends on the `visualization` module for rendering colony state. Has no upward dependencies from other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
