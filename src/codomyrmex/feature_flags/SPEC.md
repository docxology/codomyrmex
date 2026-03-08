# feature_flags - Functional Specification

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Purpose

To provide a resilient, low-latency system for controlling functional and operational aspects of Codomyrmex at runtime.

## Interface Contracts

### `FeatureManager`

- `create_flag(name, enabled=True, percentage=100.0, targeting_rules=None, metadata=None, description="")`
- `is_enabled(name, default=False, **context_attrs) -> bool`
- `get_value(name, default=None, **context_attrs) -> Any`
- `delete_flag(name) -> bool`
- `set_override(name, enabled: bool)`
- `load_from_file(path: str)`
- `save_to_file(path: str)`

### `TargetingRule`

- `attribute: str`
- `operator: str` (eq, neq, in, not_in, contains, gt, lt, gte, lte, regex)
- `value: Any`

## Evaluation Logic

1. **Global Override**: If a runtime override exists, use it immediately.
2. **Global Kill-switch**: If `flag.enabled` is `False`, return `False`.
3. **Targeting Rules**: If rules exist, evaluate them with `OR` logic. If none match, return `False`.
4. **Percentage Rollout**: Apply deterministic hashing (SHA-256) on `flag.name` and `user_id`. If user falls within `percentage`, return `True`.
5. **Default**: If no rules or percentage are specified (and enabled is True), return `True`.

## Persistence

Supports JSON file storage by default. Custom backends can implement the `FlagStore` interface.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/feature_flags/ -v
```
