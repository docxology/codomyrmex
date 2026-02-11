# Bio-Simulation Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

High-fidelity biological simulation engine. Provides digital twins of ant colonies for emergent behavior study and integrates with genomics pipelines.

## Installation

```bash
uv pip install codomyrmex
```

## Key Exports

### Simulation

- **`Colony`** — Ant colony simulation environment
- **`Ant`** — Individual agent in simulation
- **`PheromoneGrid`** — Environmental signaling layer

### Submodules

- `ant_colony/` — Eusocial behavior logic
- `genomics/` — Gene expression and trait mapping

## Quick Start

```python
from codomyrmex.bio_simulation import Colony

colony = Colony(population=1000)
colony.step(hours=24)
```

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [Parent](../README.md)
