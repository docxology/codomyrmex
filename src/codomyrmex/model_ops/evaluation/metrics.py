"""
Classification and regression metrics for model evaluation.

Provides real, functional metric implementations:
- Classification: Accuracy, Precision, Recall, F1, AUC-ROC, ConfusionMatrix
- Regression: MSE, MAE, RMSE, R²
- Orchestration: ModelEvaluator, EvaluationResult, create_evaluator
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskType(Enum):
    """Model evaluation task types."""
    BINARY_CLASSIFICATION = "binary_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REGRESSION = "regression"


@dataclass
class EvaluationResult:
    """Result of a model evaluation."""
    metrics: dict[str, float]
    task_type: TaskType
    sample_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "metrics": self.metrics,
            "task_type": self.task_type.value,
            "sample_count": self.sample_count,
            "metadata": self.metadata,
        }


class Metric(ABC):
    """Abstract base class for evaluation metrics."""

    @property
    @abstractmethod
    def name(self) -> str:
        """name ."""
        ...

    @abstractmethod
    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        ...


class AccuracyMetric(Metric):
    """Classification accuracy (correct / total)."""

    @property
    def name(self) -> str:
        """name ."""
        return "accuracy"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        if not y_true:
            return 0.0
        return sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)


class PrecisionMetric(Metric):
    """Precision for a specific positive class."""

    def __init__(self, positive_class: Any = 1):
        """Initialize this instance."""
        self.positive_class = positive_class

    @property
    def name(self) -> str:
        """name ."""
        return "precision"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        tp = sum(1 for t, p in zip(y_true, y_pred) if p == self.positive_class and t == self.positive_class)
        fp = sum(1 for t, p in zip(y_true, y_pred) if p == self.positive_class and t != self.positive_class)
        if tp + fp == 0:
            return 0.0
        return tp / (tp + fp)


class RecallMetric(Metric):
    """Recall for a specific positive class."""

    def __init__(self, positive_class: Any = 1):
        """Initialize this instance."""
        self.positive_class = positive_class

    @property
    def name(self) -> str:
        """name ."""
        return "recall"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        tp = sum(1 for t, p in zip(y_true, y_pred) if p == self.positive_class and t == self.positive_class)
        fn = sum(1 for t, p in zip(y_true, y_pred) if p != self.positive_class and t == self.positive_class)
        if tp + fn == 0:
            return 0.0
        return tp / (tp + fn)


class F1Metric(Metric):
    """F1 score for a specific positive class."""

    def __init__(self, positive_class: Any = 1):
        """Initialize this instance."""
        self.positive_class = positive_class

    @property
    def name(self) -> str:
        """name ."""
        return "f1"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        p = PrecisionMetric(self.positive_class).compute(y_true, y_pred)
        r = RecallMetric(self.positive_class).compute(y_true, y_pred)
        if p + r == 0:
            return 0.0
        return 2 * p * r / (p + r)


class MSEMetric(Metric):
    """Mean Squared Error."""

    @property
    def name(self) -> str:
        """name ."""
        return "mse"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        if not y_true:
            return 0.0
        return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / len(y_true)


class MAEMetric(Metric):
    """Mean Absolute Error."""

    @property
    def name(self) -> str:
        """name ."""
        return "mae"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        if not y_true:
            return 0.0
        return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)


class RMSEMetric(Metric):
    """Root Mean Squared Error."""

    @property
    def name(self) -> str:
        """name ."""
        return "rmse"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        return math.sqrt(MSEMetric().compute(y_true, y_pred))


class R2Metric(Metric):
    """R-squared (coefficient of determination)."""

    @property
    def name(self) -> str:
        """name ."""
        return "r2"

    def compute(self, y_true: list, y_pred: list) -> float:
        """compute ."""
        if not y_true:
            return 0.0
        mean_true = sum(y_true) / len(y_true)
        ss_tot = sum((t - mean_true) ** 2 for t in y_true)
        ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        return 1.0 - ss_res / ss_tot


class AUCROCMetric(Metric):
    """Area Under ROC Curve (Wilcoxon-Mann-Whitney statistic)."""

    @property
    def name(self) -> str:
        """name ."""
        return "auc_roc"

    def compute(self, y_true: list, y_scores: list) -> float:
        """compute ."""
        positives = [(s, t) for s, t in zip(y_scores, y_true) if t == 1]
        negatives = [(s, t) for s, t in zip(y_scores, y_true) if t == 0]
        if not positives or not negatives:
            return 0.0
        count = 0
        total = len(positives) * len(negatives)
        for ps, _ in positives:
            for ns, _ in negatives:
                if ps > ns:
                    count += 1
                elif ps == ns:
                    count += 0.5
        return count / total


class ConfusionMatrix:
    """Confusion matrix for classification tasks."""

    def __init__(self, y_true: list, y_pred: list):
        """Initialize this instance."""
        self.y_true = y_true
        self.y_pred = y_pred
        self.classes = sorted(set(y_true) | set(y_pred))
        self._matrix = self._build()

    def _build(self) -> dict[tuple, int]:
        """Build the target artifact."""
        matrix: dict[tuple, int] = {}
        for t, p in zip(self.y_true, self.y_pred):
            key = (t, p)
            matrix[key] = matrix.get(key, 0) + 1
        return matrix

    def get_cell(self, true_label: Any, pred_label: Any) -> int:
        """get Cell ."""
        return self._matrix.get((true_label, pred_label), 0)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        matrix_rows = []
        for tc in self.classes:
            row = [self.get_cell(tc, pc) for pc in self.classes]
            matrix_rows.append(row)
        return {"classes": self.classes, "matrix": matrix_rows}

    def __str__(self) -> str:
        """str ."""
        lines = ["Confusion Matrix:"]
        header = "     " + " ".join(f"{c:>5}" for c in self.classes)
        lines.append(header)
        for tc in self.classes:
            row = " ".join(f"{self.get_cell(tc, pc):>5}" for pc in self.classes)
            lines.append(f"{tc:>5} {row}")
        return "\n".join(lines)


class ModelEvaluator:
    """High-level evaluator that selects appropriate metrics by task type."""

    def __init__(self, task_type: TaskType):
        """Initialize this instance."""
        self.task_type = task_type
        self.metrics: list[Metric] = self._default_metrics()

    def _default_metrics(self) -> list[Metric]:
        """default Metrics ."""
        if self.task_type in (TaskType.BINARY_CLASSIFICATION, TaskType.MULTICLASS_CLASSIFICATION):
            return [AccuracyMetric(), PrecisionMetric(), RecallMetric(), F1Metric()]
        elif self.task_type == TaskType.REGRESSION:
            return [MSEMetric(), MAEMetric(), RMSEMetric(), R2Metric()]
        return []

    def add_metric(self, metric: Metric) -> None:
        """add Metric ."""
        self.metrics.append(metric)

    def evaluate(self, y_true: list, y_pred: list) -> EvaluationResult:
        """evaluate ."""
        results = {}
        for metric in self.metrics:
            results[metric.name] = metric.compute(y_true, y_pred)
        return EvaluationResult(
            metrics=results,
            task_type=self.task_type,
            sample_count=len(y_true),
        )


def create_evaluator(task_type_str: str) -> ModelEvaluator:
    """Factory function to create a ModelEvaluator from a task type string.

    Args:
        task_type_str: One of 'binary', 'multiclass', 'regression'.

    Returns:
        Configured ModelEvaluator.

    Raises:
        ValueError: If the task type is not recognized.
    """
    mapping = {
        "binary": TaskType.BINARY_CLASSIFICATION,
        "multiclass": TaskType.MULTICLASS_CLASSIFICATION,
        "regression": TaskType.REGRESSION,
    }
    if task_type_str not in mapping:
        raise ValueError(f"Unknown task type: {task_type_str}")
    return ModelEvaluator(mapping[task_type_str])


__all__ = [
    "TaskType",
    "EvaluationResult",
    "Metric",
    "AccuracyMetric",
    "PrecisionMetric",
    "RecallMetric",
    "F1Metric",
    "MSEMetric",
    "MAEMetric",
    "RMSEMetric",
    "R2Metric",
    "AUCROCMetric",
    "ConfusionMatrix",
    "ModelEvaluator",
    "create_evaluator",
]
