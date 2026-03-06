"""Scorer implementations: ExactMatch, Contains, Length, Composite."""

from abc import ABC, abstractmethod


class Scorer(ABC):
    """Base class for scoring outputs."""

    @abstractmethod
    def score(self, output: str, expected: str | None = None) -> float:
        """Score an output. Returns value between 0.0 and 1.0."""


class ExactMatchScorer(Scorer):
    """Score based on exact match."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def score(self, output: str, expected: str | None = None) -> float:
        """Score."""
        if expected is None:
            return 1.0
        if self.case_sensitive:
            return 1.0 if output.strip() == expected.strip() else 0.0
        return 1.0 if output.strip().lower() == expected.strip().lower() else 0.0


class ContainsScorer(Scorer):
    """Score based on whether output contains expected text."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def score(self, output: str, expected: str | None = None) -> float:
        """Score."""
        if expected is None:
            return 1.0
        if self.case_sensitive:
            return 1.0 if expected in output else 0.0
        return 1.0 if expected.lower() in output.lower() else 0.0


class LengthScorer(Scorer):
    """Score based on output length relative to target."""

    def __init__(self, target_length: int, tolerance: float = 0.3):
        self.target_length = target_length
        self.tolerance = tolerance

    def score(self, output: str, expected: str | None = None) -> float:
        """Score."""
        length = len(output)
        diff = abs(length - self.target_length) / self.target_length
        if diff <= self.tolerance:
            return 1.0 - (diff / self.tolerance) * 0.5
        return max(0.0, 0.5 - (diff - self.tolerance))


class CompositeScorer(Scorer):
    """Combine multiple scorers with weights."""

    def __init__(self, scorers: list[tuple[Scorer, float]]):
        """Args: scorers: List of (scorer, weight) tuples."""
        self.scorers = scorers
        total_weight = sum(w for _, w in scorers)
        self.normalized_scorers = [(s, w / total_weight) for s, w in scorers]

    def score(self, output: str, expected: str | None = None) -> float:
        """Score."""
        total = 0.0
        for scorer, weight in self.normalized_scorers:
            total += scorer.score(output, expected) * weight
        return total
