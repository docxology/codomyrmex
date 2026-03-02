# Contagion -- Technical Specification

**Version**: v1.0.0 | **Status**: Experimental | **Last Updated**: March 2026

## Overview

Models information spread using compartmental epidemic models (SIR, SIS, SEIR) adapted for memetic propagation. Provides cascade detection from event streams and simulation runners for contagion scenarios across configurable network topologies.

## Architecture

Compartmental mean-field simulation with cascade detection. Epidemic models partition the population into compartments (Susceptible, Infected, Recovered) and advance via discrete time steps using infection/recovery rate parameters. `CascadeDetector` classifies real event streams by velocity and size heuristics.

## Key Classes

### `SIRModel`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `population_size: int, beta: float, gamma: float` | `None` | Set population size, infection rate, recovery rate |
| `simulate` | `steps: int, initial_infected: int` | `PropagationTrace` | Run mean-field SIR simulation for given steps |

### `SISModel`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `simulate` | `steps: int, initial_infected: int` | `PropagationTrace` | SIS loop (no immunity); recovered return to susceptible |

### `SEIRModel` (extends `SIRModel`)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `population_size, beta, sigma, gamma` | `None` | Adds incubation rate (sigma) for Exposed compartment |
| `simulate` | `steps: int, initial_infected: int` | `PropagationTrace` | SEIR simulation with Exposed incubation stage |

### `CascadeDetector`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `detect` | `events: list[dict]` | `list[Cascade]` | Group events by meme_id, classify by velocity/size |

### Data Models

| Class | Fields | Purpose |
|-------|--------|---------|
| `PropagationTrace` | `time_steps, infected_counts, susceptible_counts, recovered_counts, seed_meme_id` | Simulation output with `peak_infected()` and `total_infected()` |
| `Cascade` | `seed_id, size, depth, duration, velocity, cascade_type, participants` | Detected cascade event |
| `CascadeType` | `VIRAL, ORGANIC, MANUFACTURED, DAMPENED` | Cascade classification enum |
| `ContagionModel` | `infection_rate, recovery_rate, network_size` | Configuration dataclass for simulations |
| `ResonanceMap` | `nodes, clusters` | Network resonance/amplification potential |

### Module Functions

| Function | Parameters | Returns | Description |
|----------|-----------|---------|-------------|
| `run_simulation` | `model_config: ContagionModel, steps, seed_nodes, topology` | `PropagationTrace` | High-level runner wrapping SIRModel |
| `detect_cascades` | `events: list[dict]` | `list[Cascade]` | Convenience wrapper for `CascadeDetector.detect` |

## Dependencies

- **Internal**: None (self-contained within `meme` package)
- **External**: Standard library only (`dataclasses`, `enum`)

## Constraints

- Mean-field approximation assumes well-mixed population (no network structure).
- `topology` parameter in `run_simulation` is accepted but not yet used; all simulations use mean-field.
- Cascade classification uses fixed velocity threshold (>10.0 = VIRAL, <5 nodes = DAMPENED).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Simulations terminate early when infected count reaches zero (extinction).
- Division by zero prevented in velocity calculation (fallback to `size` when `duration == 0`).
