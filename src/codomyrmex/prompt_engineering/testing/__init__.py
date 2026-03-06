"""
Prompt Testing Module

Systematic prompt evaluation and A/B testing.
"""

__version__ = "0.1.0"

from typing import Any

from .evaluators import (
    ContainsEvaluator,
    CustomEvaluator,
    Evaluator,
    ExactMatchEvaluator,
)
from .models import (
    EvaluationType,
    PromptTestCase,
    TestResult,
    TestStatus,
    TestSuiteResult,
)
from .runner import ABTest, PromptTester, PromptTestSuite

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = Any
    ResultStatus = Any


def cli_commands() -> dict[str, Any]:
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
    "ABTest",
    "ContainsEvaluator",
    "CustomEvaluator",
    # Enums
    "EvaluationType",
    # Evaluators
    "Evaluator",
    "ExactMatchEvaluator",
    # Data classes
    "PromptTestCase",
    # Core
    "PromptTestSuite",
    "PromptTester",
    "TestResult",
    "TestStatus",
    "TestSuiteResult",
    # CLI
    "cli_commands",
]
