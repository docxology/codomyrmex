# Agent Guidelines - Feature Flags

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Runtime feature toggles for gradual rollouts and quick incident response.

## Key Classes

- **`FeatureManager`** — Main entry point for management and evaluation.
- **`FlagEvaluator`** — Stateless evaluator for flag logic.
- **`RolloutManager`** — Manages staged rollout state.
- **`FlagStore`** — Abstract interface for persistence.

## Agent Instructions

1. **Prefer `FeatureManager`** — Always use the high-level manager for standard operations.
2. **Context Matters** — Always provide `user_id` when evaluating flags with percentage rollouts to ensure consistency.
3. **Descriptive Metadata** — Use the `metadata` field for multivariate flag values or extra tracking info.
4. **Cleanup** — Actively remove flags that are 100% rolled out and no longer needed in code.

## Common Patterns

### Creating a Flag
```python
manager.create_flag(
    "enable_ai_agent",
    enabled=True,
    percentage=10.0,
    description="Gradual rollout of AI assistant"
)
```

### Evaluating with Context
```python
is_on = manager.is_enabled(
    "enable_ai_agent",
    user_id="alice",
    tier="pro",
    region="us-east-1"
)
```

### Overriding for Tests
```python
manager.set_override("experimental_feature", True)
# ... run tests ...
manager.clear_override("experimental_feature")
```

## Targeting Rule Operators

- `eq`, `neq`: Equality
- `in`, `not_in`: Set membership
- `contains`: Substring or collection search
- `gt`, `lt`, `gte`, `lte`: Numeric comparisons
- `regex`: Regular expression matching

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
