"""Model Operations module for Codomyrmex.

Provides ML model operations including:
- Dataset management and sanitization
- Fine-tuning job management
- Model evaluation and metrics

Submodules:
    feature_store: Consolidated feature store capabilities.
    optimization: Consolidated optimization capabilities.
    registry: Consolidated registry capabilities.
    evaluation: Consolidated evaluation capabilities."""

import json
import uuid
from collections.abc import Callable
from typing import Any, Optional

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# Submodule exports
from . import evaluation, feature_store, optimization, registry, training

# Import evaluation components (scorer/benchmark/quality + metrics patterns)
try:
    from .evaluation import (
        BenchmarkCase,
        BenchmarkResult,
        BenchmarkSuite,
        CompositeScorer,
        ContainsScorer,
        DimensionScore,
        ExactMatchScorer,
        LengthScorer,
        QualityAnalyzer,
        QualityDimension,
        QualityReport,
        RegexScorer,
        Scorer,
        SuiteResult,
        WeightedScorer,
        analyze_quality,
        create_default_scorer,
    )
    _EVALUATION_AVAILABLE = True
except ImportError:
    _EVALUATION_AVAILABLE = False

# Metric classes (always available — pure Python, no external deps)
from .evaluation import (
    AccuracyMetric,
    AUCROCMetric,
    ConfusionMatrix,
    EvaluationResult,
    F1Metric,
    MAEMetric,
    Metric,
    ModelEvaluator,
    MSEMetric,
    PrecisionMetric,
    R2Metric,
    RecallMetric,
    RMSEMetric,
    TaskType,
    create_evaluator,
)

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

    def __init__(self, data: list[dict[str, Any]] = None):
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
            True if all examples have required keys.
            Accepts both prompt/completion and messages formats.
        """
        if not self.data:
            return True

        for example in self.data:
            has_prompt_completion = "prompt" in example and "completion" in example
            has_messages = "messages" in example
            if not (has_prompt_completion or has_messages):
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
        with open(path) as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return cls(data=data)

    def __len__(self) -> int:
        """len ."""
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
    def strip_keys(dataset: Dataset, keys: list[str]) -> Dataset:
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
        self.job_id: str | None = None
        self.status: str = "pending"

    def run(self) -> str:
        """
        Start the fine-tuning job.

        Returns:
            Job ID
        """
        self.job_id = f"ft-{uuid.uuid4().hex[:8]}"
        self.status = "running"
        return self.job_id

    def refresh_status(self) -> str:
        """
        Get current job status. Transitions running jobs to completed.

        Returns:
            Status string
        """
        if self.status == "running":
            self.status = "completed"
        return self.status

class Evaluator:
    """
    Model output evaluator with customizable metrics.
    """

    def __init__(self, metrics: dict[str, Callable] = None):
        """
        Initialize evaluator.

        Args:
            metrics: Dictionary of metric name to metric function
        """
        self.metrics = metrics or {}

    def evaluate(
        self,
        predictions: list[str],
        references: list[str],
    ) -> dict[str, float]:
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
def exact_match_metric(predictions: list[str], references: list[str]) -> float:
    """Calculate exact match ratio (strips whitespace before comparison)."""
    if not predictions:
        return 0.0
    matches = sum(1 for p, r in zip(predictions, references, strict=False) if p.strip() == r.strip())
    return matches / len(predictions)

def length_ratio_metric(predictions: list[str], references: list[str]) -> float:
    """Calculate average length ratio."""
    if not predictions:
        return 0.0

    ratios = []
    for p, r in zip(predictions, references, strict=False):
        if len(r) > 0:
            ratios.append(len(p) / len(r))
        else:
            ratios.append(1.0 if len(p) == 0 else 0.0)

    return sum(ratios) / len(ratios)

def cli_commands():
    """Return CLI commands for the model_ops module."""
    return {
        "pipelines": {
            "help": "List ML pipelines",
            "handler": lambda **kwargs: print(
                "Model Operations Pipelines\n"
                "  Available pipelines:\n"
                "    - Dataset preparation (Dataset, DatasetSanitizer)\n"
                "    - Fine-tuning (FineTuningJob)\n"
                "    - Evaluation (Scorer, BenchmarkSuite, QualityAnalyzer)\n"
                f"  Evaluation available: {_EVALUATION_AVAILABLE}"
            ),
        },
        "status": {
            "help": "Show pipeline status",
            "handler": lambda **kwargs: print(
                f"Model Ops v{__version__}\n"
                f"  Datasets submodule: {'available' if datasets is not None else 'not available'}\n"
                f"  Fine-tuning submodule: {'available' if fine_tuning is not None else 'not available'}\n"
                f"  Evaluation submodule: {'available' if _EVALUATION_AVAILABLE else 'not available'}\n"
                "  Training submodule: available\n"
                "  Status: ready"
            ),
        },
    }

__all__ = [
    "feature_store",
    "optimization",
    "registry",
    # CLI integration
    "cli_commands",
    # Submodules
    "evaluation",
    "training",
    # Core classes
    "Dataset",
    "DatasetSanitizer",
    "FineTuningJob",
    "Evaluator",
    # Evaluation components (scorer/benchmark/quality)
    "Scorer",
    "ExactMatchScorer",
    "ContainsScorer",
    "LengthScorer",
    "RegexScorer",
    "CompositeScorer",
    "WeightedScorer",
    "create_default_scorer",
    "BenchmarkCase",
    "BenchmarkResult",
    "BenchmarkSuite",
    "SuiteResult",
    "QualityDimension",
    "DimensionScore",
    "QualityReport",
    "QualityAnalyzer",
    "analyze_quality",
    # Metric functions
    "exact_match_metric",
    "length_ratio_metric",
    # Metric classes
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

__version__ = "0.1.0"

