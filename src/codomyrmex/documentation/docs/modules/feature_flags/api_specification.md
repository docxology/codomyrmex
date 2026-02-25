# Feature Flags - API Specification

## Introduction

The Feature Flags module provides a flexible system for managing feature toggles, enabling gradual rollouts, A/B testing, and runtime configuration changes without code deployments.

## Endpoints / Functions / Interfaces

### Class: `FeatureManager`

- **Description**: Central manager for feature flags with support for various evaluation strategies.
- **Constructor**:
    - `backend` (str, optional): Storage backend ("memory", "redis", "file"). Default: "memory".
    - `config_path` (str, optional): Path to configuration file.
    - `redis_client` (optional): Redis client for distributed feature flags.
- **Methods**:

#### `is_enabled(feature_name: str, context: dict | None = None) -> bool`

- **Description**: Check if a feature is enabled for the given context.
- **Parameters/Arguments**:
    - `feature_name` (str): Name of the feature flag.
    - `context` (dict, optional): Evaluation context (user_id, attributes, etc.).
- **Returns**:
    - `bool`: True if the feature is enabled.

#### `get_value(feature_name: str, default: Any = None, context: dict | None = None) -> Any`

- **Description**: Get the value of a feature flag (for multivariate flags).
- **Parameters/Arguments**:
    - `feature_name` (str): Name of the feature flag.
    - `default` (Any, optional): Default value if flag not found.
    - `context` (dict, optional): Evaluation context.
- **Returns**:
    - `Any`: Feature flag value.

#### `set_enabled(feature_name: str, enabled: bool) -> None`

- **Description**: Enable or disable a feature flag.
- **Parameters/Arguments**:
    - `feature_name` (str): Name of the feature flag.
    - `enabled` (bool): Whether the feature should be enabled.

#### `register_feature(feature: FeatureFlag) -> None`

- **Description**: Register a new feature flag.
- **Parameters/Arguments**:
    - `feature` (FeatureFlag): Feature flag configuration.

#### `get_all_features() -> list[FeatureFlag]`

- **Description**: Get all registered feature flags.
- **Returns**:
    - `list[FeatureFlag]`: List of all feature flags.

#### `evaluate(feature_name: str, context: dict) -> EvaluationResult`

- **Description**: Evaluate a feature flag with detailed result information.
- **Parameters/Arguments**:
    - `feature_name` (str): Name of the feature flag.
    - `context` (dict): Evaluation context.
- **Returns**:
    - `EvaluationResult`: Detailed evaluation result.

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
