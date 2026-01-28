"""Model Operations module for Codomyrmex.

Provides ML model operations including:
- Dataset management and sanitization
- Fine-tuning job management
- Model evaluation and metrics
"""

from typing import Any, Callable, Dict, List, Optional
import json
import uuid

# Import evaluation components
from .evaluation import (
    TaskType,
    EvaluationResult,
    Metric,
    AccuracyMetric,
    PrecisionMetric,
    RecallMetric,
    F1Metric,
    ConfusionMatrix,
    MSEMetric,
    MAEMetric,
    RMSEMetric,
    R2Metric,
    AUCROCMetric,
    ModelEvaluator,
    create_evaluator,
)

# Submodule exports
from . import evaluation
from . import training

# Try optional submodules
try:
    from . import datasets
except ImportError:
    datasets = None

try:
    from . import fine_tuning
except ImportError:
    fine_tuning = None


class Dataset:
    """
    A dataset for ML model operations.
    
    Manages collections of training/evaluation data with validation
    and I/O capabilities.
    """
    
    def __init__(self, data: List[Dict[str, Any]] = None):
        """
        Initialize a dataset.
        
        Args:
            data: List of data examples (dictionaries)
        """
        self.data = data or []
    
    def validate(self) -> bool:
        """
        Validate the dataset.
        
        Returns:
            True if all examples have required keys
        """
        if not self.data:
            return True
        
        required_keys = {"prompt", "completion"}
        for example in self.data:
            if not required_keys.issubset(example.keys()):
                return False
        return True
    
    def to_jsonl(self, path: str) -> None:
        """
        Export dataset to JSONL file.
        
        Args:
            path: Output file path
        """
        with open(path, "w") as f:
            for example in self.data:
                f.write(json.dumps(example) + "\n")
    
    @classmethod
    def from_file(cls, path: str) -> 'Dataset':
        """
        Load dataset from JSONL file.
        
        Args:
            path: Input file path
            
        Returns:
            New Dataset instance
        """
        data = []
        with open(path, "r") as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return cls(data=data)
    
    def __len__(self) -> int:
        return len(self.data)


class DatasetSanitizer:
    """
    Utilities for cleaning and filtering datasets.
    """
    
    @staticmethod
    def filter_by_length(
        dataset: Dataset,
        min_length: int = 1,
        max_length: int = 10000,
    ) -> Dataset:
        """
        Filter examples by content length.
        
        Args:
            dataset: Input dataset
            min_length: Minimum total content length
            max_length: Maximum total content length
            
        Returns:
            Filtered dataset
        """
        filtered = []
        for example in dataset.data:
            content = str(example.get("prompt", "")) + str(example.get("completion", ""))
            if min_length <= len(content) <= max_length:
                filtered.append(example)
        return Dataset(data=filtered)
    
    @staticmethod
    def strip_keys(dataset: Dataset, keys: List[str]) -> Dataset:
        """
        Remove specified keys from all examples.
        
        Args:
            dataset: Input dataset
            keys: Keys to remove
            
        Returns:
            Dataset with keys stripped
        """
        stripped = []
        for example in dataset.data:
            new_example = {k: v for k, v in example.items() if k not in keys}
            stripped.append(new_example)
        return Dataset(data=stripped)


class FineTuningJob:
    """
    Fine-tuning job management.
    
    Simulates fine-tuning operations for ML models.
    """
    
    def __init__(
        self,
        base_model: str = "gpt-3.5-turbo",
        dataset: Dataset = None,
    ):
        """
        Initialize a fine-tuning job.
        
        Args:
            base_model: Base model identifier
            dataset: Training dataset
        """
        self.base_model = base_model
        self.dataset = dataset
        self.job_id: Optional[str] = None
        self.status: str = "pending"
    
    def run(self) -> str:
        """
        Start the fine-tuning job.
        
        Returns:
            Job ID
        """
        self.job_id = f"ft-{uuid.uuid4().hex[:8]}"
        self.status = "running"
        # Simulate quick completion
        self.status = "succeeded"
        return self.job_id
    
    def refresh_status(self) -> str:
        """
        Get current job status.
        
        Returns:
            Status string
        """
        return self.status


class Evaluator:
    """
    Model output evaluator with customizable metrics.
    """
    
    def __init__(self, metrics: Dict[str, Callable] = None):
        """
        Initialize evaluator.
        
        Args:
            metrics: Dictionary of metric name to metric function
        """
        self.metrics = metrics or {}
    
    def evaluate(
        self,
        predictions: List[str],
        references: List[str],
    ) -> Dict[str, float]:
        """
        Evaluate predictions against references.
        
        Args:
            predictions: Model predictions
            references: Ground truth references
            
        Returns:
            Dictionary of metric scores
        """
        results = {}
        for name, metric_fn in self.metrics.items():
            try:
                results[name] = metric_fn(predictions, references)
            except Exception:
                results[name] = 0.0
        return results


# Convenience metric functions
def exact_match_metric(predictions: List[str], references: List[str]) -> float:
    """Calculate exact match ratio."""
    if not predictions:
        return 0.0
    matches = sum(1 for p, r in zip(predictions, references) if p == r)
    return matches / len(predictions)


def length_ratio_metric(predictions: List[str], references: List[str]) -> float:
    """Calculate average length ratio."""
    if not predictions:
        return 0.0
    
    ratios = []
    for p, r in zip(predictions, references):
        if len(r) > 0:
            ratios.append(len(p) / len(r))
        else:
            ratios.append(1.0 if len(p) == 0 else 0.0)
    
    return sum(ratios) / len(ratios)


__all__ = [
    # Submodules
    "evaluation",
    "training",
    # Core classes
    "Dataset",
    "DatasetSanitizer",
    "FineTuningJob",
    "Evaluator",
    # Evaluation components
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
    # Metric functions
    "exact_match_metric",
    "length_ratio_metric",
]

__version__ = "0.1.0"

