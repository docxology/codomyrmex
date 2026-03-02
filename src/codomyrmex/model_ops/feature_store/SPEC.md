# Feature Store — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

A typed, versioned feature store for ML serving and training. Features are defined with `FeatureType` and `ValueType` enums, stored per entity with automatic versioning, and retrieved as `FeatureVector` collections. A high-level `FeatureService` adds group registration, batch ingestion, and optional pre-serving transforms.

## Architecture

Three-layer design: **models** (dataclasses and enums), **store** (abstract backend with in-memory implementation), and **service** (high-level facade). The abstract `FeatureStore` interface allows plugging in persistent backends while `InMemoryFeatureStore` serves development and testing. `FeatureService` orchestrates store operations with optional `FeatureTransform` pipelines.

## Key Classes

### `FeatureDefinition`

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Feature identifier |
| `feature_type` | `FeatureType` | NUMERIC, CATEGORICAL, EMBEDDING, TEXT, TIMESTAMP, BOOLEAN |
| `value_type` | `ValueType` | INT, FLOAT, STRING, BOOL, LIST, DICT |
| `default_value` | `Any` | Fallback value when no stored value exists |
| `tags` | `list[str]` | Grouping/filtering tags |

### `InMemoryFeatureStore`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_feature` | `definition: FeatureDefinition` | `None` | Register a feature definition |
| `set_value` | `feature_name, entity_id, value` | `None` | Store a value; auto-increments version |
| `get_value` | `feature_name, entity_id` | `FeatureValue or None` | Retrieve stored value |
| `get_vector` | `entity_id, feature_names` | `FeatureVector` | Multi-feature lookup with default fallback |
| `list_features` | — | `list[FeatureDefinition]` | All registered definitions |
| `delete_value` | `feature_name, entity_id` | `bool` | Remove a stored value |

### `FeatureService`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register_group` | `group: FeatureGroup` | `None` | Register all features in a group |
| `ingest` | `features: dict, entity_id: str` | `None` | Store feature values for an entity |
| `ingest_batch` | `batch: list[dict], entity_id_field` | `int` | Batch ingest; returns count of records processed |
| `get_features` | `entity_id, feature_names, apply_transform` | `FeatureVector` | Retrieve with optional transform |
| `get_group_features` | `entity_id, group_name` | `FeatureVector` | Retrieve all features in a named group |

### `FeatureTransform`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `add` | `feature_name, func` | `FeatureTransform` | Register a transform callable (chainable) |
| `apply` | `vector: FeatureVector` | `FeatureVector` | Apply transforms, returning new vector |

## Dependencies

- **Internal**: None
- **External**: Standard library only (`threading`, `datetime`, `dataclasses`, `enum`)

## Constraints

- Thread safety via `threading.Lock` on all store mutations.
- Feature values are versioned starting at 1; each `set_value` call increments.
- `FeatureValue.age_seconds` computed from `datetime.now()` delta.
- `get_vector()` silently uses `default_value` for missing stored values.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- Missing features in `get_vector()` fall back to default values; no exception raised.
- `ingest_batch()` silently skips records without the `entity_id_field` key.
- All errors logged before propagation.
