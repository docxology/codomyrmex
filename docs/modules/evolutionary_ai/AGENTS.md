# Evolutionary AI Module — Agent Coordination

## Purpose

Evolutionary AI module for Codomyrmex.

## Key Capabilities

- **Genome**: A genome representing an individual's genetic material.
- **Population**: A population of individuals for evolutionary algorithms.
- `crossover()`: Perform single-point crossover between two genomes.
- `mutate()`: Apply mutation to a genome.
- `tournament_selection()`: Select an individual using tournament selection.

## Agent Usage Patterns

```python
from codomyrmex.evolutionary_ai import Genome

# Agent initializes evolutionary ai
instance = Genome()
```

## Integration Points

- **Source**: [src/codomyrmex/evolutionary_ai/](../../../src/codomyrmex/evolutionary_ai/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k evolutionary_ai -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
