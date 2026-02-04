# Feature Store Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Feature Store module provides ML feature management, storage, and retrieval for Codomyrmex. It offers a complete feature lifecycle from definition and registration through ingestion, transformation, and serving. The module includes typed feature definitions, versioned feature values, entity-based feature vectors, feature grouping, pluggable storage backends with an in-memory implementation, and a high-level service layer for ML application integration.

## Key Features

- **Typed Feature Definitions**: Define features with explicit types (`NUMERIC`, `CATEGORICAL`, `EMBEDDING`, `TEXT`, `TIMESTAMP`, `BOOLEAN`) and value types (`INT`, `FLOAT`, `STRING`, `BOOL`, `LIST`, `DICT`)
- **Versioned Feature Values**: Automatic version tracking on each feature value update with timestamps
- **Feature Vectors**: Retrieve multiple features for an entity as a single vector with ordering support
- **Feature Groups**: Organize related features into named groups with entity type association
- **Pluggable Storage**: Abstract `FeatureStore` base class with `InMemoryFeatureStore` implementation for development and testing
- **Feature Transforms**: Apply transformations (normalization, log scaling, etc.) to feature vectors before serving
- **Feature Service**: High-level `FeatureService` with group registration, batch ingestion, and transparent transform application
- **Common Definitions**: Pre-built feature definitions for common use cases (`USER_ID_FEATURE`, `TIMESTAMP_FEATURE`)

## Key Components

| Component | Description |
|-----------|-------------|
| `FeatureType` | Enum of feature types: NUMERIC, CATEGORICAL, EMBEDDING, TEXT, TIMESTAMP, BOOLEAN |
| `ValueType` | Enum of value data types: INT, FLOAT, STRING, BOOL, LIST, DICT |
| `FeatureDefinition` | Dataclass defining a feature with name, type, description, default value, tags, and metadata |
| `FeatureValue` | Dataclass for a single feature value with entity ID, timestamp, and version tracking |
| `FeatureVector` | Collection of feature values for an entity with dictionary access and list conversion |
| `FeatureGroup` | Named group of related feature definitions with entity type association |
| `FeatureStore` | Abstract base class for feature storage backends |
| `InMemoryFeatureStore` | Thread-safe in-memory feature store for development and testing |
| `FeatureTransform` | Pipeline for applying per-feature transformation functions to feature vectors |
| `FeatureService` | High-level service combining store, groups, batch ingestion, and transforms |
| `USER_ID_FEATURE` | Pre-built feature definition for user identifiers |
| `TIMESTAMP_FEATURE` | Pre-built feature definition for event timestamps |

## Quick Start

```python
from codomyrmex.feature_store import (
    FeatureService, InMemoryFeatureStore, FeatureGroup,
    FeatureDefinition, FeatureType, ValueType,
)

# Create the service
service = FeatureService(store=InMemoryFeatureStore())

# Register a feature group
user_features = FeatureGroup(
    name="user_features",
    features=[
        FeatureDefinition("age", FeatureType.NUMERIC, ValueType.INT),
        FeatureDefinition("city", FeatureType.CATEGORICAL, ValueType.STRING),
    ],
)
service.register_group(user_features)

# Ingest features
service.ingest({"age": 25, "city": "NYC"}, entity_id="user_123")

# Retrieve features for inference
vector = service.get_features("user_123", ["age", "city"])
print(vector.features)  # {"age": 25, "city": "NYC"}
```

### Applying Transforms

```python
from codomyrmex.feature_store import FeatureTransform

transform = FeatureTransform()
transform.add("age", lambda v: v / 100)  # Normalize age

service_with_transform = FeatureService(
    store=InMemoryFeatureStore(),
    transform=transform,
)
```

## Related Modules

- [inference_optimization](../inference_optimization/) - Optimized inference that consumes features from the store
- [feature_flags](../feature_flags/) - Feature flags for controlling feature store behavior at runtime

## Navigation

- **Source**: [src/codomyrmex/feature_store/](../../../src/codomyrmex/feature_store/)
- **API Specification**: [src/codomyrmex/feature_store/API_SPECIFICATION.md](../../../src/codomyrmex/feature_store/API_SPECIFICATION.md)
- **Parent**: [docs/modules/](../README.md)
