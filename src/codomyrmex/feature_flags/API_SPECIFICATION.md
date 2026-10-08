# Feature Flags - API Specification

## Introduction

The Feature Flags module provides a flexible system for managing feature toggles, enabling gradual rollouts, A/B testing, and runtime configuration changes without code deployments.

## Endpoints / Functions / Interfaces

### Class: `FeatureManager`

- **Description**: Central manager for feature flags: stores flag definitions, evaluates them for a context (percentage rollouts and targeting rules) and applies runtime overrides.
- **Constructor**:
    - `storage` (FlagStore, optional): Flag storage (default: in-memory).
    - `evaluator` (FlagEvaluator, optional): Flag evaluator.
    - `rollout_manager` (RolloutManager, optional): Rollout manager.
    - `config` (dict, optional): Manager configuration.
- **Methods**:

#### `is_enabled(name: str, default: bool = False, **context_attrs: Any) -> bool`

- **Description**: Evaluate whether a flag is enabled. A runtime override set with `set_override()` wins; an unknown flag returns `default`.
- **Parameters/Arguments**:
    - `name` (str): Name of the feature flag.
    - `default` (bool, optional): Result when the flag does not exist.
    - `**context_attrs`: Evaluation context. `user_id`, `session_id` and `environment` (default `"production"`) are recognised; any other keywords become context attributes for targeting rules.
- **Returns**:
    - `bool`: True if the feature is enabled.

#### `get_value(name: str, default: Any = None, **context_attrs: Any) -> Any`

- **Description**: Get a multivariate flag value: the flag's `metadata["value"]` when the flag is enabled for the context, else `default`.
- **Parameters/Arguments**:
    - `name` (str): Name of the feature flag.
    - `default` (Any, optional): Value when the flag is missing, disabled or has no value.
    - `**context_attrs`: Evaluation context, as for `is_enabled()`.
- **Returns**:
    - `Any`: Feature flag value.

#### `create_flag(name: str, enabled: bool = True, percentage: float = 100.0, targeting_rules: list[TargetingRule] | None = None, metadata: dict[str, Any] | None = None, description: str = "", **kwargs: Any) -> FlagDefinition`

- **Description**: Create or update a flag definition.

#### `set_override(name: str, enabled: bool) -> None`

- **Description**: Force a flag on or off at runtime; `clear_override(name)` removes the override.

#### `list_flags() -> list[FlagDefinition]`

- **Description**: List all registered flags. `get_flag(name)` returns one definition (or None) and `delete_flag(name)` removes it.

#### `load_from_file(file_path: str) -> int`

- **Description**: Load flags from a JSON file and return how many were loaded. `save_to_file(file_path)` writes all flags; `summary()` returns counts for the managed flags.

## Data Models

### Model: `FeatureFlag`

- `name` (str): Unique feature identifier.
- `enabled` (bool): Global enabled state.
- `description` (str | None): Feature description.
- `strategy` (EvaluationStrategy): How to evaluate the flag.
- `variants` (list[Variant] | None): Variants for multivariate flags.
- `targeting_rules` (list[TargetingRule] | None): Rules for targeted rollout.
- `percentage` (float | None): Percentage of users to enable for (0-100).
- `metadata` (dict | None): Additional metadata.

### Model: `EvaluationStrategy`

- `BOOLEAN`: Simple on/off flag.
- `PERCENTAGE`: Enable for a percentage of users.
- `USER_TARGETING`: Enable based on user attributes.
- `MULTIVARIATE`: Return different variants.

### Model: `Variant`

- `name` (str): Variant name.
- `value` (Any): Variant value.
- `weight` (int): Relative weight for selection.

### Model: `TargetingRule`

- `attribute` (str): Context attribute to check.
- `operator` (str): Comparison operator (eq, neq, in, contains, etc.).
- `value` (Any): Value to compare against.
- `enabled` (bool): Result if rule matches.

### Model: `EvaluationResult`

- `feature_name` (str): Feature flag name.
- `enabled` (bool): Whether feature is enabled.
- `value` (Any | None): Feature value.
- `variant` (str | None): Selected variant name.
- `reason` (str): Evaluation reason.
- `metadata` (dict): Additional evaluation metadata.

## Authentication & Authorization

Feature flag management endpoints should be protected. The module supports integration with external auth systems.

## Rate Limiting

Redis-backed feature flags support caching to minimize backend calls.

## Versioning

This API follows semantic versioning. Breaking changes will be documented in the changelog.
