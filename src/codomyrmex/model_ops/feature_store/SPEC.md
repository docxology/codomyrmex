# Feature Store - Technical Specification

> Codomyrmex v1.1.4 | March 2026

## Overview

This specification defines the feature store subsystem within the `model_ops` module. The feature store manages the lifecycle of ML features: definition, registration, ingestion, transformation, and serving for inference.

## Design Principles

1. **Pluggable backends** -- the `FeatureStore` ABC defines the storage contract; `InMemoryFeatureStore` is the reference implementation. Custom backends (Redis, database-backed) inherit from `FeatureStore`.
2. **Type-safe definitions** -- features are declared with `FeatureType` (semantic) and `ValueType` (data) enums, enabling validation before storage.
3. **Thread-safe writes** -- all mutating operations in `InMemoryFeatureStore` use `threading.Lock` to support concurrent agent access.
4. **Transform-at-read** -- feature transformations are applied at retrieval time via `FeatureTransform`, keeping stored values in their raw form.

## Architecture

```
feature_store/
    __init__.py       # Re-exports models + store + service
    store.py          # FeatureStore ABC, InMemoryFeatureStore
    service.py        # FeatureService, FeatureTransform
```

Dependencies flow: `service.py` -> `store.py` -> `models` (from `codomyrmex.feature_store.models`).

## Functional Requirements

### Feature Definition

| Requirement | Implementation |
|-------------|---------------|
| Features have typed schemas | `FeatureDefinition(name, feature_type, value_type)` |
| Features support default values | `FeatureDefinition.default_value` field |
| Features can be tagged and annotated | `FeatureDefinition.tags` and `.metadata` fields |
| Feature values are validated against definitions | `FeatureDefinition.validate_value(value) -> bool` |

### Storage Backend (FeatureStore ABC)

| Method | Signature | Description |
|--------|-----------|-------------|
| `register_feature` | `(definition: FeatureDefinition) -> None` | Register a feature schema |
| `get_feature_definition` | `(name: str) -> FeatureDefinition or None` | Look up a feature schema |
| `set_value` | `(feature_name: str, entity_id: str, value: Any) -> None` | Store a feature value |
| `get_value` | `(feature_name: str, entity_id: str) -> FeatureValue or None` | Retrieve a stored value |
| `get_vector` | `(entity_id: str, feature_names: list[str]) -> FeatureVector` | Multi-feature retrieval |

### InMemoryFeatureStore (additional methods)

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_features` | `() -> list[FeatureDefinition]` | List all registered features |
| `delete_value` | `(feature_name: str, entity_id: str) -> bool` | Remove a stored value |

### FeatureService

| Method | Signature | Description |
|--------|-----------|-------------|
| `register_group` | `(group: FeatureGroup) -> None` | Register a group and all its features |
| `register_feature` | `(definition: FeatureDefinition) -> None` | Register a single feature |
| `ingest` | `(features: dict, entity_id: str) -> None` | Store features for an entity |
| `ingest_batch` | `(batch: list[dict], entity_id_field: str) -> int` | Batch ingestion |
| `get_features` | `(entity_id: str, feature_names: list, apply_transform: bool) -> FeatureVector` | Serve features |
| `get_group_features` | `(entity_id: str, group_name: str) -> FeatureVector` | Serve all features in a group |
| `list_groups` | `() -> list[str]` | List registered group names |

### FeatureTransform

| Method | Signature | Description |
|--------|-----------|-------------|
| `add` | `(feature_name: str, func: Callable) -> FeatureTransform` | Add transform (chainable) |
| `apply` | `(vector: FeatureVector) -> FeatureVector` | Apply transforms to a vector |

## Interface Contracts

- `FeatureValue.version` is a monotonically increasing integer, starting at 1, incremented on each `set_value` call for the same entity+feature pair.
- `get_vector` applies `default_value` from `FeatureDefinition` when a value is not found for a feature name.
- `FeatureTransform.apply` returns a new `FeatureVector`; it does not mutate the input.
- `ingest_batch` returns the count of successfully ingested records; records missing the `entity_id_field` key are skipped.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `threading` | Lock for thread-safe `InMemoryFeatureStore` mutations |
| `abc` | Abstract base class for `FeatureStore` |
| `codomyrmex.feature_store.models` | `FeatureType`, `ValueType`, `FeatureDefinition`, `FeatureValue`, `FeatureVector`, `FeatureGroup` |

## Constraints

- `InMemoryFeatureStore` is not persistent -- data is lost on process exit. Use for testing and development only.
- Feature names must be unique within a store; re-registering a feature overwrites its definition.
- `FeatureTransform` skips `None` values (no transform applied, original `None` preserved).

## Navigation

- Parent: [model_ops module](../README.md)
- Root: [codomyrmex](../../../../README.md)
