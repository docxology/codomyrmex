# Model Registry Module — Agent Coordination

## Purpose

Model versioning, metadata, and lifecycle management.

## Key Capabilities

- **ModelStage**: Lifecycle stages for models.
- **ModelFramework**: Supported ML frameworks.
- **ModelMetrics**: Performance metrics for a model.
- **ModelVersion**: A specific version of a model.
- **RegisteredModel**: A registered model with multiple versions.
- `to_dict()`: Convert to dictionary.
- `full_name()`: Get full model name with version.
- `to_dict()`: Convert to dictionary.

## Agent Usage Patterns

```python
from codomyrmex.model_registry import ModelStage

# Agent initializes model registry
instance = ModelStage()
```

## Integration Points

- **Source**: [src/codomyrmex/model_registry/](../../../src/codomyrmex/model_registry/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)
