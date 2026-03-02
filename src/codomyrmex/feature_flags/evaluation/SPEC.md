# Flag Evaluation Engine -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Core evaluation logic for feature flags, implementing targeting rules, percentage-based rollout via deterministic hashing, and a global kill-switch. Evaluates flags against an `EvaluationContext` with a defined precedence order.

## Architecture

Stateless evaluator design. `FlagEvaluator` receives a `FlagDefinition` and `EvaluationContext`, applies evaluation rules in strict precedence (kill-switch, targeting rules, percentage rollout), and returns an `EvaluationResult`. Percentage rollout uses SHA-256 hashing of flag name + user ID for deterministic, consistent bucketing.

## Key Classes

### `TargetingRule` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `attribute` | `str` | Context attribute key to match against |
| `operator` | `str` | Comparison operator: `eq`, `neq`, `in`, `contains`, `gt`, `lt`, `gte`, `lte` |
| `value` | `Any` | Value to compare with |

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `matches` | `context: EvaluationContext` | `bool` | Test if this rule matches the given context |

### `FlagDefinition` (Dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Unique flag identifier |
| `enabled` | `bool` | Global kill-switch (default True) |
| `percentage` | `float` | Rollout percentage 0.0-100.0 (default 100.0) |
| `targeting_rules` | `list[TargetingRule]` | Optional targeting rules (OR logic) |

### `FlagEvaluator`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `evaluate` | `flag, context` | `EvaluationResult` | Evaluate a flag with full precedence chain |
| `evaluate_targeting_rules` | `rules, context` | `bool` | Return True if any targeting rule matches (OR logic) |
| `evaluate_percentage_rollout` | `flag, user_id` | `bool` | Deterministic bucket check using SHA-256 |

## Evaluation Precedence

1. **Kill-switch**: If `flag.enabled` is False, always return disabled.
2. **Targeting rules**: If rules exist and none match, return disabled.
3. **Percentage rollout**: Hash-based deterministic bucketing (0.01% granularity).
4. **Default**: Return enabled.

## Percentage Rollout Algorithm

```
hash = SHA-256(flag_name + ":" + user_id)
bucket = int(hash[:8], 16) % 10000    # 0-9999
threshold = percentage * 100           # basis points
enabled = bucket < threshold
```

## Dependencies

- **Internal**: `feature_flags.strategies` (`EvaluationContext`, `EvaluationResult`, `EvaluationStrategy`)
- **External**: None (Python stdlib: `hashlib`, `logging`, `dataclasses`)

## Constraints

- Targeting rule comparison failures (TypeError, ValueError) are caught, logged as warnings, and treated as non-matches.
- Percentage rollout is deterministic: same flag + user always produces the same result.
- Zero-mock: real evaluation only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Invalid operator names silently return False (rule does not match).
- Type mismatches in targeting rule comparisons are caught and logged as warnings.
- All errors logged before propagation.
