# Feature Store Specification

**Version**: v1.1.6 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides feature management, storage, and serving for ML applications. Defines feature schemas with type validation, supports feature groups and point-in-time retrieval, and includes built-in feature transforms.

## Functional Requirements

1. Feature definition with typed schemas (FeatureType, ValueType) and validation rules
2. Feature group management for organizing related features with shared metadata
3. Point-in-time feature vector retrieval via FeatureVector for training and inference


## Interface

```python
from codomyrmex.feature_store import FeatureStore, InMemoryFeatureStore, FeatureDefinition, FeatureType

store = InMemoryFeatureStore()
store.register(FeatureDefinition(name="age", feature_type=FeatureType.NUMERIC))
store.ingest(entity_id="user_1", features={"age": 30})
vector = store.get_vector(entity_id="user_1")
```

## Exports

FeatureType, ValueType, FeatureDefinition, FeatureValue, FeatureVector, FeatureGroup, FeatureStore, InMemoryFeatureStore, FeatureTransform, FeatureService

## Navigation

- [Source README](../../src/codomyrmex/feature_store/README.md) | [AGENTS.md](AGENTS.md)
