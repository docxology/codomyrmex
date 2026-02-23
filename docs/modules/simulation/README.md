# Simulation Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Simulation module provides a general-purpose discrete event simulation engine. It supports configurable simulation parameters, event scheduling, time-stepping, and result collection for modeling complex systems.

## Installation

```bash
uv add codomyrmex
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `Simulator` | Class | Core simulation engine |
| `SimulationConfig` | Class | Simulation parameter configuration |

## Quick Start

```python
from codomyrmex.simulation import Simulator, SimulationConfig

config = SimulationConfig(
    duration=100,
    time_step=0.1,
    seed=42
)
sim = Simulator(config)
results = sim.run()
```

## Architecture

```
simulation/
├── __init__.py     # Exports: Simulator, SimulationConfig
├── simulator.py    # Core simulation engine
└── tests/          # Zero-Mock tests
```

## Navigation

- [SPEC.md](SPEC.md) | [AGENTS.md](AGENTS.md) | [PAI.md](PAI.md) | [Parent](../README.md)
