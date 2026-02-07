# Feature Flags Module — Agent Coordination

## Purpose

Feature Flags module for Codomyrmex.

## Key Capabilities

- Feature Flags operations and management

## Agent Usage Patterns

```python
from codomyrmex.feature_flags import *

# Agent uses feature flags capabilities
```

## Integration Points

- **Source**: [src/codomyrmex/feature_flags/](../../../src/codomyrmex/feature_flags/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)


## Key Components

- **`VariantType`** — Experiment variant types.
- **`Variant`** — An experiment variant.
- **`Experiment`** — An A/B test experiment.
- **`Assignment`** — User's experiment assignment.
- **`ExperimentEvent`** — An experiment analytics event.

### Submodules

- `core` — Core
- `evaluation` — Evaluation
- `rollout` — Rollout
- `storage` — Storage
- `strategies` — Strategies

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k feature_flags -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
