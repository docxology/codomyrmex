"""Model evaluation benchmarks and scoring logic."""

from typing import List, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class Evaluator:
    """Orchestrates model evaluation against a set of benchmarks."""
    
    def __init__(self, metrics: Dict[str, Callable[[str, str], float]]):
        self.metrics = metrics

    def evaluate(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Run evaluation metrics on predictions vs references."""
        if len(predictions) != len(references):
            raise ValueError("Predictions and references must have the same length")
            
        results = {}
        for name, metric_fn in self.metrics.items():
            scores = [metric_fn(p, r) for p, r in zip(predictions, references)]
            results[name] = sum(scores) / len(scores) if scores else 0.0
            
        return results

def exact_match_metric(pred: str, ref: str) -> float:
    return 1.0 if pred.strip() == ref.strip() else 0.0

def length_ratio_metric(pred: str, ref: str) -> float:
    if not ref: return 1.0
    return len(pred) / len(ref)
