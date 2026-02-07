# Model Ops Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model Operations module for Codomyrmex.

## Key Features

- **Dataset** — A dataset for ML model operations.
- **DatasetSanitizer** — Utilities for cleaning and filtering datasets.
- **FineTuningJob** — Fine-tuning job management.
- **Evaluator** — Model output evaluator with customizable metrics.
- `exact_match_metric()` — Calculate exact match ratio (strips whitespace before comparison).
- `length_ratio_metric()` — Calculate average length ratio.
- `validate()` — Validate the dataset.
- `to_jsonl()` — Export dataset to JSONL file.

## Submodules

| Submodule | Description |
|-----------|-------------|
| `datasets` | Dataset management submodule. |
| `evaluation` | Model evaluation utilities for ML operations. |
| `fine_tuning` | Fine-tuning submodule. |
| `training` | Training utilities submodule. |

## Quick Start

```python
from codomyrmex.model_ops import Dataset, DatasetSanitizer, FineTuningJob

# Initialize
instance = Dataset()
```

## API Reference

### Classes

| Class | Description |
|-------|-------------|
| `Dataset` | A dataset for ML model operations. |
| `DatasetSanitizer` | Utilities for cleaning and filtering datasets. |
| `FineTuningJob` | Fine-tuning job management. |
| `Evaluator` | Model output evaluator with customizable metrics. |

### Functions

| Function | Description |
|----------|-------------|
| `exact_match_metric()` | Calculate exact match ratio (strips whitespace before comparison). |
| `length_ratio_metric()` | Calculate average length ratio. |
| `validate()` | Validate the dataset. |
| `to_jsonl()` | Export dataset to JSONL file. |
| `from_file()` | Load dataset from JSONL file. |
| `filter_by_length()` | Filter examples by content length. |
| `strip_keys()` | Remove specified keys from all examples. |
| `run()` | Start the fine-tuning job. |
| `refresh_status()` | Get current job status. Transitions running jobs to completed. |
| `evaluate()` | Evaluate predictions against references. |

## Directory Contents

| File | Description |
|------|-------------|
| `README.md` | This documentation |
| `AGENTS.md` | Agent coordination guide |
| `SPEC.md` | Technical specification |

## Navigation

- **Source**: [src/codomyrmex/model_ops/](../../../src/codomyrmex/model_ops/)
- **Parent**: [Modules](../README.md)
