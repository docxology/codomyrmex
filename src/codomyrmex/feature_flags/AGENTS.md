# Agent Guidelines - Feature Flags

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Runtime feature toggles for gradual rollouts and quick incident response. Provides `FeatureManager`
for flag creation and evaluation, `FlagEvaluator` for stateless flag logic, `RolloutManager` for
staged rollout state, and targeting rules for user segmentation. Three MCP tools (`flag_create`,
`flag_is_enabled`, `flag_list`) expose the full flag lifecycle to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `FeatureManager`, `FlagEvaluator`, `RolloutManager`, `FlagStore` |
| `manager.py` | `FeatureManager` — main entry point for flag management and evaluation |
| `evaluation.py` | `FlagEvaluator`, `FlagDefinition` — stateless flag evaluation |
| `strategies/` | Rollout strategies (`PercentageStrategy`, `UserListStrategy`, `TimeWindowStrategy`) |
| `strategies/__init__.py` | `EvaluationContext` — context passed to flag evaluators |
| `store.py` | `FlagStore` — abstract persistence interface |
| `mcp_tools.py` | MCP tools: `flag_create`, `flag_is_enabled`, `flag_list` |

## Key Classes

- **`FeatureManager`** — Main entry point for flag management and evaluation
- **`FlagEvaluator`** — Stateless evaluator for flag logic
- **`RolloutManager`** — Manages staged rollout state
- **`FlagStore`** — Abstract interface for persistence
- **`EvaluationContext`** — Context object passed to evaluators (user_id, tier, region, etc.)

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `flag_create` | Create or update a feature flag with key, enabled state, and rollout percentage | SAFE |
| `flag_is_enabled` | Evaluate whether a feature flag is enabled for an optional user ID | SAFE |
| `flag_list` | List all feature flags currently defined in this session | SAFE |

## Agent Instructions

1. **Prefer `FeatureManager`** — Always use the high-level manager for standard operations
2. **Context Matters** — Always provide `user_id` when evaluating flags with percentage rollouts to ensure consistency
3. **Descriptive Metadata** — Use the `metadata` field for multivariate flag values or extra tracking info
4. **Cleanup** — Actively remove flags that are 100% rolled out and no longer needed in code
5. **MCP session scope** — MCP tools store flags in a process-local dict; flags are not persisted between sessions

## Operating Contracts

- MCP tool flag registry is process-local — not shared across MCP server restarts
- `flag_is_enabled` returns `False` for unknown keys (no exception)
- `FlagEvaluator.evaluate()` is stateless — create a new instance per evaluation or share safely
- `percentage=0.0` is always OFF; `percentage=100.0` is always ON (regardless of `user_id`)
- **DO NOT** store secrets or user PII in flag `metadata` — flags may be logged

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

## Testing Patterns

```python
# Verify flag creation and evaluation
from codomyrmex.feature_flags import FeatureManager

manager = FeatureManager()
manager.create_flag("test_flag", enabled=True, percentage=100.0)
assert manager.is_enabled("test_flag", user_id="alice") is True

# Verify disabled flag
manager.create_flag("off_flag", enabled=False)
assert manager.is_enabled("off_flag") is False

# Verify override mechanism
manager.set_override("test_flag", False)
assert manager.is_enabled("test_flag") is False
manager.clear_override("test_flag")
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full | `flag_create`, `flag_is_enabled`, `flag_list` | TRUSTED |
| **Architect** | Read + Design | `flag_list` — flag taxonomy review, rollout strategy design | OBSERVED |
| **QATester** | Validation | `flag_is_enabled`, `flag_list` — flag evaluation verification during VERIFY | OBSERVED |
| **Researcher** | Read-only | `flag_list`, `flag_is_enabled` — inspect flag state for analysis | SAFE |

### Engineer Agent
**Use Cases**: Creating and managing feature flags during BUILD/EXECUTE, implementing percentage rollouts, overriding flags for test isolation.

### Architect Agent
**Use Cases**: Designing flag taxonomy, planning rollout strategies, reviewing targeting rule architecture.

### QATester Agent
**Use Cases**: Verifying flag evaluation correctness during VERIFY, confirming rollout percentages, testing targeting rules.

### Researcher Agent
**Use Cases**: Inspecting active feature flag state to understand system configuration during analysis.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
