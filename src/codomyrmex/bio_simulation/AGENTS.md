# Bio-Simulation Agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Simulated biological entities and research assistant agents.

## Agents

### `SimulatedAnt`

- **Role**: Operates within the bio-simulation.
- **Capabilities**: `move`, `deposit_pheromone`, `pickup_item`.

### `MyrmecologistAgent`

- **Role**: Designs and observes experiments.
- **Capabilities**: `configure_simulation`, `analyze_results`.

## Tools

| Tool | Agent | Description |
| :--- | :--- | :--- |
| `step_simulation` | Myrmecologist | Advance time |
| `sample_population` | Myrmecologist | Get census data |

## Integration

These agents interact via the `bio_simulation` environment API.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
