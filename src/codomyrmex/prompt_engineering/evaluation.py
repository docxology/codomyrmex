"""
Prompt Evaluation and Scoring

Provides tools for evaluating prompt-response pairs against
configurable criteria with weighted scoring.
"""

from __future__ import annotations

import re
import statistics
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


@dataclass
class EvaluationCriteria:
    """
    A single evaluation criterion with a scoring function and weight.

    The scorer_fn takes (prompt: str, response: str) and returns a float
    between 0.0 and 1.0.
    """

    name: str
    weight: float
    scorer_fn: Callable[[str, str], float]
    description: str = ""

    def score(self, prompt: str, response: str) -> float:
        """
        Run this criterion's scorer on a prompt-response pair.

        Args:
            prompt: The prompt string.
            response: The model response string.

        Returns:
            Score between 0.0 and 1.0.
        """
        raw_score = self.scorer_fn(prompt, response)
        return max(0.0, min(1.0, raw_score))


@dataclass
class EvaluationResult:
    """Complete result of evaluating a prompt-response pair."""

    prompt: str
    response: str
    scores: dict[str, float] = field(default_factory=dict)
    weighted_score: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert evaluation result to dictionary."""
        return {
            "prompt": self.prompt[:200] + "..." if len(self.prompt) > 200 else self.prompt,
            "response": self.response[:200] + "..." if len(self.response) > 200 else self.response,
            "scores": self.scores,
            "weighted_score": self.weighted_score,
            "details": self.details,
        }


# -- Built-in scorer functions --

def score_response_length(prompt: str, response: str) -> float:
    """
    Score based on response length relative to a reasonable range.

    Responses between 50-500 words score highest. Very short or very
    long responses score lower.
    """
    word_count = len(response.split())
    if word_count < 10:
        return 0.2
    if word_count < 50:
        return 0.5 + (word_count - 10) / 80
    if word_count <= 500:
        return 1.0
    if word_count <= 1000:
        return 1.0 - (word_count - 500) / 1000
    return 0.5


def score_relevance(prompt: str, response: str) -> float:
    """
    Score relevance by measuring keyword overlap between prompt and response.

    Extracts significant words (4+ chars) from the prompt and checks
    how many appear in the response.
    """
    prompt_words = set(
        w.lower() for w in re.findall(r"\b\w{4,}\b", prompt)
    )
    if not prompt_words:
        return 1.0

    response_lower = response.lower()
    found = sum(1 for w in prompt_words if w in response_lower)
    return found / len(prompt_words)


def score_structure(prompt: str, response: str) -> float:
    """
    Score response structure quality.

    Awards points for having paragraphs, bullet points, headers,
    numbered lists, and code blocks - indicators of well-organized output.
    """
    score = 0.0
    checks = 0

    # Has multiple paragraphs
    checks += 1
    if response.count("\n\n") >= 1:
        score += 1.0

    # Has bullet points or numbered lists
    checks += 1
    if re.search(r"^[\s]*[-*]\s", response, re.MULTILINE):
        score += 1.0
    elif re.search(r"^[\s]*\d+[.)]\s", response, re.MULTILINE):
        score += 1.0

    # Has some form of headers or emphasis
    checks += 1
    if re.search(r"(^#+\s|^\*\*|^__)", response, re.MULTILINE):
        score += 1.0

    # Not a wall of text (has line breaks)
    checks += 1
    lines = response.strip().split("\n")
    if len(lines) > 1:
        score += 1.0

    return score / checks if checks > 0 else 0.5


def score_completeness(prompt: str, response: str) -> float:
    """
    Score whether the response addresses the apparent intent of the prompt.

    Checks for question answering patterns, requested sections, and
    whether the response appears truncated.
    """
    score = 0.0
    checks = 0

    # If prompt asks a question, response should not be empty
    checks += 1
    if "?" in prompt:
        if len(response.strip()) > 20:
            score += 1.0
        elif len(response.strip()) > 0:
            score += 0.5
    else:
        score += 1.0  # Not a question, give full marks

    # Response should not appear truncated
    checks += 1
    stripped = response.rstrip()
    if stripped and stripped[-1] in ".!?)\":;>]":
        score += 1.0
    elif stripped:
        score += 0.5

    # Response should have meaningful content
    checks += 1
    if len(response.split()) >= 10:
        score += 1.0
    elif len(response.split()) >= 3:
        score += 0.5

    return score / checks if checks > 0 else 0.5


# -- Default criteria presets --

def get_default_criteria() -> list[EvaluationCriteria]:
    """
    Get the default set of evaluation criteria.

    Returns:
        List of EvaluationCriteria with balanced weights.
    """
    return [
        EvaluationCriteria(
            name="relevance",
            weight=0.35,
            scorer_fn=score_relevance,
            description="Measures keyword overlap between prompt and response",
        ),
        EvaluationCriteria(
            name="completeness",
            weight=0.30,
            scorer_fn=score_completeness,
            description="Checks if response fully addresses the prompt",
        ),
        EvaluationCriteria(
            name="structure",
            weight=0.20,
            scorer_fn=score_structure,
            description="Evaluates response formatting and organization",
        ),
        EvaluationCriteria(
            name="length",
            weight=0.15,
            scorer_fn=score_response_length,
            description="Scores response length appropriateness",
        ),
    ]


class PromptEvaluator:
    """
    Evaluates prompt-response pairs against configurable criteria.

    Supports weighted scoring, batch evaluation, and comparison between
    multiple responses to the same prompt.
    """

    def __init__(
        self,
        criteria: list[EvaluationCriteria] | None = None,
    ) -> None:
        """
        Initialize the evaluator.

        Args:
            criteria: List of evaluation criteria. If None, uses defaults.
        """
        self._criteria = criteria if criteria is not None else get_default_criteria()

    @property
    def criteria(self) -> list[EvaluationCriteria]:
        """Get the current evaluation criteria."""
        return list(self._criteria)

    def add_criteria(self, criteria: EvaluationCriteria) -> None:
        """
        Add an evaluation criterion.

        Args:
            criteria: The criterion to add.
        """
        self._criteria.append(criteria)

    def remove_criteria(self, name: str) -> bool:
        """
        Remove a criterion by name.

        Args:
            name: Name of the criterion to remove.

        Returns:
            True if found and removed, False otherwise.
        """
        for i, c in enumerate(self._criteria):
            if c.name == name:
                self._criteria.pop(i)
                return True
        return False

    def evaluate(
        self,
        prompt: str,
        response: str,
        criteria: list[EvaluationCriteria] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a prompt-response pair against all criteria.

        Args:
            prompt: The prompt string.
            response: The model's response string.
            criteria: Optional override criteria. If None, uses instance criteria.

        Returns:
            EvaluationResult with per-criterion scores and weighted total.
        """
        active_criteria = criteria if criteria is not None else self._criteria

        scores: dict[str, float] = {}
        weighted_sum = 0.0
        total_weight = 0.0

        for criterion in active_criteria:
            criterion_score = criterion.score(prompt, response)
            scores[criterion.name] = round(criterion_score, 4)
            weighted_sum += criterion_score * criterion.weight
            total_weight += criterion.weight

        weighted_score = weighted_sum / total_weight if total_weight > 0 else 0.0

        return EvaluationResult(
            prompt=prompt,
            response=response,
            scores=scores,
            weighted_score=round(weighted_score, 4),
            details={
                "criteria_count": len(active_criteria),
                "total_weight": round(total_weight, 4),
            },
        )

    def evaluate_batch(
        self,
        pairs: list[tuple[str, str]],
    ) -> list[EvaluationResult]:
        """
        Evaluate multiple prompt-response pairs.

        Args:
            pairs: List of (prompt, response) tuples.

        Returns:
            List of EvaluationResult objects.
        """
        return [self.evaluate(prompt, response) for prompt, response in pairs]

    def compare_responses(
        self,
        prompt: str,
        responses: list[str],
    ) -> dict[str, Any]:
        """
        Compare multiple responses to the same prompt.

        Args:
            prompt: The shared prompt.
            responses: List of different response strings to compare.

        Returns:
            Dictionary with individual results, rankings, and statistics.
        """
        results = [self.evaluate(prompt, resp) for resp in responses]

        ranked = sorted(
            enumerate(results),
            key=lambda x: x[1].weighted_score,
            reverse=True,
        )

        all_scores = [r.weighted_score for r in results]

        return {
            "results": [r.to_dict() for r in results],
            "ranking": [
                {"index": idx, "weighted_score": results[idx].weighted_score}
                for idx, _ in ranked
            ],
            "best_index": ranked[0][0] if ranked else None,
            "statistics": {
                "mean": round(statistics.mean(all_scores), 4) if all_scores else 0.0,
                "stdev": round(statistics.stdev(all_scores), 4) if len(all_scores) > 1 else 0.0,
                "min": round(min(all_scores), 4) if all_scores else 0.0,
                "max": round(max(all_scores), 4) if all_scores else 0.0,
            },
        }

    def criteria_names(self) -> list[str]:
        """
        List the names of all active criteria.

        Returns:
            Sorted list of criterion names.
        """
        return sorted(c.name for c in self._criteria)


__all__ = [
    "EvaluationCriteria",
    "EvaluationResult",
    "PromptEvaluator",
    "get_default_criteria",
    "score_relevance",
    "score_response_length",
    "score_structure",
    "score_completeness",
]
