# Feature Store — Functional Specification

**Module**: `codomyrmex.feature_store`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

ML feature management, storage, and retrieval.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `FeatureType` | Class | Types of features. |
| `ValueType` | Class | Data types for feature values. |
| `FeatureDefinition` | Class | Definition of a feature. |
| `FeatureValue` | Class | A feature value with metadata. |
| `FeatureVector` | Class | A collection of feature values for an entity. |
| `FeatureGroup` | Class | A group of related features. |
| `FeatureStore` | Class | Base class for feature storage backends. |
| `InMemoryFeatureStore` | Class | In-memory feature store for development and testing. |
| `FeatureTransform` | Class | Transform features before serving. |
| `FeatureService` | Class | High-level feature service for ML applications. |
| `full_name()` | Function | Get fully qualified name. |
| `to_dict()` | Function | Convert to dictionary. |
| `age_seconds()` | Function | Get age of this value in seconds. |
| `get()` | Function | Get a feature value. |
| `to_list()` | Function | Convert to list in specified order. |

## 3. Dependencies

See `src/codomyrmex/feature_store/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.feature_store import FeatureType, ValueType, FeatureDefinition, FeatureValue, FeatureVector
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k feature_store -v
```

## References

- [README.md](README.md) — Human-readable documentation
- [AGENTS.md](AGENTS.md) — Agent coordination guide
- [Source Code](../../../src/codomyrmex/feature_store/)
