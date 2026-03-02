# Feature Flags Module

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

Advanced feature flag management with evaluation strategies, gradual rollout, and persistent storage.

## Design Principles

- **Resilience**: Defaults to safe 'closed' states if evaluation fails.
- **Performance**: High-speed deterministic evaluation using hashing.
- **Flexibility**: Multiple storage backends and rich targeting rules.

## Architecture

The module is composed of several specialized submodules:

- **`core`**: The central `FeatureManager` that orchestrates evaluation, storage, and rollouts.
- **`evaluation`**: Core logic for evaluating flags against contexts.
- **`strategies`**: Implementation of various evaluation strategies (Boolean, Percentage, UserList, etc.).
- **`rollout`**: Management of multi-stage gradual rollouts.
- **`storage`**: Backends for flag persistence (In-memory, File).

## Quick Start

```python
from codomyrmex.feature_flags import FeatureManager

# Initialize manager
manager = FeatureManager()

# Create a flag with a 25% rollout
manager.create_flag("new_ui", percentage=25.0, description="New user interface")

# Check if enabled for a user
if manager.is_enabled("new_ui", user_id="user_123"):
    show_new_ui()
else:
    show_old_ui()

# Multivariate flags
manager.create_flag("max_results", enabled=True, metadata={"value": 50})
limit = manager.get_value("max_results", default=10)
```

## Advanced Targeting

Targeting rules allow granular control based on user attributes:

```python
from codomyrmex.feature_flags.evaluation import TargetingRule

rule = TargetingRule(attribute="plan", operator="eq", value="premium")
manager.create_flag("beta_feature", targeting_rules=[rule])

# Enabled only for premium users
is_enabled = manager.is_enabled("beta_feature", plan="premium")
```

## Documentation

- [SPEC](SPEC.md) - Functional Specification
- [AGENTS](AGENTS.md) - Guidelines for AI Agents
- [SECURITY](SECURITY.md) - Security and Privacy considerations
