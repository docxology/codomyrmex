# Bio Simulation Module — Agent Coordination

## Purpose

Bio-Simulation Module for Codomyrmex.

Provides ant colony simulation with pheromone-based foraging and
genomics / genetic algorithm integration.

## Key Capabilities

- **`Colony`** — Ant colony simulation environment
- **`Ant`** — Individual agent in simulation
- **`PheromoneGrid`** — Environmental signaling layer
- `ant_colony/` — Eusocial behavior logic
- `genomics/` — Gene expression and trait mapping

## Agent Usage Patterns

```python
from codomyrmex.bio_simulation import Colony

colony = Colony(population=1000)
colony.step(hours=24)
```

## Key Components

| Export | Type |
|--------|------|
| `Ant` | Public API |
| `AntState` | Public API |
| `Colony` | Public API |
| `Environment` | Public API |
| `Genome` | Public API |
| `Population` | Public API |

## Source Files

| File | Description |
|------|-------------|
| `colony.py` | Simulated biological agent. |
| `visualization.py` | Renders a scatter plot of current ant positions. |

## Submodules

- `ant_colony/` — Ant Colony
- `genomics/` — Genomics

## Integration Points

- **Source**: [src/codomyrmex/bio_simulation/](../../../src/codomyrmex/bio_simulation/)
- **Spec**: [SPEC.md](SPEC.md)
- **PAI**: [PAI.md](PAI.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k bio_simulation -v
```

- Always use real, functional tests — no mocks (Zero-Mock policy)
- Verify all changes pass existing tests before submitting
