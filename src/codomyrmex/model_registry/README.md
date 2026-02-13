# model_registry

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model versioning, metadata, and lifecycle management for ML models. Provides a central registry for registering model versions with framework, metrics, parameters, and tags. Supports lifecycle stage transitions (development, staging, production, archived) with automatic demotion of previous production versions, pluggable artifact storage backends, and version-level CRUD operations.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Enums

- **`ModelStage`** -- Lifecycle stages: DEVELOPMENT, STAGING, PRODUCTION, ARCHIVED
- **`ModelFramework`** -- Supported ML frameworks: SKLEARN, PYTORCH, TENSORFLOW, ONNX, CUSTOM

### Data Classes

- **`ModelMetrics`** -- Performance metrics container with standard fields (accuracy, precision, recall, F1, AUC-ROC, MSE, MAE) and a custom metrics dictionary
- **`ModelVersion`** -- A specific version of a model with stage, framework, artifact path, metrics, parameters, tags, and timestamps; provides `full_name` property (e.g., "model:1.0.0")
- **`RegisteredModel`** -- A registered model with multiple versions; provides `latest_version` (by creation date), `production_version`, and version lookup by string

### Storage

- **`ModelStore`** -- Abstract base class for model artifact storage with save, load, and delete operations
- **`FileModelStore`** -- File-system-based artifact storage organizing models as `{base_path}/{model_name}/{version}/model.bin`
- **`InMemoryModelStore`** -- Thread-safe in-memory artifact storage for testing

### Services

- **`ModelRegistry`** -- Central model registry; registers new versions (rejects duplicates), retrieves models/versions/latest/production, transitions lifecycle stages with automatic production demotion, lists all models and versions, deletes versions with artifact cleanup, and loads stored artifacts

## Directory Contents

- `models.py` -- Data models (ModelVersion, RegisteredModel, etc.)
- `stores.py` -- Storage backends (ModelStore, FileModelStore)
- `registry.py` -- Core registry logic (ModelRegistry)
- `__init__.py` -- Public API re-exports
- `README.md` -- This file
- `AGENTS.md` -- Agent integration documentation
- `API_SPECIFICATION.md` -- Programmatic API specification
- `MCP_TOOL_SPECIFICATION.md` -- Model Context Protocol tool definitions
- `PAI.md` -- PAI integration notes
- `SPEC.md` -- Module specification
- `py.typed` -- PEP 561 type stub marker

## Quick Start

```python
from codomyrmex.model_registry import ModelStage, ModelFramework, ModelMetrics

# Initialize ModelStage
instance = ModelStage()
```

## Navigation

- **Full Documentation**: [docs/modules/model_registry/](../../../docs/modules/model_registry/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
