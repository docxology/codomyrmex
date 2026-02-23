# simulation - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `simulation` module provides the core simulation engine for Codomyrmex. It enables step-based simulation execution with configurable parameters, supporting agent-based modeling and system dynamics use cases. The module manages simulation lifecycle (initialization, stepping, completion) and result collection.

## Design Principles

### Modularity

- **Decoupled Engine**: The `Simulator` class is independent of specific simulation models; logic is injected via subclassing or the `params` dictionary.
- **Configurable**: `SimulationConfig` dataclass separates configuration from execution.

### Internal Coherence

- **Structured Logging**: All simulation events (init, start, step errors, completion) are logged via `logging_monitoring`.
- **Consistent Results**: `get_results()` returns a standardized dictionary format regardless of simulation type.

### Parsimony

- **Minimal Interface**: Three public methods (`run()`, `step()`, `get_results()`) and one configuration class.
- **Sensible Defaults**: Works out of the box with `Simulator()` and no configuration.

### Functionality

- **Step Loop**: `run()` executes `step()` in a loop until `max_steps` or early termination.
- **Reproducibility**: Optional `seed` parameter for deterministic simulation runs.
- **Error Recovery**: Exceptions during `step()` are logged with step context and re-raised; `_running` state is always cleaned up via `finally`.

## Architecture

```mermaid
graph TD
    subgraph "Configuration"
        Config[SimulationConfig]
    end

    subgraph "Core Engine"
        Sim[Simulator]
        Run[run()]
        Step[step()]
        Results[get_results()]
    end

    subgraph "Infrastructure"
        Logger[logging_monitoring]
    end

    Config --> Sim
    Sim --> Run
    Run --> Step
    Run --> Results
    Sim --> Logger
```

## Functional Requirements

### Core Capabilities

1. **Simulation Execution**: Run simulations to completion via `run()` or incrementally via `step()`.
2. **Configuration**: Accept simulation parameters through `SimulationConfig` (name, max_steps, seed, params).
3. **Result Collection**: Return structured results including steps completed, configuration name, and status.
4. **Lifecycle Management**: Track running state and step count; clean up on completion or failure.

### Quality Standards

- Type hints on all public methods and configuration fields
- Structured logging for all lifecycle events
- Exception safety with proper state cleanup

## Interface Contracts

### Public API

- `Simulator(config: SimulationConfig | None = None)` - Initialize the simulator engine.
- `Simulator.run() -> dict[str, Any]` - Execute the full simulation loop.
- `Simulator.step() -> None` - Execute a single simulation step.
- `Simulator.get_results() -> dict[str, Any]` - Return current simulation results.
- `SimulationConfig(name, max_steps, seed, params)` - Configuration dataclass.

### Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (structured logging via `get_logger`).

## Implementation Guidelines

### Usage Patterns

1. Create a `SimulationConfig` with desired parameters
2. Instantiate `Simulator` with the config
3. Call `run()` for full execution or `step()` for incremental control
4. Retrieve results via `get_results()` or the return value of `run()`

### Extension Points

- Subclass `Simulator` and override `step()` to implement custom simulation logic
- Use `params` dictionary in `SimulationConfig` for model-specific parameters

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Package Root**: [../README.md](../README.md)
- **Package SPEC**: [../SPEC.md](../SPEC.md)
