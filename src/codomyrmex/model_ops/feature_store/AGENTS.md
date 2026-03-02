# Codomyrmex Agents — src/codomyrmex/model_ops/feature_store

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Feature store sub-module for ML inference and training pipelines. Provides typed feature definitions, versioned per-entity feature storage, feature vector retrieval, feature grouping, batch ingestion, and configurable pre-serving transforms. Includes both an abstract `FeatureStore` backend interface and a thread-safe `InMemoryFeatureStore` implementation.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `FeatureType` | Enum of feature types: NUMERIC, CATEGORICAL, EMBEDDING, TEXT, TIMESTAMP, BOOLEAN |
| `models.py` | `ValueType` | Enum of value types: INT, FLOAT, STRING, BOOL, LIST, DICT |
| `models.py` | `FeatureDefinition` | Dataclass defining a feature with name, type, description, default value, tags |
| `models.py` | `FeatureValue` | Dataclass holding a versioned value for a specific feature/entity pair with timestamp |
| `models.py` | `FeatureVector` | Collection of feature values for a single entity; supports `get()` and `to_list()` |
| `models.py` | `FeatureGroup` | Named group of related `FeatureDefinition` instances with entity type |
| `store.py` | `FeatureStore` (ABC) | Abstract backend interface: `register_feature`, `set_value`, `get_value`, `get_vector` |
| `store.py` | `InMemoryFeatureStore` | Thread-safe in-memory implementation with auto-versioning and default-value fallback |
| `service.py` | `FeatureTransform` | Registers per-feature callables; `apply()` transforms a `FeatureVector` immutably |
| `service.py` | `FeatureService` | High-level facade: group registration, single/batch ingestion, transform-aware retrieval |

## Operating Contracts

- `InMemoryFeatureStore` uses `threading.Lock` for all mutations; safe for concurrent access.
- `FeatureValue.version` auto-increments on each `set_value()` call for the same feature/entity pair.
- `get_vector()` falls back to `FeatureDefinition.default_value` when no stored value exists.
- `FeatureTransform.apply()` returns a new `FeatureVector` without mutating the input.
- `FeatureService.ingest_batch()` expects records with an `entity_id_field` key; records lacking it are skipped.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`threading`, `datetime`, `dataclasses`, `enum`)
- **Used by**: ML inference pipelines requiring feature lookup at serving time

## Navigation

- **Parent**: [model_ops](../README.md)
- **Root**: [Root](../../../../README.md)
