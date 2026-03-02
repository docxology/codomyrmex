# Agent Guidelines - Simulation

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Step-based simulation engine for agent-based modeling and system dynamics.

## Key Classes

- **Simulator** -- Core simulation engine with run/step/results lifecycle
- **SimulationConfig** -- Configuration dataclass (name, max_steps, seed, params)

## Agent Instructions

1. **Configure before running** -- Create a `SimulationConfig` with appropriate parameters before instantiating `Simulator`
2. **Set seeds for reproducibility** -- Always provide a `seed` value when deterministic results are needed
3. **Use step() for control** -- Prefer `step()` in a loop when you need per-step inspection or early termination
4. **Check results** -- Call `get_results()` after completion to retrieve simulation outcome data
5. **Handle exceptions** -- Wrap `run()` calls in try/except; simulation errors are logged and re-raised

## Common Patterns

```python
from codomyrmex.simulation import Simulator, SimulationConfig

# Full run with configuration
config = SimulationConfig(
    name="agent_experiment",
    max_steps=1000,
    seed=42,
    params={"decay_rate": 0.95}
)
sim = Simulator(config)
results = sim.run()
print(f"Completed: {results['steps_completed']} steps")

# Step-by-step with inspection
sim = Simulator(SimulationConfig(max_steps=100))
for i in range(50):
    sim.step()
    sim.step_count += 1  # tracked internally by run()
results = sim.get_results()

# Default configuration
sim = Simulator()
results = sim.run()
assert results["status"] == "completed"
```

## Testing Patterns

```python
from codomyrmex.simulation import Simulator, SimulationConfig

# Verify default initialization
sim = Simulator()
assert sim.config.name == "default_simulation"
assert sim.config.max_steps == 1000
assert sim.step_count == 0

# Verify configuration
config = SimulationConfig(name="test", max_steps=10, seed=42)
sim = Simulator(config)
results = sim.run()
assert results["steps_completed"] == 10
assert results["status"] == "completed"

# Verify get_results structure
results = sim.get_results()
assert "steps_completed" in results
assert "config" in results
assert "status" in results
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, interface design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, output validation | OBSERVED |

### Engineer Agent
**Use Cases**: Runs system and environment simulations via `Simulator` and `SimulationConfig`. Configures step-based runs, sets seeds for reproducibility, and retrieves structured results from simulation outcomes.

### Architect Agent
**Use Cases**: Designs simulation models and scenarios, reviews step-based engine architecture, evaluates configuration parameter schemas, and plans integration with agent-based modeling workflows.

### QATester Agent
**Use Cases**: Validates simulation output accuracy, verifies deterministic results with seeded runs, confirms step count tracking, and tests early termination and error handling paths.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
