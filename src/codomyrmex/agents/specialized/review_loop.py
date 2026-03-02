"""Generate → test → review → fix cycle for autonomous coding.

Orchestrates code generation, test generation, and review
until convergence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.coding.generator import CodeBundle, CodeGenerator
from codomyrmex.coding.test_generator import TestGenerator, TestSuite
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ReviewResult:
    """Result of a code review iteration.

    Attributes:
        iteration: Iteration number.
        approved: Whether the code was approved.
        issues: Issues found.
        score: Quality score (0-1).
    """

    iteration: int = 0
    approved: bool = False
    issues: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class ReviewLoopResult:
    """Complete result of the review loop.

    Attributes:
        converged: Whether the loop converged (approval reached).
        iterations: Total iterations.
        final_code: Final code bundle.
        final_tests: Final test suite.
        reviews: All review results.
    """

    converged: bool = False
    iterations: int = 0
    final_code: CodeBundle | None = None
    final_tests: TestSuite | None = None
    reviews: list[ReviewResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "converged": self.converged,
            "iterations": self.iterations,
            "functions": self.final_code.functions if self.final_code else [],
            "tests": self.final_tests.test_count if self.final_tests else 0,
        }


class ReviewLoop:
    """Autonomous generate → test → review cycle.

    Usage::

        loop = ReviewLoop(max_iterations=5)
        result = loop.run("Create a calculator with add and multiply")
        assert result.converged
    """

    def __init__(
        self,
        max_iterations: int = 5,
        approval_threshold: float = 0.7,
    ) -> None:
        """Initialize this instance."""
        self._max_iterations = max_iterations
        self._approval_threshold = approval_threshold
        self._generator = CodeGenerator()
        self._test_generator = TestGenerator()

    def run(self, spec: str) -> ReviewLoopResult:
        """Run the generate-test-review loop.

        Args:
            spec: Task specification.

        Returns:
            ``ReviewLoopResult`` with convergence status.
        """
        result = ReviewLoopResult()
        code = self._generator.generate(spec)

        for i in range(self._max_iterations):
            # Generate tests for current code
            tests = self._test_generator.from_source(code.source)

            # Review
            review = self._review(code, tests, i + 1)
            result.reviews.append(review)

            if review.approved:
                result.converged = True
                result.iterations = i + 1
                result.final_code = code
                result.final_tests = tests
                logger.info("Review loop converged", extra={"iterations": i + 1})
                return result

            # Improve: each iteration increases quality score
            # In a real system this would re-generate code
            code = self._generator.generate(spec)

        result.iterations = self._max_iterations
        result.final_code = code
        result.final_tests = self._test_generator.from_source(code.source)
        return result

    def _review(self, code: CodeBundle, tests: TestSuite, iteration: int) -> ReviewResult:
        """Simulate code review with quality scoring."""
        issues: list[str] = []
        score = 0.0

        # Check: has functions or classes
        if code.functions:
            score += 0.3
        else:
            issues.append("No functions generated")

        # Check: has tests
        if tests.test_count > 0:
            score += 0.3
        else:
            issues.append("No tests generated")

        # Check: code compiles
        try:
            compile(code.source, code.filename, "exec")
            score += 0.2
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")

        # Check: reasonable size
        if code.line_count >= 5:
            score += 0.2
        else:
            issues.append("Code too short")

        return ReviewResult(
            iteration=iteration,
            approved=score >= self._approval_threshold,
            issues=issues,
            score=score,
        )


__all__ = ["ReviewLoop", "ReviewLoopResult", "ReviewResult"]
