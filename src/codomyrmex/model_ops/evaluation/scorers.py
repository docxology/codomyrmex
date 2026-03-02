"""
Output scoring functions for model evaluation.

Provides a protocol-based scoring system with composable scorers
for evaluating LLM outputs against reference values.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


class Scorer(ABC):
    """Abstract base class for output scorers.

    All scorers implement the score() method that compares an output
    against a reference value and returns a float between 0.0 and 1.0.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this scorer."""
        ...

    @abstractmethod
    def score(self, output: str, reference: str) -> float:
        """Score the output against the reference.

        Args:
            output: The model output to evaluate.
            reference: The reference/expected value to compare against.

        Returns:
            A float between 0.0 (no match) and 1.0 (perfect match).
        """
        ...

    def score_batch(self, pairs: list[tuple[str, str]]) -> list[float]:
        """Score multiple output/reference pairs.

        Args:
            pairs: List of (output, reference) tuples.

        Returns:
            List of scores corresponding to each pair.
        """
        return [self.score(output, reference) for output, reference in pairs]


class ExactMatchScorer(Scorer):
    """Scores 1.0 if output exactly matches reference, 0.0 otherwise.

    Args:
        case_sensitive: Whether comparison is case-sensitive. Defaults to True.
        strip_whitespace: Whether to strip leading/trailing whitespace
            before comparison. Defaults to True.
    """

    def __init__(
        self,
        case_sensitive: bool = True,
        strip_whitespace: bool = True,
    ) -> None:
        self._case_sensitive = case_sensitive
        self._strip_whitespace = strip_whitespace

    @property
    def name(self) -> str:
        """name ."""
        return "exact_match"

    def score(self, output: str, reference: str) -> float:
        """score ."""
        a = output
        b = reference

        if self._strip_whitespace:
            a = a.strip()
            b = b.strip()

        if not self._case_sensitive:
            a = a.lower()
            b = b.lower()

        return 1.0 if a == b else 0.0


class ContainsScorer(Scorer):
    """Scores 1.0 if the output contains the reference as a substring, 0.0 otherwise.

    Args:
        case_sensitive: Whether the substring search is case-sensitive.
            Defaults to False.
    """

    def __init__(self, case_sensitive: bool = False) -> None:
        self._case_sensitive = case_sensitive

    @property
    def name(self) -> str:
        """name ."""
        return "contains"

    def score(self, output: str, reference: str) -> float:
        """score ."""
        a = output
        b = reference

        if not self._case_sensitive:
            a = a.lower()
            b = b.lower()

        return 1.0 if b in a else 0.0


class LengthScorer(Scorer):
    """Scores based on output length relative to a target range.

    Returns 1.0 if the output length falls within [min_length, max_length].
    Returns a proportional score that decays linearly as the length moves
    away from the target range, reaching 0.0 at twice the deviation.

    The reference parameter is ignored; scoring is based solely on the
    output length and the configured target range.

    Args:
        min_length: Minimum acceptable character count.
        max_length: Maximum acceptable character count.
    """

    def __init__(self, min_length: int = 1, max_length: int = 500) -> None:
        if min_length < 0:
            raise ValueError("min_length must be non-negative")
        if max_length < min_length:
            raise ValueError("max_length must be >= min_length")

        self._min_length = min_length
        self._max_length = max_length

    @property
    def name(self) -> str:
        """name ."""
        return "length"

    def score(self, output: str, reference: str = "") -> float:
        """score ."""
        length = len(output)

        if self._min_length <= length <= self._max_length:
            return 1.0

        # Calculate how far outside the range we are
        range_size = max(self._max_length - self._min_length, 1)

        if length < self._min_length:
            deviation = self._min_length - length
        else:
            deviation = length - self._max_length

        # Score decays linearly; reaches 0.0 when deviation equals the range size
        score = max(0.0, 1.0 - (deviation / range_size))
        return round(score, 6)


class RegexScorer(Scorer):
    """Scores 1.0 if the output matches the reference as a regex pattern, 0.0 otherwise.

    The reference parameter is treated as a regex pattern.

    Args:
        flags: Regex flags to apply. Defaults to 0 (no flags).
        full_match: If True, the entire output must match the pattern.
            If False, the pattern just needs to be found somewhere in the output.
            Defaults to False.
    """

    def __init__(self, flags: int = 0, full_match: bool = False) -> None:
        self._flags = flags
        self._full_match = full_match

    @property
    def name(self) -> str:
        """name ."""
        return "regex"

    def score(self, output: str, reference: str) -> float:
        """score ."""
        try:
            pattern = re.compile(reference, self._flags)
        except re.error as e:
            logger.warning("Invalid regex pattern '%s': %s", reference, e)
            return 0.0

        if self._full_match:
            return 1.0 if pattern.fullmatch(output) else 0.0
        else:
            return 1.0 if pattern.search(output) else 0.0


@dataclass
class WeightedScorer:
    """A scorer paired with a weight for use in CompositeScorer."""
    scorer: Scorer
    weight: float = 1.0


class CompositeScorer(Scorer):
    """Combines multiple scorers with configurable weights.

    The final score is the weighted average of all constituent scorers.

    Args:
        scorers: List of WeightedScorer instances. Can also be populated
            via add_scorer().
    """

    def __init__(self, scorers: list[WeightedScorer] | None = None) -> None:
        self._scorers: list[WeightedScorer] = list(scorers) if scorers else []

    @property
    def name(self) -> str:
        """name ."""
        return "composite"

    def add_scorer(self, scorer: Scorer, weight: float = 1.0) -> CompositeScorer:
        """Add a scorer with an associated weight.

        Args:
            scorer: The scorer to add.
            weight: The weight for this scorer. Must be positive.

        Returns:
            Self for method chaining.

        Raises:
            ValueError: If weight is not positive.
        """
        if weight <= 0:
            raise ValueError("Weight must be positive")
        self._scorers.append(WeightedScorer(scorer=scorer, weight=weight))
        return self

    def score(self, output: str, reference: str) -> float:
        """score ."""
        if not self._scorers:
            return 0.0

        total_weight = sum(ws.weight for ws in self._scorers)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            ws.scorer.score(output, reference) * ws.weight
            for ws in self._scorers
        )
        return round(weighted_sum / total_weight, 6)

    def score_detailed(
        self, output: str, reference: str
    ) -> dict[str, Any]:
        """Score with detailed per-scorer breakdown.

        Args:
            output: The model output.
            reference: The reference value.

        Returns:
            Dictionary with overall score and per-scorer details.
        """
        if not self._scorers:
            return {"overall": 0.0, "scorers": []}

        total_weight = sum(ws.weight for ws in self._scorers)
        details = []
        weighted_sum = 0.0

        for ws in self._scorers:
            individual_score = ws.scorer.score(output, reference)
            weighted_sum += individual_score * ws.weight
            details.append({
                "name": ws.scorer.name,
                "score": individual_score,
                "weight": ws.weight,
                "weighted_score": round(
                    individual_score * ws.weight / total_weight, 6
                )
                if total_weight > 0
                else 0.0,
            })

        overall = round(weighted_sum / total_weight, 6) if total_weight > 0 else 0.0

        return {"overall": overall, "scorers": details}

    @property
    def scorer_count(self) -> int:
        """Number of scorers in this composite."""
        return len(self._scorers)


def create_default_scorer() -> CompositeScorer:
    """Create a default composite scorer with sensible defaults.

    Returns a CompositeScorer configured with:
        - ExactMatchScorer (weight 2.0)
        - ContainsScorer (weight 1.0)
        - LengthScorer (weight 0.5)
    """
    return CompositeScorer([
        WeightedScorer(ExactMatchScorer(case_sensitive=False), weight=2.0),
        WeightedScorer(ContainsScorer(), weight=1.0),
        WeightedScorer(LengthScorer(min_length=1, max_length=1000), weight=0.5),
    ])


__all__ = [
    "Scorer",
    "ExactMatchScorer",
    "ContainsScorer",
    "LengthScorer",
    "RegexScorer",
    "CompositeScorer",
    "WeightedScorer",
    "create_default_scorer",
]
