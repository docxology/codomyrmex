# Feature Store

> Codomyrmex v1.1.4 | March 2026

## Overview

The `feature_store` submodule provides feature management, storage, and serving for ML applications. It implements a pluggable storage backend architecture with an in-memory implementation for development and testing, plus a high-level `FeatureService` for feature ingestion, transformation, and retrieval.

Features are defined with explicit types and schemas via `FeatureDefinition`, organized into `FeatureGroup` collections, and served as `FeatureVector` objects for point-in-time inference.

## PAI Integration

| PAI Phase | Role |
|-----------|------|
| BUILD | Feature definitions and transforms are authored during model development |
| EXECUTE | `FeatureService.get_features()` serves feature vectors at inference time |
| VERIFY | Feature type validation ensures data quality before model consumption |

## Key Exports

| Export | Type | Description |
|--------|------|-------------|
| `FeatureType` | Enum | Feature categories: NUMERIC, CATEGORICAL, EMBEDDING, TEXT, TIMESTAMP, BOOLEAN |
| `ValueType` | Enum | Data types: INT, FLOAT, STRING, BOOL, LIST, DICT |
| `FeatureDefinition` | dataclass | Feature schema with name, types, default value, tags, metadata |
| `FeatureValue` | dataclass | A stored feature value for a specific entity with versioning |
| `FeatureVector` | dataclass | Multiple feature values for an entity at a point in time |
| `FeatureGroup` | dataclass | Named collection of related `FeatureDefinition` objects |
| `FeatureStore` | ABC | Abstract base class for storage backends |
| `InMemoryFeatureStore` | class | Thread-safe in-memory storage implementation |
| `FeatureTransform` | class | Chainable feature value transformations |
| `FeatureService` | class | High-level service combining store, groups, and transforms |
| `USER_ID_FEATURE` | constant | Built-in user ID feature definition |
| `TIMESTAMP_FEATURE` | constant | Built-in timestamp feature definition |

## Quick Start

```python
from codomyrmex.model_ops.feature_store import (
    FeatureDefinition, FeatureGroup, FeatureService,
    FeatureTransform, FeatureType, InMemoryFeatureStore, ValueType,
)

# Create store and service
store = InMemoryFeatureStore()
transform = FeatureTransform()
transform.add("age", lambda v: v / 100)  # Normalize age

service = FeatureService(store=store, transform=transform)

# Define and register features
user_features = FeatureGroup(
    name="user_features",
    features=[
        FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
        FeatureDefinition("city", FeatureType.CATEGORICAL, ValueType.STRING),
    ],
)
service.register_group(user_features)

# Ingest data
service.ingest({"age": 25, "city": "NYC"}, entity_id="user_123")

# Retrieve for inference
vector = service.get_features("user_123", ["age", "city"])
print(vector.features)  # {"age": 0.25, "city": "NYC"}
```

## Architecture

```
model_ops/feature_store/
    __init__.py       # Module exports and CLI commands
    store.py          # FeatureStore ABC + InMemoryFeatureStore
    service.py        # FeatureService + FeatureTransform
```

Models (`FeatureType`, `ValueType`, `FeatureDefinition`, `FeatureValue`, `FeatureVector`, `FeatureGroup`) are defined in the sibling `codomyrmex.feature_store.models` module and re-exported here.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/model_ops/ -v
```

## Navigation

- Parent: [model_ops module](../README.md)
- Models: [feature_store.models](../../../feature_store/models.py)
- Root: [codomyrmex](../../../../README.md)
