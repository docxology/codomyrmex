# Agent Guidelines - Feature Flags

## Module Overview

Runtime feature toggles for gradual rollouts and quick incident response.

## Key Classes

- **FlagManager** — Create and manage feature flags
- **FlagEvaluator** — Evaluate flags for users
- **RolloutStrategy** — Percentage-based rollouts
- **FlagStore** — Persistent flag storage

## Agent Instructions

1. **Default to off** — New flags should be disabled by default
2. **Use descriptive names** — `enable_new_checkout` not `flag_1`
3. **Clean up** — Remove flags after full rollout
4. **Percentage rollouts** — Use for gradual releases
5. **Override for testing** — Use test overrides, not hardcodes

## Common Patterns

```python
from codomyrmex.feature_flags import FlagManager, FlagEvaluator

# Initialize flag manager
flags = FlagManager()

# Create a feature flag
flags.create("new_dashboard", default=False, description="New dashboard UI")

# Percentage rollout
flags.set_rollout("new_dashboard", percentage=10)  # 10% of users

# Evaluate for a user
evaluator = FlagEvaluator(flags)
if evaluator.is_enabled("new_dashboard", user_id=user.id):
    show_new_dashboard()
else:
    show_old_dashboard()

# Override for testing
with flags.override("new_dashboard", True):
    test_new_dashboard()
```

## Testing Patterns

```python
# Verify flag creation
flags = FlagManager()
flags.create("test_flag", default=False)
assert not flags.is_enabled("test_flag")

# Verify rollout
flags.set_rollout("test_flag", percentage=100)
assert flags.is_enabled("test_flag", user_id="any")

# Verify override
with flags.override("test_flag", True):
    assert flags.is_enabled("test_flag")
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
