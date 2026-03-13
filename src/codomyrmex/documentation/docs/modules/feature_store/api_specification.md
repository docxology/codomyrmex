# Feature Store - API Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## 1. Overview
The `feature_store` module provides feature management, storage, and serving for ML applications. Supports typed feature definitions, point-in-time retrieval, feature groups, and online/offline serving with pluggable storage backends.

## 2. Core Components

### 2.1 Classes

| Class | Description |
|-------|-------------|
| `FeatureStore` | Abstract base for feature storage backends |
| `InMemoryFeatureStore` | Ephemeral in-memory storage for development and testing |
| `FeatureService` | Online feature serving with transform pipelines |
| `FeatureTransform` | Chainable feature transformation (normalisation, encoding, etc.) |
| `FeatureDefinition` | Schema definition for a single feature (name, type, default) |
| `FeatureGroup` | Logical grouping of related features |
| `FeatureValue` | A single feature value with metadata |
| `FeatureVector` | Point-in-time feature vector for model inference |

### 2.2 Enums

| Enum | Values |
|------|--------|
| `FeatureType` | Numerical, categorical, text, embedding, etc. |
| `ValueType` | float, int, string, bool, list, etc. |

### 2.3 Exceptions

| Exception | Description |
|-----------|-------------|
| `FeatureStoreError` | Base exception for feature store operations |
| `FeatureNotFoundError` | Requested feature does not exist |
| `FeatureRegistrationError` | Feature registration failed |
| `FeatureValidationError` | Feature value fails validation |

### 2.4 Constants

| Name | Description |
|------|-------------|
| `USER_ID_FEATURE` | Built-in user ID feature definition |
| `TIMESTAMP_FEATURE` | Built-in timestamp feature definition |

## 3. Usage Example

```python
from codomyrmex.feature_store import InMemoryFeatureStore, FeatureDefinition, FeatureType

store = InMemoryFeatureStore()
store.register(FeatureDefinition(name="age", feature_type=FeatureType.NUMERICAL))
store.ingest("user_1", {"age": 25})

vector = store.get_features("user_1", ["age"])
print(vector.values)
```

## 4. Navigation

- [README](README.md) | [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
