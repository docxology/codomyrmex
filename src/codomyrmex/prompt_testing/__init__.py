"""
Prompt Testing Module

Systematic prompt evaluation and A/B testing.
"""

__version__ = "0.1.0"

from .models import EvaluationType, PromptTestCase, TestResult, TestStatus, TestSuiteResult
from .evaluators import ContainsEvaluator, CustomEvaluator, Evaluator, ExactMatchEvaluator
from .runner import ABTest, PromptTestSuite, PromptTester

__all__ = [
    # Enums
    "EvaluationType",
    "TestStatus",
    # Data classes
    "PromptTestCase",
    "TestResult",
    "TestSuiteResult",
    # Evaluators
    "Evaluator",
    "ExactMatchEvaluator",
    "ContainsEvaluator",
    "CustomEvaluator",
    # Core
    "PromptTestSuite",
    "PromptTester",
    "ABTest",
]
