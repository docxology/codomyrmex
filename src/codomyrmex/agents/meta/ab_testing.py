"""A/B testing engine for strategy comparison.

Compares two strategies over n trials and determines a winner.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ABTestResult:
    """Result of an A/B test.

    Attributes:
        strategy_a: First strategy name.
        strategy_b: Second strategy name.
        wins_a: Trials won by A.
        wins_b: Trials won by B.
        ties: Tied trials.
        winner: Name of winning strategy (or ``tie``).
        significance: Statistical significance (p-value approximation).
    """

    strategy_a: str = ""
    strategy_b: str = ""
    wins_a: int = 0
    wins_b: int = 0
    ties: int = 0
    winner: str = "tie"
    significance: float = 1.0

    @property
    def total_trials(self) -> int:
        """total Trials ."""
        return self.wins_a + self.wins_b + self.ties

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "strategy_a": self.strategy_a,
            "strategy_b": self.strategy_b,
            "wins_a": self.wins_a,
            "wins_b": self.wins_b,
            "ties": self.ties,
            "winner": self.winner,
            "significance": round(self.significance, 4),
            "total_trials": self.total_trials,
        }


class ABTestEngine:
    """Compare strategies via A/B testing.

    Uses score-based comparison over multiple trials.

    Usage::

        engine = ABTestEngine()
        result = engine.compare_scores(
            "fast", [0.8, 0.7, 0.9],
            "thorough", [0.9, 0.85, 0.95],
        )
        print(f"Winner: {result.winner}")
    """

    def compare_scores(
        self,
        name_a: str,
        scores_a: list[float],
        name_b: str,
        scores_b: list[float],
    ) -> ABTestResult:
        """Compare two strategies based on scores.

        Args:
            name_a: Strategy A name.
            scores_a: Scores for A.
            name_b: Strategy B name.
            scores_b: Scores for B.

        Returns:
            ``ABTestResult`` with winner determination.
        """
        n_trials = min(len(scores_a), len(scores_b))
        wins_a = 0
        wins_b = 0
        ties = 0

        for i in range(n_trials):
            if scores_a[i] > scores_b[i]:
                wins_a += 1
            elif scores_b[i] > scores_a[i]:
                wins_b += 1
            else:
                ties += 1

        # Simple binomial test approximation
        total_decisive = wins_a + wins_b
        if total_decisive > 0:
            p_a = wins_a / total_decisive
            # Use proportion test: how far from 0.5 is the proportion?
            significance = abs(p_a - 0.5) * 2  # 0=equivalent, 1=decisive
        else:
            significance = 0.0

        if wins_a > wins_b:
            winner = name_a
        elif wins_b > wins_a:
            winner = name_b
        else:
            winner = "tie"

        result = ABTestResult(
            strategy_a=name_a,
            strategy_b=name_b,
            wins_a=wins_a,
            wins_b=wins_b,
            ties=ties,
            winner=winner,
            significance=significance,
        )

        logger.info(
            "A/B test complete",
            extra={"winner": winner, "trials": n_trials},
        )

        return result


__all__ = ["ABTestEngine", "ABTestResult"]
