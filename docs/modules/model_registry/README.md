# Model Registry Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model versioning, metadata, and lifecycle management for ML models. Provides a central registry for registering model versions with associated metrics, parameters, and artifacts. Supports full lifecycle stage transitions (development, staging, production, archived), multiple ML framework types (sklearn, PyTorch, TensorFlow, ONNX, custom), and pluggable storage backends for model artifacts including file-based and in-memory stores.

## Key Features

- **Model Versioning**: Register and track multiple versions of each model with semantic version strings
- **Lifecycle Management**: Transition models through development, staging, production, and archived stages with automatic demotion of prior production versions
- **Performance Metrics**: Attach structured metrics (accuracy, precision, recall, F1, AUC-ROC, MSE, MAE, and custom) to each model version
- **Pluggable Storage**: Abstract `ModelStore` interface with `FileModelStore` (disk-based) and `InMemoryModelStore` (testing) implementations
- **Thread-Safe Operations**: All registry mutations protected with threading locks for concurrent access
- **Artifact Management**: Save, load, and delete serialized model artifacts through the storage backend
- **Framework Tracking**: Record which ML framework produced each model version

## Key Components

| Component | Description |
|-----------|-------------|
| `ModelRegistry` | Central registry for registering, querying, and managing model versions and their artifacts |
| `RegisteredModel` | A registered model entity containing multiple versions with latest/production lookups |
| `ModelVersion` | A specific version of a model with stage, framework, metrics, parameters, and tags |
| `ModelMetrics` | Dataclass for structured performance metrics (accuracy, precision, recall, F1, AUC-ROC, MSE, MAE, custom) |
| `ModelStage` | Enum of lifecycle stages: DEVELOPMENT, STAGING, PRODUCTION, ARCHIVED |
| `ModelFramework` | Enum of supported ML frameworks: SKLEARN, PYTORCH, TENSORFLOW, ONNX, CUSTOM |
| `ModelStore` | Abstract base class defining the storage backend interface (save, load, delete artifacts) |
| `FileModelStore` | File-system-based model artifact storage backend |
| `InMemoryModelStore` | In-memory model artifact storage for testing scenarios |

## Quick Start

```python
from codomyrmex.model_registry import (
    ModelRegistry, ModelFramework, ModelMetrics, ModelStage
)

# Create a registry (defaults to in-memory store)
registry = ModelRegistry()

# Register a model version with metrics
version = registry.register(
    name="my_classifier",
    version="1.0.0",
    framework=ModelFramework.SKLEARN,
    metrics=ModelMetrics(accuracy=0.95, f1_score=0.93),
    parameters={"n_estimators": 100},
    description="Random forest classifier v1",
)

# Query registered models
model = registry.get_model("my_classifier")
latest = model.latest_version
print(f"Latest: {latest.full_name}")  # "my_classifier:1.0.0"

# Promote to production
registry.transition_stage("my_classifier", "1.0.0", ModelStage.PRODUCTION)

# Retrieve production model
prod = registry.get_production_model("my_classifier")
print(f"Production: {prod.full_name}")
```

```python
from codomyrmex.model_registry import ModelRegistry, FileModelStore

# Use file-based storage for persistent artifacts
registry = ModelRegistry(store=FileModelStore("./model_artifacts"))

registry.register(
    name="my_model",
    version="2.0.0",
    artifact=b"serialized_model_bytes",
)

# Load artifact back
artifact = registry.load_artifact("my_model", "2.0.0")
```

## Related Modules

- [model_ops](../model_ops/) - Model operations including training, evaluation, and dataset management
- [observability_dashboard](../observability_dashboard/) - Monitor model performance metrics on dashboards

## Navigation

- **Source**: [src/codomyrmex/model_registry/](../../../src/codomyrmex/model_registry/)
- **Parent**: [docs/modules/](../README.md)
