# Feature Store

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

Typed, versioned, and thread-safe feature management for ML applications. Provides storage backends, feature grouping, validation, transforms, and batch ingestion for serving features at inference time.

## Quick Start

```python
from codomyrmex.feature_store import (
    FeatureDefinition, FeatureType, ValueType,
    InMemoryFeatureStore, FeatureService,
)

store = InMemoryFeatureStore()
store.register_feature(FeatureDefinition(
    name="user_age",
    feature_type=FeatureType.NUMERIC,
    value_type=ValueType.INT,
))
store.set_value("user_age", "user_123", 25)

value = store.get_value("user_age", "user_123")
print(value.value)  # 25
```

## Installation

```bash
uv sync
```

No optional extras are required for this module.

## Core Classes

| Class | Module | Description |
|-------|--------|-------------|
| `FeatureType` | `models` | Enum of feature categories: NUMERIC, CATEGORICAL, EMBEDDING, TEXT, TIMESTAMP, BOOLEAN |
| `ValueType` | `models` | Enum of value data types: INT, FLOAT, STRING, BOOL, LIST, DICT |
| `FeatureDefinition` | `models` | Dataclass defining a feature with name, types, description, default value, tags, and metadata |
| `FeatureValue` | `models` | Dataclass holding a feature value with entity ID, timestamp, and version tracking |
| `FeatureVector` | `models` | Collection of feature values for a single entity, with dict-like access and list conversion |
| `FeatureGroup` | `models` | Named group of related `FeatureDefinition` instances with entity type and tags |
| `FeatureStore` | `store` | Abstract base class defining the storage backend interface |
| `InMemoryFeatureStore` | `store` | Thread-safe in-memory storage backend for development and testing |
| `FeatureTransform` | `service` | Chainable per-feature transforms applied before serving |
| `FeatureService` | `service` | High-level service combining store, groups, transforms, and batch ingestion |

## Built-in Feature Definitions

Two common definitions are provided out of the box:

- `USER_ID_FEATURE` -- categorical string feature for user identifiers
- `TIMESTAMP_FEATURE` -- timestamp string feature for event timestamps

## API Reference

### FeatureDefinition

```python
FeatureDefinition(
    name: str,
    feature_type: FeatureType,
    value_type: ValueType,
    description: str = "",
    default_value: Any = None,
    tags: list[str] = [],
    metadata: dict[str, Any] = {},
)

def validate_value(self, value: Any) -> bool
def to_dict(self) -> dict[str, Any]
```

### InMemoryFeatureStore

```python
def register_feature(self, definition: FeatureDefinition) -> None
def get_feature_definition(self, name: str) -> Optional[FeatureDefinition]
def set_value(self, feature_name: str, entity_id: str, value: Any) -> None
def get_value(self, feature_name: str, entity_id: str) -> Optional[FeatureValue]
def get_vector(self, entity_id: str, feature_names: List[str]) -> FeatureVector
def list_features(self) -> List[FeatureDefinition]
def delete_value(self, feature_name: str, entity_id: str) -> bool
```

### FeatureTransform

```python
def add(self, feature_name: str, func: Callable[[Any], Any]) -> FeatureTransform
def apply(self, vector: FeatureVector) -> FeatureVector
```

### FeatureService

```python
FeatureService(
    store: Optional[FeatureStore] = None,
    transform: Optional[FeatureTransform] = None,
)

def register_group(self, group: FeatureGroup) -> None
def register_feature(self, definition: FeatureDefinition) -> None
def ingest(self, features: Dict[str, Any], entity_id: str) -> None
def ingest_batch(self, batch: List[Dict[str, Any]], entity_id_field: str = "entity_id") -> int
def get_features(self, entity_id: str, feature_names: List[str], apply_transform: bool = True) -> FeatureVector
def get_group_features(self, entity_id: str, group_name: str) -> FeatureVector
def list_groups(self) -> List[str]
```

## MCP Tools

The feature store module exposes tools for the Model Context Protocol (MCP) to manage features directly from agents:

- `feature_store_register_feature`: Registers a new feature definition in the store.
- `feature_store_ingest`: Ingests feature values for a specific entity.
- `feature_store_get_features`: Retrieves feature values for an entity.

## Exceptions

| Exception | Description |
|-----------|-------------|
| `FeatureStoreError` | Base exception for all feature store operations |
| `FeatureNotFoundError` | Feature definition or value not found |
| `FeatureRegistrationError` | Feature registration failed (e.g., invalid definition) |
| `FeatureValidationError` | Value does not match the feature definition type |

## PAI Integration

The Feature Store maps to the **BUILD** and **EXECUTE** phases of the PAI Algorithm. Use it to define, populate, and serve ML features during model training and inference workflows.

## Testing

```bash
uv run pytest src/codomyrmex/tests/unit/feature_store/
```

## Zero-Mock Policy

All tests run against real `InMemoryFeatureStore` instances. No mocks, stubs, or fake data.

---

[AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
