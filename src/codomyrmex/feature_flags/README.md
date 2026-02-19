# Feature Flags Module

**Version**: v0.1.7 | **Status**: Active

Feature flag management with evaluation strategies and gradual rollout.


## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Classes
- **`VariantType`** — Experiment variant types.
- **`Variant`** — An experiment variant.
- **`Experiment`** — An A/B test experiment.
- **`Assignment`** — User's experiment assignment.
- **`ExperimentEvent`** — An experiment analytics event.
- **`ExperimentManager`** — Manage A/B test experiments.

### Submodules
- **`core/`** — Core flag management submodule.
- **`evaluation/`** — Flag evaluation submodule.
- **`rollout/`** — Gradual rollout submodule.
- **`storage/`** — Flag storage submodule.
- **`strategies/`** — Feature flag evaluation strategies.

## Quick Start

```python
from codomyrmex.feature_flags import strategies, storage, evaluation, rollout

# Using FeatureManager (if available)
from codomyrmex.feature_flags import FeatureManager

manager = FeatureManager()

# Define flags
manager.define("dark_mode", default=False)
manager.define("new_checkout", default=False, rollout_percent=25)

# Check flags
if manager.is_enabled("dark_mode", user_id="user-123"):
    show_dark_mode()

# Gradual rollout
if manager.is_enabled("new_checkout", user_id="user-123"):
    render_new_checkout()
else:
    render_old_checkout()

# Override for testing
with manager.override("experimental_feature", True):
    run_experiment()
```

## Submodules

| Module | Description |
|--------|-------------|
| `strategies` | Evaluation strategies (percentage, user segment, etc.) |
| `storage` | Flag storage backends (memory, file, redis) |
| `evaluation` | Flag evaluation logic |
| `rollout` | Gradual rollout management |
| `core` | Core flag manager |

## Exports

| Class | Description |
|-------|-------------|
| `FeatureManager` | Main flag manager |


## Documentation

- [Module Documentation](../../../docs/modules/feature_flags/README.md)
- [Agent Guide](../../../docs/modules/feature_flags/AGENTS.md)
- [Specification](../../../docs/modules/feature_flags/SPEC.md)

## Navigation

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
