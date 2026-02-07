# Feature Store Module — Agent Coordination

## Purpose

ML feature management, storage, and retrieval.

## Key Capabilities

- **FeatureType**: Types of features.
- **ValueType**: Data types for feature values.
- **FeatureDefinition**: Definition of a feature.
- **FeatureValue**: A feature value with metadata.
- **FeatureVector**: A collection of feature values for an entity.
- `full_name()`: Get fully qualified name.
- `to_dict()`: Convert to dictionary.
- `age_seconds()`: Get age of this value in seconds.

## Agent Usage Patterns

```python
from codomyrmex.feature_store import FeatureType

# Agent initializes feature store
instance = FeatureType()
```

## Integration Points

- **Source**: [src/codomyrmex/feature_store/](../../../src/codomyrmex/feature_store/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k feature_store -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
