# Model Ops — Functional Specification

**Module**: `codomyrmex.model_ops`  
**Version**: v0.1.0  
**Status**: Active

## 1. Overview

Model Operations module for Codomyrmex.

## 2. Architecture

### Components

| Component | Type | Description |
|-----------|------|-------------|
| `Dataset` | Class | A dataset for ML model operations. |
| `DatasetSanitizer` | Class | Utilities for cleaning and filtering datasets. |
| `FineTuningJob` | Class | Fine-tuning job management. |
| `Evaluator` | Class | Model output evaluator with customizable metrics. |
| `exact_match_metric()` | Function | Calculate exact match ratio (strips whitespace before comparison). |
| `length_ratio_metric()` | Function | Calculate average length ratio. |
| `validate()` | Function | Validate the dataset. |
| `to_jsonl()` | Function | Export dataset to JSONL file. |
| `from_file()` | Function | Load dataset from JSONL file. |

### Submodule Structure

- `datasets/` — Dataset management submodule.
- `evaluation/` — Model evaluation utilities for ML operations.
- `fine_tuning/` — Fine-tuning submodule.
- `training/` — Training utilities submodule.

### Source Files

- `evaluators.py`

## 3. Dependencies

See `src/codomyrmex/model_ops/__init__.py` for import dependencies.

## 4. Public API

```python
from codomyrmex.model_ops import Dataset, DatasetSanitizer, FineTuningJob, Evaluator
```

## 5. Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_ops -v
```
