"""
Model evaluation utilities for ML operations.

Provides metrics and evaluation frameworks for machine learning models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Tuple
from enum import Enum
import math


class TaskType(Enum):
    """Types of ML tasks."""
    BINARY_CLASSIFICATION = "binary_classification"
    MULTICLASS_CLASSIFICATION = "multiclass_classification"
    REGRESSION = "regression"
    RANKING = "ranking"
    SEQUENCE = "sequence"


@dataclass
class EvaluationResult:
    """Result of model evaluation."""
    metrics: Dict[str, float]
    task_type: TaskType
    sample_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "task_type": self.task_type.value,
            "sample_count": self.sample_count,
            "metadata": self.metadata,
        }


class Metric(ABC):
    """Abstract base class for evaluation metrics."""
    
    name: str
    
    @abstractmethod
    def compute(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        **kwargs
    ) -> float:
        """Compute the metric."""
        pass


class AccuracyMetric(Metric):
    """Classification accuracy."""
    
    name = "accuracy"
    
    def compute(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        **kwargs
    ) -> float:
        if not y_true:
            return 0.0
        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        return correct / len(y_true)


class PrecisionMetric(Metric):
    """Precision for binary classification."""
    
    name = "precision"
    
    def __init__(self, positive_class: Any = 1):
        self.positive_class = positive_class
    
    def compute(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        **kwargs
    ) -> float:
        tp = sum(1 for t, p in zip(y_true, y_pred) 
                 if t == self.positive_class and p == self.positive_class)
        fp = sum(1 for t, p in zip(y_true, y_pred) 
                 if t != self.positive_class and p == self.positive_class)
        
        if tp + fp == 0:
            return 0.0
        return tp / (tp + fp)


class RecallMetric(Metric):
    """Recall for binary classification."""
    
    name = "recall"
    
    def __init__(self, positive_class: Any = 1):
        self.positive_class = positive_class
    
    def compute(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        **kwargs
    ) -> float:
        tp = sum(1 for t, p in zip(y_true, y_pred) 
                 if t == self.positive_class and p == self.positive_class)
        fn = sum(1 for t, p in zip(y_true, y_pred) 
                 if t == self.positive_class and p != self.positive_class)
        
        if tp + fn == 0:
            return 0.0
        return tp / (tp + fn)


class F1Metric(Metric):
    """F1 score for binary classification."""
    
    name = "f1"
    
    def __init__(self, positive_class: Any = 1):
        self.precision = PrecisionMetric(positive_class)
        self.recall = RecallMetric(positive_class)
    
    def compute(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        **kwargs
    ) -> float:
        p = self.precision.compute(y_true, y_pred)
        r = self.recall.compute(y_true, y_pred)
        
        if p + r == 0:
            return 0.0
        return 2 * (p * r) / (p + r)


class ConfusionMatrix:
    """Confusion matrix for classification."""
    
    def __init__(self, y_true: List[Any], y_pred: List[Any]):
        self.classes = sorted(set(y_true) | set(y_pred))
        self.class_to_idx = {c: i for i, c in enumerate(self.classes)}
        
        n = len(self.classes)
        self.matrix = [[0] * n for _ in range(n)]
        
        for t, p in zip(y_true, y_pred):
            i = self.class_to_idx[t]
            j = self.class_to_idx[p]
            self.matrix[i][j] += 1
    
    def get_cell(self, true_class: Any, pred_class: Any) -> int:
        """Get count for a specific cell."""
        i = self.class_to_idx.get(true_class, -1)
        j = self.class_to_idx.get(pred_class, -1)
        if i < 0 or j < 0:
            return 0
        return self.matrix[i][j]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "classes": self.classes,
            "matrix": self.matrix,
        }
    
    def __str__(self) -> str:
        lines = ["Confusion Matrix:"]
        header = "       " + " ".join(f"{c:>6}" for c in self.classes)
        lines.append(header)
        
        for i, row in enumerate(self.matrix):
            row_str = f"{self.classes[i]:>6} " + " ".join(f"{v:>6}" for v in row)
            lines.append(row_str)
        
        return "\n".join(lines)


class MSEMetric(Metric):
    """Mean Squared Error for regression."""
    
    name = "mse"
    
    def compute(
        self,
        y_true: List[float],
        y_pred: List[float],
        **kwargs
    ) -> float:
        if not y_true:
            return 0.0
        return sum((t - p) ** 2 for t, p in zip(y_true, y_pred)) / len(y_true)


class MAEMetric(Metric):
    """Mean Absolute Error for regression."""
    
    name = "mae"
    
    def compute(
        self,
        y_true: List[float],
        y_pred: List[float],
        **kwargs
    ) -> float:
        if not y_true:
            return 0.0
        return sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)


class RMSEMetric(Metric):
    """Root Mean Squared Error for regression."""
    
    name = "rmse"
    
    def compute(
        self,
        y_true: List[float],
        y_pred: List[float],
        **kwargs
    ) -> float:
        mse = MSEMetric().compute(y_true, y_pred)
        return math.sqrt(mse)


class R2Metric(Metric):
    """R-squared (coefficient of determination) for regression."""
    
    name = "r2"
    
    def compute(
        self,
        y_true: List[float],
        y_pred: List[float],
        **kwargs
    ) -> float:
        if not y_true:
            return 0.0
        
        mean_true = sum(y_true) / len(y_true)
        ss_tot = sum((t - mean_true) ** 2 for t in y_true)
        ss_res = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
        
        if ss_tot == 0:
            return 0.0
        
        return 1 - (ss_res / ss_tot)


class AUCROCMetric(Metric):
    """Area Under ROC Curve for binary classification."""
    
    name = "auc_roc"
    
    def compute(
        self,
        y_true: List[int],
        y_scores: List[float],
        **kwargs
    ) -> float:
        if not y_true:
            return 0.0
        
        # Sort by scores descending
        sorted_pairs = sorted(zip(y_scores, y_true), reverse=True)
        
        n_pos = sum(1 for _, y in sorted_pairs if y == 1)
        n_neg = len(sorted_pairs) - n_pos
        
        if n_pos == 0 or n_neg == 0:
            return 0.5
        
        auc = 0.0
        tp = 0
        
        for _, y in sorted_pairs:
            if y == 1:
                tp += 1
            else:
                auc += tp
        
        return auc / (n_pos * n_neg)


class ModelEvaluator:
    """Evaluator for machine learning models."""
    
    def __init__(self, task_type: TaskType):
        self.task_type = task_type
        self.metrics: List[Metric] = self._get_default_metrics()
    
    def _get_default_metrics(self) -> List[Metric]:
        """Get default metrics for the task type."""
        if self.task_type in (TaskType.BINARY_CLASSIFICATION, TaskType.MULTICLASS_CLASSIFICATION):
            return [
                AccuracyMetric(),
                PrecisionMetric(),
                RecallMetric(),
                F1Metric(),
            ]
        elif self.task_type == TaskType.REGRESSION:
            return [
                MSEMetric(),
                MAEMetric(),
                RMSEMetric(),
                R2Metric(),
            ]
        return []
    
    def add_metric(self, metric: Metric) -> 'ModelEvaluator':
        """Add a metric to the evaluator."""
        self.metrics.append(metric)
        return self
    
    def evaluate(
        self,
        y_true: List[Any],
        y_pred: List[Any],
        **kwargs
    ) -> EvaluationResult:
        """Evaluate predictions against ground truth."""
        results = {}
        
        for metric in self.metrics:
            try:
                value = metric.compute(y_true, y_pred, **kwargs)
                results[metric.name] = round(value, 6)
            except Exception as e:
                results[metric.name] = None
        
        return EvaluationResult(
            metrics=results,
            task_type=self.task_type,
            sample_count=len(y_true),
            metadata=kwargs,
        )
    
    def cross_validate(
        self,
        X: List[Any],
        y: List[Any],
        model_fn,
        n_folds: int = 5,
    ) -> List[EvaluationResult]:
        """Perform k-fold cross validation."""
        fold_size = len(X) // n_folds
        results = []
        
        for i in range(n_folds):
            # Split data
            start = i * fold_size
            end = start + fold_size if i < n_folds - 1 else len(X)
            
            X_test = X[start:end]
            y_test = y[start:end]
            X_train = X[:start] + X[end:]
            y_train = y[:start] + y[end:]
            
            # Train and predict
            model = model_fn()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            # Evaluate
            result = self.evaluate(y_test, y_pred, fold=i)
            results.append(result)
        
        return results


def create_evaluator(task_type: str) -> ModelEvaluator:
    """Factory function to create evaluators."""
    type_map = {
        "binary": TaskType.BINARY_CLASSIFICATION,
        "multiclass": TaskType.MULTICLASS_CLASSIFICATION,
        "regression": TaskType.REGRESSION,
        "ranking": TaskType.RANKING,
    }
    
    task = type_map.get(task_type)
    if not task:
        raise ValueError(f"Unknown task type: {task_type}")
    
    return ModelEvaluator(task)


__all__ = [
    "TaskType",
    "EvaluationResult",
    "Metric",
    "AccuracyMetric",
    "PrecisionMetric",
    "RecallMetric",
    "F1Metric",
    "ConfusionMatrix",
    "MSEMetric",
    "MAEMetric",
    "RMSEMetric",
    "R2Metric",
    "AUCROCMetric",
    "ModelEvaluator",
    "create_evaluator",
]
