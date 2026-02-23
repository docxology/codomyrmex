# feature_flags/strategies

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Feature flag evaluation strategies. Provides a pluggable strategy pattern for evaluating feature flags based on boolean toggles, percentage rollouts, user allowlists/blocklists, context attributes, environments, and composable AND/OR logic.

## Key Exports

### Data Classes

- **`EvaluationContext`** -- Context for flag evaluation containing optional user ID, session ID, environment name, custom attributes, and timestamp. Includes `get_hash_key()` for consistent hashing (MD5-based)
- **`EvaluationResult`** -- Result of a flag evaluation with enabled boolean, optional variant, reason string, and metadata

### Abstract Base Class

- **`EvaluationStrategy`** -- ABC requiring `evaluate()`, `to_dict()`, and `from_dict()` methods for all strategies. Supports full serialization/deserialization

### Strategy Implementations

- **`BooleanStrategy`** -- Simple on/off toggle. Returns a static enabled state
- **`PercentageStrategy`** -- Percentage-based rollout (0-100%). Supports sticky sessions via consistent MD5 hashing of user/session IDs, or random evaluation for non-sticky mode
- **`UserListStrategy`** -- Allowlist/blocklist evaluation. Blocked users are always denied, allowed users are always enabled, others get the default. Includes `add_user()`, `remove_user()`, and `block_user()` management methods
- **`AttributeStrategy`** -- Attribute-based targeting using comparison operators: `eq`, `neq`, `gt`, `lt`, `gte`, `lte`, `in`, `contains`. Evaluates against arbitrary context attributes
- **`EnvironmentStrategy`** -- Environment-based gating. Enables flags only in specified environments (e.g., development, staging, production)
- **`CompositeStrategy`** -- Combines multiple strategies with AND or OR logic. Supports recursive composition for advanced targeting rules

### Factory Function

- **`create_strategy()`** -- Deserialize a strategy from a dictionary config, dispatching to the appropriate class by `"type"` field

## Directory Contents

- `__init__.py` - Strategy ABC, six implementations, context/result data classes, and factory function (364 lines)
- `py.typed` - PEP 561 typing marker
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration documentation
- `PAI.md` - PAI integration notes

## Navigation

- **Parent Module**: [feature_flags](../README.md)
- **Project Root**: [codomyrmex](../../../../README.md)
