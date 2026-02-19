# Evaluation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Model evaluation utilities for ML operations. Provides a pluggable metrics framework and evaluation harness for classification and regression tasks, including accuracy, precision, recall, F1, confusion matrix, MSE, MAE, RMSE, R-squared, and AUC-ROC metrics with k-fold cross-validation support.

## Key Exports

### Enums

- **`TaskType`** -- ML task types: BINARY_CLASSIFICATION, MULTICLASS_CLASSIFICATION, REGRESSION, RANKING, SEQUENCE

### Data Structures

- **`EvaluationResult`** -- Container for evaluation metrics, task type, sample count, and metadata

### Classification Metrics

- **`Metric`** -- Abstract base class defining the `compute(y_true, y_pred)` interface
- **`AccuracyMetric`** -- Classification accuracy (correct predictions / total)
- **`PrecisionMetric`** -- Precision for binary classification with configurable positive class
- **`RecallMetric`** -- Recall for binary classification with configurable positive class
- **`F1Metric`** -- F1 score combining precision and recall
- **`ConfusionMatrix`** -- N-class confusion matrix with cell access and string rendering
- **`AUCROCMetric`** -- Area Under ROC Curve using trapezoidal approximation

### Regression Metrics

- **`MSEMetric`** -- Mean Squared Error
- **`MAEMetric`** -- Mean Absolute Error
- **`RMSEMetric`** -- Root Mean Squared Error
- **`R2Metric`** -- R-squared (coefficient of determination)

### Evaluator

- **`ModelEvaluator`** -- Orchestrates evaluation with auto-selected default metrics per task type, supports custom metric addition, and provides k-fold cross-validation
- **`create_evaluator()`** -- Factory function to create evaluators by task type string ("binary", "multiclass", "regression", "ranking")

## Directory Contents

- `__init__.py` - All metric classes, evaluator, and factory function (409 lines)
- `evaluators.py` - Additional evaluator implementations
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.model_ops.evaluation import ModelEvaluator, TaskType, ConfusionMatrix

evaluator = ModelEvaluator(TaskType.BINARY_CLASSIFICATION)
result = evaluator.evaluate(y_true=[1, 0, 1, 1], y_pred=[1, 0, 0, 1])
print(result.metrics)  # {'accuracy': 0.75, 'precision': 1.0, 'recall': 0.666667, 'f1': 0.8}

cm = ConfusionMatrix(y_true=[1, 0, 1, 1], y_pred=[1, 0, 0, 1])
print(cm)
```

## Navigation

- **Parent Module**: [model_ops](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
