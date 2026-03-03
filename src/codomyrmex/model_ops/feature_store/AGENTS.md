# Feature Store - Agent Coordination

> Codomyrmex v1.0.8 | March 2026

## Overview

The feature store submodule provides ML feature management for agents working with model operations. It exposes a `FeatureStore` abstract backend, a thread-safe `InMemoryFeatureStore`, and a high-level `FeatureService` for ingestion, batch loading, transformation, and retrieval of feature vectors.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports: models, store backends, service, CLI commands |
| `store.py` | `FeatureStore` (ABC) and `InMemoryFeatureStore` with thread-safe CRUD |
| `service.py` | `FeatureService` for group registration, ingestion, batch ops, and `FeatureTransform` |

## MCP Tools Available

The feature store does not expose its own MCP tools directly. Feature operations are accessed through the parent `model_ops` module MCP tools.

## Agent Instructions

1. **Use `InMemoryFeatureStore` for testing** -- it provides thread-safe storage without external dependencies, suitable for agent-driven test scenarios.
2. **Register features before use** -- call `store.register_feature(definition)` or `service.register_group(group)` before ingesting values; otherwise values are stored without type validation.
3. **Apply transforms at retrieval time** -- `FeatureTransform` normalizes or transforms feature values when `service.get_features()` is called with `apply_transform=True` (the default).
4. **Use batch ingestion for bulk loads** -- `service.ingest_batch(records, entity_id_field="entity_id")` processes lists of dictionaries efficiently.
5. **Version tracking is automatic** -- `InMemoryFeatureStore.set_value()` increments the version counter on each update for a given entity+feature pair.

## Operating Contracts

- `FeatureStore` is an ABC; agents must use `InMemoryFeatureStore` or implement a custom backend inheriting from `FeatureStore`.
- `FeatureValue` objects include `version` (auto-incremented integer) and `timestamp` (set at creation).
- `FeatureVector.features` is a `dict[str, Any]` mapping feature names to their values, with defaults applied for missing values when definitions exist.
- All store write operations (`set_value`, `delete_value`, `register_feature`) are guarded by `threading.Lock`.

## Common Patterns

```python
from codomyrmex.model_ops.feature_store import (
    FeatureDefinition, FeatureType, ValueType,
    InMemoryFeatureStore, FeatureService, FeatureTransform,
)

# Direct store usage
store = InMemoryFeatureStore()
store.register_feature(FeatureDefinition("score", FeatureType.NUMERIC, ValueType.FLOAT))
store.set_value("score", "entity_1", 0.95)
value = store.get_value("score", "entity_1")
# value.value == 0.95, value.version == 1

# Service with transforms
transform = FeatureTransform()
transform.add("score", lambda v: round(v, 2))
service = FeatureService(store=store, transform=transform)
vector = service.get_features("entity_1", ["score"])
```

## PAI Agent Role Access Matrix

| Agent Role | Access Level | Typical Use |
|------------|-------------|-------------|
| Engineer | Read/Write | Implement feature pipelines and storage backends |
| Architect | Read | Design feature schemas and group organizations |
| QATester | Read/Write | Validate feature ingestion and retrieval correctness |

## Navigation

- Parent: [model_ops module](../README.md)
- Root: [codomyrmex](../../../../README.md)
