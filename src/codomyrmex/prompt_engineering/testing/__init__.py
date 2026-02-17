"""
Prompt Testing Module

Systematic prompt evaluation and A/B testing.
"""

__version__ = "0.1.0"

from .models import EvaluationType, PromptTestCase, TestResult, TestStatus, TestSuiteResult
from .evaluators import ContainsEvaluator, CustomEvaluator, Evaluator, ExactMatchEvaluator
from .runner import ABTest, PromptTestSuite, PromptTester

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the prompt_testing module."""
    return {
        "suites": lambda: print(
            "Prompt Test Suites\n"
            "  Evaluation types: " + ", ".join(et.value for et in EvaluationType) + "\n"
            "  Test statuses: " + ", ".join(ts.value for ts in TestStatus) + "\n"
            "  Use PromptTestSuite to organize and list prompt test suites."
        ),
        "run": lambda: print(
            "Run Prompt Tests\n"
            "  Use PromptTester to execute prompt test suites.\n"
            "  Evaluators: ExactMatchEvaluator, ContainsEvaluator, CustomEvaluator\n"
            "  Use ABTest for comparative prompt evaluation."
        ),
    }


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
    # CLI
    "cli_commands",
]
