# Codomyrmex Agents — src/codomyrmex/model_ops/registry

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Model registry sub-module for versioning, lifecycle management, and artifact storage of ML models. Supports registering model versions with framework metadata, performance metrics, and training parameters. Manages stage transitions (Development -> Staging -> Production -> Archived) with automatic demotion of previous production versions. Provides pluggable storage backends for model artifacts.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `models.py` | `ModelStage` | Enum: DEVELOPMENT, STAGING, PRODUCTION, ARCHIVED |
| `models.py` | `ModelFramework` | Enum: SKLEARN, PYTORCH, TENSORFLOW, ONNX, CUSTOM |
| `models.py` | `ModelMetrics` | Dataclass for performance metrics (accuracy, precision, recall, f1, auc_roc, mse, mae, custom) |
| `models.py` | `ModelVersion` | Dataclass for a versioned model with stage, framework, metrics, parameters, tags, artifact path |
| `models.py` | `RegisteredModel` | Container for all versions of a named model; provides `latest_version`, `production_version`, `get_version()` |
| `stores.py` | `ModelStore` (ABC) | Abstract storage backend: `save_artifact`, `load_artifact`, `delete_artifact` |
| `stores.py` | `FileModelStore` | File-system backed storage at `{base_path}/{model_name}/{version}/model.bin` |
| `stores.py` | `InMemoryModelStore` | Thread-safe in-memory artifact storage for testing |
| `registry.py` | `ModelRegistry` | Central registry: register versions, stage transitions, artifact load/save, model/version listing and deletion |

## Operating Contracts

- `ModelRegistry.register()` raises `ValueError` if a version string already exists for a given model name.
- `transition_stage()` to `PRODUCTION` automatically demotes the current production version to `ARCHIVED`.
- `ModelRegistry` uses `threading.Lock` for all mutating operations.
- `FileModelStore` creates directory trees on first artifact save via `mkdir(parents=True)`.
- `InMemoryModelStore` uses `threading.Lock` for artifact mutations.
- `delete_version()` also deletes the associated artifact via the store backend.
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`threading`, `datetime`, `pathlib`, `dataclasses`, `enum`)
- **Used by**: MLOps pipelines needing model versioning and promotion workflows

## Navigation

- **Parent**: [model_ops](../README.md)
- **Root**: [Root](../../../../README.md)
