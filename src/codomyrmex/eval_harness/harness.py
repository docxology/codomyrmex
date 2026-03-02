"""LLM Eval Harness -- standardized evaluation framework for language models.

Provides:
- EvalTask: Named evaluation task with examples (input/target pairs)
- EvalResult: Task-level results with score, latency, and per-example details
- ExactMatchMetric: Binary exact match after normalization
- F1Metric: Token-level F1 score
- EvalHarness: Runs a model function against multiple tasks
"""
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np


@dataclass
class EvalTask:
    """A single evaluation task with examples."""

    name: str
    examples: list[dict]  # Each: {"input": str, "target": str}
    metric: str = "exact_match"
    description: str = ""


@dataclass
class EvalResult:
    """Results from evaluating one task."""

    task_name: str
    num_examples: int
    score: float
    metric: str
    latency_ms_mean: float
    details: list[dict] = field(default_factory=list)


def normalize_answer(answer: str) -> str:
    """Normalize for exact match: lowercase, strip whitespace."""
    return answer.strip().lower()


class ExactMatchMetric:
    """Binary exact match after normalization."""

    @staticmethod
    def score(predictions: list[str], targets: list[str]) -> float:
        """Compute exact match accuracy.

        Args:
            predictions: Model predictions
            targets: Gold targets

        Returns:
            Fraction of exact matches
        """
        correct = sum(
            normalize_answer(p) == normalize_answer(t)
            for p, t in zip(predictions, targets, strict=False)
        )
        return correct / len(targets) if targets else 0.0


class F1Metric:
    """Token-level F1 score."""

    @staticmethod
    def _f1_single(pred: str, target: str) -> float:
        """Compute F1 for a single prediction-target pair."""
        pred_tokens = normalize_answer(pred).split()
        target_tokens = normalize_answer(target).split()
        if not pred_tokens or not target_tokens:
            return float(normalize_answer(pred) == normalize_answer(target))
        common = set(pred_tokens) & set(target_tokens)
        if not common:
            return 0.0
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(target_tokens)
        return 2 * precision * recall / (precision + recall)

    @classmethod
    def score(cls, predictions: list[str], targets: list[str]) -> float:
        """Compute mean token-level F1 score.

        Args:
            predictions: Model predictions
            targets: Gold targets

        Returns:
            Mean F1 score across examples
        """
        if not targets:
            return 0.0
        return float(
            np.mean([cls._f1_single(p, t) for p, t in zip(predictions, targets, strict=False)])
        )


class EvalHarness:
    """Standardized LLM evaluation harness.

    Runs a model function against multiple tasks and reports metrics.
    """

    def __init__(self, model_fn: Callable[[str], str] = None):
        """Initialize the harness.

        Args:
            model_fn: Function that takes input text and returns generated text.
                      If None, uses a stub that returns the input (identity).
        """
        self.model_fn = model_fn or (lambda x: x)
        self.results: list[EvalResult] = []

    def evaluate_task(self, task: EvalTask) -> EvalResult:
        """Run evaluation on a single task.

        Args:
            task: EvalTask with examples and metric specification

        Returns:
            EvalResult with score, latency, and per-example details
        """
        predictions = []
        latencies = []

        for example in task.examples:
            t0 = time.perf_counter()
            pred = self.model_fn(example["input"])
            latencies.append((time.perf_counter() - t0) * 1000)
            predictions.append(pred)

        targets = [ex["target"] for ex in task.examples]

        # Compute metric
        if task.metric == "f1":
            score = F1Metric.score(predictions, targets)
        else:  # default exact_match
            score = ExactMatchMetric.score(predictions, targets)

        details = [
            {
                "input": ex["input"],
                "target": t,
                "prediction": p,
                "correct": normalize_answer(p) == normalize_answer(t),
            }
            for ex, t, p in zip(task.examples, targets, predictions, strict=False)
        ]

        result = EvalResult(
            task_name=task.name,
            num_examples=len(task.examples),
            score=score,
            metric=task.metric,
            latency_ms_mean=float(np.mean(latencies)),
            details=details,
        )
        self.results.append(result)
        return result

    def evaluate_all(self, tasks: list[EvalTask]) -> dict:
        """Evaluate all tasks and return summary.

        Args:
            tasks: List of EvalTask objects

        Returns:
            dict with: num_tasks, mean_score, results (per-task summaries)
        """
        results = [self.evaluate_task(t) for t in tasks]
        return {
            "num_tasks": len(results),
            "mean_score": float(np.mean([r.score for r in results])),
            "results": [
                {
                    "task": r.task_name,
                    "score": r.score,
                    "metric": r.metric,
                    "n_examples": r.num_examples,
                    "latency_ms": r.latency_ms_mean,
                }
                for r in results
            ],
        }
