"""Prompt Testing Evaluators — output evaluation strategies.

Provides:
- ExactMatchEvaluator: binary match with case option
- ContainsEvaluator: substring containment scoring
- SimilarityEvaluator: fuzzy string similarity (Jaccard)
- LengthEvaluator: check output length against expected bounds
- RegexEvaluator: validate output against regex patterns
- CompositeEvaluator: weighted combination of multiple evaluators
- CustomEvaluator: user-provided scoring function
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Callable

from .models import PromptTestCase


class Evaluator(ABC):
    """Base class for output evaluators."""

    @abstractmethod
    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Evaluate output and return score (0-1)."""


class ExactMatchEvaluator(Evaluator):
    """Evaluator for exact matches."""

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        expected = test_case.expected_output
        actual = actual_output
        if not self.case_sensitive:
            expected = expected.lower()
            actual = actual.lower()
        return 1.0 if expected.strip() == actual.strip() else 0.0


class ContainsEvaluator(Evaluator):
    """Evaluator for substring containment with scoring."""

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        actual = actual_output if self.case_sensitive else actual_output.lower()
        total_checks = len(test_case.expected_contains) + len(test_case.expected_not_contains)
        if total_checks == 0:
            return 1.0
        passed = 0
        for term in test_case.expected_contains:
            check = term if self.case_sensitive else term.lower()
            if check in actual:
                passed += 1
        for term in test_case.expected_not_contains:
            check = term if self.case_sensitive else term.lower()
            if check not in actual:
                passed += 1
        return passed / total_checks


class SimilarityEvaluator(Evaluator):
    """Evaluate output similarity using word-level Jaccard index."""

    def __init__(self, case_sensitive: bool = False) -> None:
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        expected = test_case.expected_output
        actual = actual_output
        if not self.case_sensitive:
            expected = expected.lower()
            actual = actual.lower()
        expected_words = set(expected.split())
        actual_words = set(actual.split())
        if not expected_words and not actual_words:
            return 1.0
        union = expected_words | actual_words
        if not union:
            return 0.0
        intersection = expected_words & actual_words
        return len(intersection) / len(union)


class LengthEvaluator(Evaluator):
    """Evaluate whether output length falls within expected bounds."""

    def __init__(self, min_length: int = 0, max_length: int = 10000) -> None:
        self.min_length = min_length
        self.max_length = max_length

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        length = len(actual_output)
        if self.min_length <= length <= self.max_length:
            return 1.0
        if length < self.min_length:
            return length / self.min_length if self.min_length > 0 else 0.0
        # length > max_length
        return self.max_length / length if length > 0 else 0.0


class RegexEvaluator(Evaluator):
    """Evaluate output against one or more regex patterns."""

    def __init__(self, patterns: list[str] | None = None, all_must_match: bool = True) -> None:
        self._patterns = [re.compile(p) for p in (patterns or [])]
        self.all_must_match = all_must_match

    def add_pattern(self, pattern: str) -> None:
        self._patterns.append(re.compile(pattern))

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        if not self._patterns:
            return 1.0
        matches = sum(1 for p in self._patterns if p.search(actual_output))
        if self.all_must_match:
            return 1.0 if matches == len(self._patterns) else matches / len(self._patterns)
        return 1.0 if matches > 0 else 0.0


class CompositeEvaluator(Evaluator):
    """Combine multiple evaluators with weights.

    Example::

        comp = CompositeEvaluator()
        comp.add(ContainsEvaluator(), weight=0.6)
        comp.add(LengthEvaluator(min_length=50), weight=0.4)
        score = comp.evaluate(test_case, output)
    """

    def __init__(self) -> None:
        self._evaluators: list[tuple[Evaluator, float]] = []

    def add(self, evaluator: Evaluator, weight: float = 1.0) -> None:
        """Add an evaluator with a weight."""
        self._evaluators.append((evaluator, weight))

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        if not self._evaluators:
            return 0.0
        total_weight = sum(w for _, w in self._evaluators)
        if total_weight == 0:
            return 0.0
        weighted_sum = sum(
            evaluator.evaluate(test_case, actual_output) * weight
            for evaluator, weight in self._evaluators
        )
        return weighted_sum / total_weight


class CustomEvaluator(Evaluator):
    """Evaluator using a user-provided function."""

    def __init__(self, eval_fn: Callable[[PromptTestCase, str], float]) -> None:
        self.eval_fn = eval_fn

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """evaluate ."""
        return self.eval_fn(test_case, actual_output)
