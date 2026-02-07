# FPF (Filesystem Processing Framework) Module — Agent Coordination

## Purpose

First Principles Framework (FPF) module.

## Key Capabilities

- **FPFClient**: High-level client for working with FPF specifications.
- `load_from_file()`: Load and parse FPF specification from a local file.
- `fetch_and_load()`: Fetch latest FPF specification from GitHub and load it.
- `search()`: Search for patterns.

## Agent Usage Patterns

```python
from codomyrmex.fpf import FPFClient

# Agent initializes fpf (filesystem processing framework)
instance = FPFClient()
```

## Integration Points

- **Source**: [src/codomyrmex/fpf/](../../../src/codomyrmex/fpf/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Key Components

- **`FPFClient`** — High-level client for working with FPF specifications.

### Submodules

- `constraints` — Constraints
- `models` — Models
- `optimization` — Optimization
- `reasoning` — Reasoning

