# Codomyrmex Agents — src/codomyrmex/feature_flags/strategies

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Pluggable evaluation strategies for feature flags. Implements the Strategy pattern with an abstract `EvaluationStrategy` base class and six concrete strategies: `BooleanStrategy`, `PercentageStrategy`, `UserListStrategy`, `AttributeStrategy`, `EnvironmentStrategy`, and `CompositeStrategy`. Each strategy evaluates an `EvaluationContext` and returns a typed `EvaluationResult` with enable state, variant, reason, and metadata.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `__init__.py` | `EvaluationContext` | Dataclass carrying user_id, session_id, environment, attributes, and timestamp for evaluation |
| `__init__.py` | `EvaluationResult` | Dataclass with enabled bool, optional variant, reason string, and metadata dict |
| `__init__.py` | `EvaluationStrategy` | ABC defining `evaluate`, `to_dict`, and `from_dict` interface |
| `__init__.py` | `BooleanStrategy` | Simple on/off toggle returning a fixed boolean |
| `__init__.py` | `PercentageStrategy` | MD5-based deterministic rollout; supports sticky sessions via `get_hash_key()` |
| `__init__.py` | `UserListStrategy` | Allow/block list evaluation with configurable default for unknown users |
| `__init__.py` | `AttributeStrategy` | Evaluates context attributes against operators: eq, neq, gt, lt, gte, lte, in, contains |
| `__init__.py` | `EnvironmentStrategy` | Enables flag only in specified environments (e.g., development, staging) |
| `__init__.py` | `CompositeStrategy` | Combines multiple strategies with AND/OR logic |
| `__init__.py` | `create_strategy` | Factory function that deserializes a strategy dict into the correct class via a type registry |

## Operating Contracts

- Every strategy must implement `evaluate(context) -> EvaluationResult`, `to_dict() -> dict`, and `from_dict(data) -> EvaluationStrategy`.
- `PercentageStrategy` uses `hashlib.md5` for consistent hashing; percentages are clamped to [0, 100].
- `AttributeStrategy._check_condition` catches `TypeError`/`ValueError` and logs a warning rather than crashing.
- `create_strategy` raises `ValueError` for unknown strategy types.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: `hashlib`, `random`, `abc`, `datetime`, `dataclasses` (standard library only)
- **Used by**: `feature_flags.core.FeatureManager` (for pluggable evaluation), `feature_flags.rollout`

## Navigation

- **Parent**: [feature_flags](../README.md)
- **Root**: [Root](../../../../README.md)
