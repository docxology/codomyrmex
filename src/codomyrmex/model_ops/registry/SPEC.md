# Registry — Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Central model registry for ML model versioning, lifecycle stage management, and artifact persistence. Models are registered with framework metadata, performance metrics, and training parameters. Stage transitions follow a lifecycle pipeline with automatic demotion rules. Artifact storage is abstracted behind a pluggable `ModelStore` interface with file-system and in-memory implementations.

## Architecture

Three-layer design: **models** (dataclasses and enums for version metadata), **stores** (abstract artifact backend with `FileModelStore` and `InMemoryModelStore`), and **registry** (thread-safe orchestration layer). `ModelRegistry` maintains an in-memory dictionary of `RegisteredModel` instances, each containing a list of `ModelVersion` objects. Artifacts are delegated to the `ModelStore` backend.

## Key Classes

### `ModelVersion`

| Field | Type | Description |
|-------|------|-------------|
| `version` | `str` | Semantic version string |
| `model_name` | `str` | Parent model name |
| `stage` | `ModelStage` | Current lifecycle stage |
| `framework` | `ModelFramework` | ML framework used |
| `metrics` | `ModelMetrics` | Performance metrics |
| `parameters` | `dict[str, Any]` | Training parameters |
| `tags` | `dict[str, str]` | Key-value tags |
| `artifact_path` | `str or None` | Path to stored artifact |
| `full_name` | property | `"{model_name}:{version}"` |

### `ModelRegistry`

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `name, version, framework, metrics, parameters, description, tags, artifact` | `ModelVersion` | Register a new version; raises `ValueError` on duplicate |
| `get_model` | `name: str` | `RegisteredModel or None` | Retrieve registered model by name |
| `get_version` | `name, version` | `ModelVersion or None` | Retrieve specific version |
| `get_latest` | `name: str` | `ModelVersion or None` | Latest version by `created_at` |
| `get_production_model` | `name: str` | `ModelVersion or None` | Version currently in PRODUCTION stage |
| `transition_stage` | `name, version, stage` | `ModelVersion or None` | Change stage; auto-archives previous production |
| `list_models` | — | `list[str]` | All registered model names |
| `list_versions` | `name: str` | `list[ModelVersion]` | All versions of a model |
| `delete_version` | `name, version` | `bool` | Remove version and its artifact |
| `load_artifact` | `name, version` | `bytes or None` | Load artifact bytes from store |

### `ModelStore` (ABC) and Implementations

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `save_artifact` | `model_name, version, artifact: bytes` | `str` | Save artifact, return storage path |
| `load_artifact` | `path: str` | `bytes` | Load artifact from path |
| `delete_artifact` | `path: str` | `bool` | Delete artifact at path |

**FileModelStore**: Stores at `{base_path}/{model_name}/{version}/model.bin`, creates directories automatically.

**InMemoryModelStore**: Thread-safe dict-based storage; `FileNotFoundError` on missing artifact load.

## Dependencies

- **Internal**: None
- **External**: Standard library only (`threading`, `datetime`, `pathlib`, `logging`, `dataclasses`, `enum`)

## Constraints

- Duplicate version registration raises `ValueError`.
- Production promotion automatically archives the previous production version.
- `RegisteredModel.latest_version` selects by `created_at` timestamp (not version string).
- `ModelMetrics.to_dict()` excludes `None`-valued standard metrics and merges `custom` dict.
- Zero-mock: real data only, `NotImplementedError` for unimplemented paths.

## Error Handling

- `ValueError` raised on duplicate version in `register()`.
- `FileNotFoundError` raised by `InMemoryModelStore.load_artifact()` for missing artifacts.
- `FileModelStore.delete_artifact()` catches `FileNotFoundError` and logs a warning, returning `False`.
- All errors logged before propagation.
