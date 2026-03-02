"""Model evaluation benchmarks and scoring logic."""

import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)

class Evaluator:
    """Orchestrates model evaluation against a set of benchmarks."""

    def __init__(self, metrics: dict[str, Callable[[str, str], float]]):
        """Initialize this instance."""
        self.metrics = metrics

    def evaluate(self, predictions: list[str], references: list[str]) -> dict[str, float]:
        """Run evaluation metrics on predictions vs references."""
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have the same length")

        results = {}
        for name, metric_fn in self.metrics.items():
            scores = [metric_fn(p, r) for p, r in zip(predictions, references)]
            results[name] = sum(scores) / len(scores) if scores else 0.0

        return results

def exact_match_metric(pred: str, ref: str) -> float:
    """exact Match Metric ."""
    return 1.0 if pred.strip() == ref.strip() else 0.0

def length_ratio_metric(pred: str, ref: str) -> float:
    """length Ratio Metric ."""
    if not ref: return 1.0
    return len(pred) / len(ref)
