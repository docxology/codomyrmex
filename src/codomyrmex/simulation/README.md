# Simulation Module

**Version**: v0.1.7 | **Status**: Alpha

Core simulation engine for agent-based modeling and system dynamics simulations within Codomyrmex. Provides a step-based simulation loop with configurable parameters, seeding, and result collection.

## Key Exports

### Classes

- **`Simulator`** -- Core simulator engine. Manages the simulation lifecycle including initialization, step execution, and result collection. Accepts an optional `SimulationConfig` for customization.
- **`SimulationConfig`** -- Dataclass for configuring a simulation run. Controls simulation name, maximum steps, random seed, and arbitrary parameter dictionaries.

## Quick Start

```python
from codomyrmex.simulation import Simulator, SimulationConfig

# Run with default configuration
sim = Simulator()
results = sim.run()

# Run with custom configuration
config = SimulationConfig(
    name="my_experiment",
    max_steps=500,
    seed=42,
    params={"learning_rate": 0.01, "population": 100}
)
sim = Simulator(config)
results = sim.run()

# Step-by-step execution
sim = Simulator()
for i in range(10):
    sim.step()
results = sim.get_results()
```

## Directory Contents

- `__init__.py` - Package exports: `Simulator`, `SimulationConfig`
- `simulator.py` - Core simulation logic: `Simulator` class and `SimulationConfig` dataclass

## Dependencies

- `logging_monitoring` - Structured logging for simulation events

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k simulation -v
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md) | [API_SPECIFICATION](API_SPECIFICATION.md) | [MCP_TOOL_SPECIFICATION](MCP_TOOL_SPECIFICATION.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
