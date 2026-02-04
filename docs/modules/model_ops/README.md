# Model Operations Module Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Structured and scalable framework for ML model operations. Provides dataset management and sanitization, fine-tuning job orchestration, and model evaluation with customizable metrics. The module supports reproducible model optimization workflows including data preparation (JSONL I/O, validation, filtering), training job lifecycle management, and comprehensive output evaluation using both built-in and user-defined metric functions.

## Key Features

- **Dataset Management**: Load, validate, export, and filter ML datasets in JSONL format with prompt/completion structure
- **Dataset Sanitization**: Filter examples by content length and strip unwanted keys from dataset entries
- **Fine-Tuning Job Management**: Create and manage fine-tuning jobs with unique job IDs and lifecycle tracking
- **Custom Evaluation**: Evaluate model predictions against references using pluggable metric functions
- **Built-in Metrics**: Exact match ratio and length ratio metrics available out of the box
- **Advanced Evaluation Submodule**: Full evaluation framework with accuracy, precision, recall, F1, AUC-ROC, MSE, MAE, RMSE, R2, and confusion matrix support
- **Training Submodule**: Dedicated training orchestration capabilities

## Key Components

| Component | Description |
|-----------|-------------|
| `Dataset` | Core dataset class for managing collections of training/evaluation data with validation and JSONL I/O |
| `DatasetSanitizer` | Utilities for cleaning and filtering datasets by length and stripping keys |
| `FineTuningJob` | Fine-tuning job lifecycle management with job ID generation and status tracking |
| `Evaluator` | Model output evaluator with customizable metric functions |
| `exact_match_metric` | Built-in metric function calculating exact match ratio between predictions and references |
| `length_ratio_metric` | Built-in metric function calculating average length ratio between predictions and references |
| `ModelEvaluator` | Advanced evaluator from the evaluation submodule supporting multiple task types |
| `create_evaluator` | Factory function for creating evaluators with pre-configured metrics |
| `TaskType` | Enum defining evaluation task types (from evaluation submodule) |
| `EvaluationResult` | Structured result container from the evaluation submodule |
| `AccuracyMetric` | Accuracy metric implementation |
| `PrecisionMetric` | Precision metric implementation |
| `RecallMetric` | Recall metric implementation |
| `F1Metric` | F1-score metric implementation |
| `ConfusionMatrix` | Confusion matrix computation |
| `MSEMetric` | Mean squared error metric |
| `MAEMetric` | Mean absolute error metric |
| `RMSEMetric` | Root mean squared error metric |
| `R2Metric` | R-squared (coefficient of determination) metric |
| `AUCROCMetric` | Area under the ROC curve metric |
| `evaluation` | Submodule for comprehensive model evaluation |
| `training` | Submodule for training orchestration |

## Quick Start

```python
from codomyrmex.model_ops import Dataset, DatasetSanitizer, Evaluator, exact_match_metric

# Create and validate a dataset
dataset = Dataset(data=[
    {"prompt": "What is 2+2?", "completion": "4"},
    {"prompt": "Capital of France?", "completion": "Paris"},
])
assert dataset.validate()

# Export to JSONL
dataset.to_jsonl("training_data.jsonl")

# Load from file
loaded = Dataset.from_file("training_data.jsonl")

# Filter dataset by content length
sanitizer = DatasetSanitizer()
filtered = sanitizer.filter_by_length(dataset, min_length=5, max_length=500)

# Evaluate model outputs
evaluator = Evaluator(metrics={"exact_match": exact_match_metric})
scores = evaluator.evaluate(
    predictions=["4", "London"],
    references=["4", "Paris"],
)
print(scores)  # {"exact_match": 0.5}
```

```python
from codomyrmex.model_ops import FineTuningJob, Dataset

# Create and run a fine-tuning job
dataset = Dataset(data=[{"prompt": "Hello", "completion": "Hi there!"}])
job = FineTuningJob(base_model="gpt-3.5-turbo", dataset=dataset)
job_id = job.run()
print(f"Job {job_id}: {job.refresh_status()}")
```

```python
from codomyrmex.model_ops import create_evaluator, TaskType

# Use the advanced evaluation submodule
evaluator = create_evaluator(TaskType.CLASSIFICATION)
```

## Related Modules

- [model_registry](../model_registry/) - Model versioning and lifecycle management after training
- [prompt_testing](../prompt_testing/) - Systematic prompt evaluation and A/B testing

## Navigation

- **Source**: [src/codomyrmex/model_ops/](../../../src/codomyrmex/model_ops/)
- **Parent**: [docs/modules/](../README.md)
