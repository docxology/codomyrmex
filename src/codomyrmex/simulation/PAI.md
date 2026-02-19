# Personal AI Infrastructure -- Simulation Module

**Version**: v0.1.7 | **Status**: Alpha | **Last Updated**: February 2026

## Overview

The Simulation module provides a step-based simulation engine for agent-based modeling and system dynamics. This is a **Core Layer** module.

## PAI Capabilities

### Simulation Execution

Run configurable simulations with structured result collection:

```python
from codomyrmex.simulation import Simulator, SimulationConfig

config = SimulationConfig(
    name="pai_experiment",
    max_steps=500,
    seed=42,
    params={"agent_count": 10, "environment_size": 100}
)
sim = Simulator(config)
results = sim.run()
# results: {"steps_completed": 500, "config": "pai_experiment", "status": "completed"}
```

### Step-by-Step Control

For fine-grained execution where PAI agents need per-step observation:

```python
sim = Simulator(SimulationConfig(max_steps=100))
for i in range(100):
    sim.step()
results = sim.get_results()
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Simulator` | Class | Core simulation engine with run/step/results lifecycle |
| `SimulationConfig` | Dataclass | Configuration: name, max_steps, seed, params |

## PAI Algorithm Phase Mapping

| Phase | Simulation Module Contribution |
|-------|-------------------------------|
| **EXECUTE** | `Simulator.run()` and `Simulator.step()` execute simulation workloads |
| **OBSERVE** | `Simulator.get_results()` provides structured output for observation |
| **VERIFY** | Result dictionaries enable post-execution verification of simulation outcomes |

## Architecture Role

**Core Layer** -- Part of the codomyrmex layered architecture. Depends on `logging_monitoring` (Foundation Layer) for structured logging.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) -- Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) -- Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
