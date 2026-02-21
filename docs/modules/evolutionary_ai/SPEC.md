# Evolutionary AI — Functional Specification

**Module**: `codomyrmex.evolutionary_ai`  
**Version**: v1.0.0  
**Status**: Active

## 1. Overview

Evolutionary AI module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `Genome` | Class | A genome representing an individual's genetic material. |
| `Population` | Class | A population of individuals for evolutionary algorithms. |
| `crossover()` | Function | Perform single-point crossover between two genomes. |
| `mutate()` | Function | Apply mutation to a genome. |
| `tournament_selection()` | Function | Select an individual using tournament selection. |
| `random()` | Function | Create a random genome. |
| `copy()` | Function | Create a copy of this genome. |

### Submodule Structure

- `fitness/` — Fitness evaluation submodule.
- `genome/` — Genome representation submodule.
- `operators/` — Genetic operators for evolutionary AI.
- `population/` — Population management submodule.
- `selection/` — Selection methods submodule.

## 3. Dependencies

See `src/codomyrmex/evolutionary_ai/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.evolutionary_ai import Genome, Population
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k evolutionary_ai -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/evolutionary_ai/)
