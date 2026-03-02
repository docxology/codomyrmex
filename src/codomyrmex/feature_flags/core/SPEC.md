# Core Flag Management -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides the `FeatureManager` class, a self-contained feature flag evaluation engine that supports boolean, percentage-based, allowlist/denylist, and time-windowed flags. Flags are stored in-memory with optional JSON file persistence.

## Architecture

`FeatureManager` holds an internal `dict[str, FlagDefinition]` and an override map `dict[str, bool]`. Evaluation walks a fixed priority chain (overrides first, boolean last). No external dependencies are required; the module uses only the Python standard library.

## Key Classes

### `FlagDefinition`

Dataclass representing a single feature flag.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `key` | `str` | required | Unique flag identifier |
| `enabled` | `bool` | `False` | Boolean on/off state |
| `percentage` | `float \| None` | `None` | 0-100 rollout percentage (deterministic per user) |
| `allowlist` | `list[str]` | `[]` | User IDs that always receive `True` |
| `denylist` | `list[str]` | `[]` | User IDs that always receive `False` |
| `start_time` | `float \| None` | `None` | Unix timestamp: flag active after this time |
| `end_time` | `float \| None` | `None` | Unix timestamp: flag inactive after this time |
| `description` | `str` | `""` | Human-readable description |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary data; `metadata["value"]` used for multivariate flags |

### `FeatureManager`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: dict \| None` | `None` | Bootstrap flags from a config dict (bool or dict values) |
| `create_flag` | `key: str, **kwargs` | `FlagDefinition` | Create or replace a flag definition |
| `delete_flag` | `key: str` | `bool` | Remove a flag; returns True if it existed |
| `get_flag` | `key: str` | `FlagDefinition \| None` | Retrieve a flag definition |
| `list_flags` | none | `list[FlagDefinition]` | List all registered flags |
| `is_enabled` | `key: str, default: bool, **context` | `bool` | Evaluate flag using six-step priority chain |
| `get_value` | `key: str, default: Any, **context` | `Any` | Get multivariate value from metadata |
| `set_override` | `key: str, value: bool` | `None` | Set a test override (highest priority) |
| `clear_override` | `key: str` | `None` | Remove a single test override |
| `clear_all_overrides` | none | `None` | Remove all test overrides |
| `load_from_file` | `file_path: str` | `int` | Load flags from JSON file; returns count loaded |
| `save_to_file` | `file_path: str` | `None` | Persist all flags to JSON file |
| `summary` | none | `dict[str, Any]` | Return counts of total, enabled, percentage, overrides |

## Dependencies

- **Internal**: None (self-contained within `feature_flags`)
- **External**: Standard library only (`json`, `pathlib`, `time`, `dataclasses`, `logging`)

## Constraints

- Percentage rollout requires a non-empty `user_id` in context; returns `False` without one.
- Time-window checks use `time.time()` (UTC epoch seconds).
- `save_to_file` / `load_from_file` use plain JSON with no atomic-write guarantees (see `storage` submodule for atomic persistence).
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `load_from_file` propagates `FileNotFoundError` and `json.JSONDecodeError` from the underlying file read.
- `is_enabled` never raises on missing flags; returns `default` instead.
- All errors logged via the module-level `logger` before propagation.
