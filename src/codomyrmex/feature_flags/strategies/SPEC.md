# Evaluation Strategies -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a Strategy-pattern framework for feature flag evaluation. Six concrete strategies cover boolean toggles, percentage rollouts, user targeting, attribute matching, environment gating, and composite (AND/OR) combinations. All strategies serialize to/from dicts for JSON persistence.

## Architecture

Each strategy extends `EvaluationStrategy` (ABC) and implements three methods: `evaluate`, `to_dict`, `from_dict`. The `create_strategy` factory dispatches on a `"type"` key to instantiate the correct class. `CompositeStrategy` recursively composes child strategies.

## Key Classes

### `EvaluationContext`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `user_id` | `str \| None` | `None` | Identifies the user for targeting and percentage hashing |
| `session_id` | `str \| None` | `None` | Session identifier (used in hash key for sticky rollouts) |
| `environment` | `str` | `"production"` | Current environment name |
| `attributes` | `dict[str, Any]` | `{}` | Arbitrary context attributes for `AttributeStrategy` |
| `timestamp` | `datetime` | `now()` | Evaluation time |
| `get_hash_key()` | -- | `str` | MD5 hex digest of `"{user_id}-{session_id}"` |

### `EvaluationResult`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | required | Whether the flag is on for this evaluation |
| `variant` | `str \| None` | `None` | Optional variant name for multivariate flags |
| `reason` | `str` | `""` | Human-readable evaluation reason (e.g., `"percentage:25%"`) |
| `metadata` | `dict[str, Any]` | `{}` | Strategy-specific details |

### `BooleanStrategy`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `enabled: bool = False` | -- | Set fixed boolean state |
| `evaluate` | `context: EvaluationContext` | `EvaluationResult` | Returns the fixed boolean |

### `PercentageStrategy`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `percentage: float, sticky: bool = True` | -- | Percentage clamped to [0, 100] |
| `evaluate` | `context: EvaluationContext` | `EvaluationResult` | Deterministic hash when sticky + user/session present; random otherwise |

### `UserListStrategy`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `allowed_users, blocked_users, default: bool` | -- | Sets stored as Python `set` internally |
| `evaluate` | `context: EvaluationContext` | `EvaluationResult` | Block list checked first, then allow list, then default |
| `add_user` | `user_id: str` | `None` | Add to allowlist |
| `remove_user` | `user_id: str` | `None` | Remove from allowlist |
| `block_user` | `user_id: str` | `None` | Add to blocklist |

### `AttributeStrategy`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `attribute: str, operator: str, value: Any, enabled_value: bool` | -- | Operators: eq, neq, gt, lt, gte, lte, in, contains |
| `evaluate` | `context: EvaluationContext` | `EvaluationResult` | Compares `context.attributes[attribute]` using the operator |

### `EnvironmentStrategy`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `enabled_environments: list[str]` | -- | Defaults to `["development"]` |
| `evaluate` | `context: EvaluationContext` | `EvaluationResult` | True only if `context.environment` is in the enabled set |

### `CompositeStrategy`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `strategies: list[EvaluationStrategy], operator: str` | -- | Operator is `"and"` or `"or"` |
| `evaluate` | `context: EvaluationContext` | `EvaluationResult` | Evaluates all children; combines with `all()` or `any()` |

### `create_strategy`

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `dict[str, Any]` | Dict with `"type"` key mapping to strategy class name |
| returns | `EvaluationStrategy` | Instantiated strategy via `from_dict` |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`hashlib`, `random`, `abc`, `datetime`, `dataclasses`, `logging`)

## Constraints

- `PercentageStrategy` uses MD5 (not cryptographic -- acceptable for rollout distribution).
- `AttributeStrategy` silently returns `False` on operator comparison errors (logged as warning).
- `CompositeStrategy.from_dict` recursively calls `create_strategy` for child strategies.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `create_strategy` raises `ValueError` for unknown strategy type strings.
- `AttributeStrategy._check_condition` catches `TypeError` / `ValueError` and logs a warning.
- All errors logged before propagation.
