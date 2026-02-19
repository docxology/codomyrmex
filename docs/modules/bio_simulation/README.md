# Bio-Simulation Module Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

High-fidelity biological simulation engine providing digital twins of ant colonies for emergent behavior study and integration with genomics pipelines.

## Installation

```bash
uv pip install codomyrmex
```

## Key Features

- **`Colony`** -- Ant colony simulation environment with population dynamics.
- **`Ant`** -- Individual agent in simulation with behavioral rules.
- **`PheromoneGrid`** -- Environmental signaling layer for stigmergic communication.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `ant_colony` | Eusocial behavior logic |
| `genomics` | Gene expression and trait mapping |

## Quick Start

```python
from codomyrmex.bio_simulation import Colony

colony = Colony(population=1000)
colony.step(hours=24)
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Colony` | Ant colony simulation environment |
| `Ant` | Individual agent in simulation |
| `PheromoneGrid` | Environmental signaling layer |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k bio_simulation -v
```

## Navigation

- **Source**: [src/codomyrmex/bio_simulation/](../../../src/codomyrmex/bio_simulation/)
- **API Spec**: [API_SPECIFICATION.md](../../../src/codomyrmex/bio_simulation/API_SPECIFICATION.md)
- **MCP Spec**: [MCP_TOOL_SPECIFICATION.md](../../../src/codomyrmex/bio_simulation/MCP_TOOL_SPECIFICATION.md)
- **Parent**: [Modules](../README.md)
