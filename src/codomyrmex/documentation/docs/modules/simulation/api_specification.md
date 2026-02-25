# Simulation - API Specification

**Version**: v0.1.7 | **Status**: Alpha | **Last Updated**: February 2026

## Overview

The Simulation module provides a step-based simulation engine. It exposes two primary constructs: the `SimulationConfig` dataclass for configuration and the `Simulator` class for execution.

## Core API

### Configuration

```python
from codomyrmex.simulation import SimulationConfig

config = SimulationConfig(
    name="my_simulation",
    max_steps=500,
    seed=42,
    params={"learning_rate": 0.01, "population": 100}
)
```

### Simulation Execution

```python
from codomyrmex.simulation import Simulator, SimulationConfig

# Full run
config = SimulationConfig(name="experiment_1", max_steps=1000, seed=42)
sim = Simulator(config)
results = sim.run()

# Step-by-step
sim = Simulator()
for _ in range(10):
    sim.step()
results = sim.get_results()
```

## Endpoints / Functions / Interfaces

### Class: `SimulationConfig`

- **Description**: Dataclass that holds all configuration parameters for a simulation run.
- **Method**: N/A (Python dataclass)
- **Fields**:
    - `name` (str): Human-readable simulation name. Default: `"default_simulation"`.
    - `max_steps` (int): Maximum number of steps before the simulation terminates. Default: `1000`.
    - `seed` (int | None): Random seed for reproducibility. Default: `None`.
    - `params` (dict[str, Any]): Arbitrary key-value parameters for model-specific configuration. Default: `{}`.

### Class: `Simulator`

- **Description**: Core simulation engine that manages lifecycle, step execution, and result collection.
- **Method**: N/A (Python class)
- **Parameters/Arguments** (constructor):
    - `config` (SimulationConfig | None): Configuration for the simulation. If `None`, uses default `SimulationConfig()`.

### Function: `Simulator.run()`

- **Description**: Executes the simulation loop, calling `step()` repeatedly until `max_steps` is reached or the simulation is stopped. Returns the final results.
- **Method**: N/A (Instance method)
- **Parameters/Arguments**: None
- **Returns/Response**:
    - `dict[str, Any]`: Result dictionary with the following structure:
        ```json
        {
          "steps_completed": 1000,
          "config": "my_simulation",
          "status": "completed"
        }
        ```
- **Error Handling**: Exceptions raised during `step()` are logged with step context and re-raised. The `_running` state is always reset via `finally`.

### Function: `Simulator.step()`

- **Description**: Executes a single simulation step. Override this method in subclasses to implement custom simulation logic.
- **Method**: N/A (Instance method)
- **Parameters/Arguments**: None
- **Returns/Response**: None

### Function: `Simulator.get_results()`

- **Description**: Returns the current simulation results as a structured dictionary.
- **Method**: N/A (Instance method)
- **Parameters/Arguments**: None
- **Returns/Response**:
    - `dict[str, Any]`: Result dictionary containing:
        - `steps_completed` (int): Number of steps executed so far.
        - `config` (str): Name of the simulation configuration.
        - `status` (str): `"completed"` if the simulation has finished, `"running"` if still active.

## Data Models

### Model: `SimulationConfig`

- `name` (str): Simulation name identifier.
- `max_steps` (int): Upper bound on simulation steps.
- `seed` (int | None): Optional random seed.
- `params` (dict[str, Any]): Arbitrary model parameters.

### Model: Result Dictionary

- `steps_completed` (int): Total steps executed.
- `config` (str): Configuration name.
- `status` (str): One of `"completed"` or `"running"`.

## Authentication & Authorization

Not applicable for this internal simulation module.

## Rate Limiting

Not applicable for this internal simulation module.

## Versioning

This module follows the general versioning strategy of the Codomyrmex project. API stability is aimed for, with changes documented in future CHANGELOG entries.

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Repository Root**: [../../../README.md](../../../README.md)
