# Model Ops Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

ML model operations module providing dataset management, fine-tuning job orchestration, and model evaluation with pluggable metrics. The `Dataset` class manages training/evaluation data collections with JSONL I/O and validation for prompt/completion and messages formats. `DatasetSanitizer` filters and cleans datasets by length and key stripping. `FineTuningJob` simulates fine-tuning workflows with status tracking. The `evaluation` submodule provides a comprehensive metrics framework with accuracy, precision, recall, F1, confusion matrix, MSE, MAE, RMSE, R-squared, and AUC-ROC.

## Key Exports

### Submodules

- **`evaluation`** -- Comprehensive model evaluation framework with typed metrics
- **`training`** -- Training pipeline configuration and execution

### Core Classes

- **`Dataset`** -- Collection of training/evaluation examples with JSONL I/O, validation for prompt/completion and messages formats
- **`DatasetSanitizer`** -- Utilities for filtering datasets by content length and stripping unwanted keys
- **`FineTuningJob`** -- Fine-tuning job lifecycle management with status tracking (pending/running/completed)
- **`Evaluator`** -- Model output evaluator with pluggable custom metric functions

### Evaluation Framework

- **`TaskType`** -- Enum of evaluation task types (classification, regression, etc.)
- **`EvaluationResult`** -- Container for evaluation results across metrics
- **`Metric`** -- Base metric class for evaluation
- **`AccuracyMetric`** -- Classification accuracy metric
- **`PrecisionMetric`** -- Classification precision metric
- **`RecallMetric`** -- Classification recall metric
- **`F1Metric`** -- F1 score (harmonic mean of precision and recall)
- **`ConfusionMatrix`** -- Confusion matrix computation and analysis
- **`MSEMetric`** -- Mean Squared Error for regression tasks
- **`MAEMetric`** -- Mean Absolute Error for regression tasks
- **`RMSEMetric`** -- Root Mean Squared Error for regression tasks
- **`R2Metric`** -- R-squared (coefficient of determination) for regression
- **`AUCROCMetric`** -- Area Under ROC Curve for binary classification
- **`ModelEvaluator`** -- High-level evaluator orchestrating multiple metrics
- **`create_evaluator()`** -- Factory function to create a configured ModelEvaluator

### Convenience Metric Functions

- **`exact_match_metric()`** -- Calculate exact match ratio between predictions and references (strips whitespace)
- **`length_ratio_metric()`** -- Calculate average length ratio between predictions and references

## Directory Contents

- `__init__.py` - Module entry point with Dataset, DatasetSanitizer, FineTuningJob, Evaluator, and metric functions
- `evaluation/` - Comprehensive metrics framework (Metric base class, typed metrics, ModelEvaluator)
- `training/` - Training pipeline configuration and execution
- `datasets/` - Additional dataset utilities and loaders
- `fine_tuning/` - Fine-tuning job management extensions
- `evaluators.py` - Legacy evaluator implementations

## Quick Start

```python
from codomyrmex.model_ops import Dataset, DatasetSanitizer

# Create a Dataset instance
dataset = Dataset()

# Use DatasetSanitizer for additional functionality
datasetsanitizer = DatasetSanitizer()
```

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k model_ops -v
```

## Consolidated Sub-modules

The following modules have been consolidated into this module as sub-packages:

| Sub-module | Description |
|------------|-------------|
| **`evaluation/`** | LLM output scoring, benchmark suites, A/B comparison |
| **`registry/`** | Model versioning and artifact management |
| **`optimization/`** | Model quantization, ONNX export, inference acceleration |
| **`vector_store/`** | ML feature management and storage |

Original standalone modules remain as backward-compatible re-export wrappers.

## Navigation

- **Full Documentation**: [docs/modules/model_ops/](../../../docs/modules/model_ops/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
