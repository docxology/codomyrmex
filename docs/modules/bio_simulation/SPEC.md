# Bio Simulation — Functional Specification

**Module**: `codomyrmex.bio_simulation`  
**Version**: v0.1.7  
**Status**: Active

## 1. Overview

Bio-Simulation Module for Codomyrmex.

Provides ant colony simulation with pheromone-based foraging and
genomics / genetic algorithm integration.

## 2. Architecture

### Source Files

| File | Purpose |
|------|--------|
| `colony.py` | Simulated biological agent. |
| `visualization.py` | Renders a scatter plot of current ant positions. |

### Submodule Structure

- `ant_colony/` — Ant Colony
- `genomics/` — Genomics

## 3. Dependencies

No internal Codomyrmex dependencies.

## 4. Public API

### Exports (`__all__`)

- `Ant`
- `AntState`
- `Colony`
- `Environment`
- `Genome`
- `Population`

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k bio_simulation -v
```

All tests follow the Zero-Mock policy.

## 6. References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/bio_simulation/)
