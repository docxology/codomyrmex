# Model Registry — Functional Specification

**Module**: `codomyrmex.model_registry`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Model versioning, metadata, and lifecycle management.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `ModelStage` | Class | Lifecycle stages for models. |
| `ModelFramework` | Class | Supported ML frameworks. |
| `ModelMetrics` | Class | Performance metrics for a model. |
| `ModelVersion` | Class | A specific version of a model. |
| `RegisteredModel` | Class | A registered model with multiple versions. |
| `ModelStore` | Class | Base class for model storage backends. |
| `FileModelStore` | Class | File-based model storage. |
| `InMemoryModelStore` | Class | In-memory model storage for testing. |
| `ModelRegistry` | Class | Central model registry for versioning and management. |
| `to_dict()` | Function | Convert to dictionary. |
| `full_name()` | Function | Get full model name with version. |
| `to_dict()` | Function | Convert to dictionary. |
| `latest_version()` | Function | Get the latest version. |
| `production_version()` | Function | Get the production version. |

## 3. Dependencies

See `src/codomyrmex/model_registry/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.model_registry import ModelStage, ModelFramework, ModelMetrics, ModelVersion, RegisteredModel
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_registry -v
```
