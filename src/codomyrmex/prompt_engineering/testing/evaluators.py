"""
Prompt Testing Evaluators

Output evaluation strategies for prompt testing.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable

from .models import PromptTestCase


class Evaluator(ABC):
    """Base class for output evaluators."""

    @abstractmethod
    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Evaluate output and return score (0-1)."""
        pass


class ExactMatchEvaluator(Evaluator):
    """Evaluator for exact matches."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Check for exact match."""
        expected = test_case.expected_output
        actual = actual_output

        if not self.case_sensitive:
            expected = expected.lower()
            actual = actual.lower()

        return 1.0 if expected.strip() == actual.strip() else 0.0


class ContainsEvaluator(Evaluator):
    """Evaluator for substring containment."""

    def __init__(self, case_sensitive: bool = False):
        self.case_sensitive = case_sensitive

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Check for contains/not contains."""
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


class CustomEvaluator(Evaluator):
    """Evaluator using custom function."""

    def __init__(self, eval_fn: Callable[[PromptTestCase, str], float]):
        self.eval_fn = eval_fn

    def evaluate(self, test_case: PromptTestCase, actual_output: str) -> float:
        """Apply custom evaluation function."""
        return self.eval_fn(test_case, actual_output)
