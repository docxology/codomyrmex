"""Multi-dimensional outcome scoring for agent self-improvement.

Scores agent outcomes on correctness, efficiency, quality, and speed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class OutcomeScore:
    """Multi-dimensional score of an agent outcome.

    Attributes:
        correctness: Test pass rate (0-1).
        efficiency: Token efficiency (0-1, 1=minimal tokens).
        quality: Code quality score (0-1).
        speed: Relative speed (0-1, 1=fastest).
        composite: Weighted composite score.
    """

    correctness: float = 0.0
    efficiency: float = 0.0
    quality: float = 0.0
    speed: float = 0.0
    composite: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "correctness": round(self.correctness, 3),
            "efficiency": round(self.efficiency, 3),
            "quality": round(self.quality, 3),
            "speed": round(self.speed, 3),
            "composite": round(self.composite, 3),
        }


class OutcomeScorer:
    """Score agent outcomes across multiple dimensions.

    Usage::

        scorer = OutcomeScorer()
        score = scorer.score(
            tests_passed=9, tests_total=10,
            tokens_used=500, token_budget=1000,
            quality_issues=2, max_quality_issues=10,
            elapsed_seconds=5.0, time_budget=30.0,
        )
        print(f"Composite: {score.composite:.2f}")
    """

    def __init__(
        self,
        weights: dict[str, float] | None = None,
    ) -> None:
        """Execute   Init   operations natively."""
        self._weights = weights or {
            "correctness": 0.4,
            "efficiency": 0.2,
            "quality": 0.25,
            "speed": 0.15,
        }

    def score(
        self,
        tests_passed: int = 0,
        tests_total: int = 1,
        tokens_used: int = 0,
        token_budget: int = 1000,
        quality_issues: int = 0,
        max_quality_issues: int = 10,
        elapsed_seconds: float = 0.0,
        time_budget: float = 30.0,
    ) -> OutcomeScore:
        """Calculate outcome score.

        Args:
            tests_passed: Number of passing tests.
            tests_total: Total tests.
            tokens_used: Tokens consumed.
            token_budget: Maximum token budget.
            quality_issues: Code quality issues found.
            max_quality_issues: Maximum tolerable issues.
            elapsed_seconds: Wall-clock time.
            time_budget: Time budget.

        Returns:
            ``OutcomeScore`` with composite.
        """
        correctness = tests_passed / max(tests_total, 1)
        efficiency = max(0.0, 1.0 - tokens_used / max(token_budget, 1))
        quality = max(0.0, 1.0 - quality_issues / max(max_quality_issues, 1))
        speed = max(0.0, 1.0 - elapsed_seconds / max(time_budget, 0.001))

        composite = (
            self._weights["correctness"] * correctness
            + self._weights["efficiency"] * efficiency
            + self._weights["quality"] * quality
            + self._weights["speed"] * speed
        )

        s = OutcomeScore(
            correctness=correctness,
            efficiency=efficiency,
            quality=quality,
            speed=speed,
            composite=min(composite, 1.0),
        )

        logger.info("Outcome scored", extra={"composite": round(s.composite, 3)})
        return s


__all__ = ["OutcomeScore", "OutcomeScorer"]
