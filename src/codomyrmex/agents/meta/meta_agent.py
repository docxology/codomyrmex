"""Meta-agent for self-improving agent strategies.

Wraps any agent operation and tracks outcomes to evolve strategy
selection over time.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from codomyrmex.agents.meta.ab_testing import ABTestEngine
from codomyrmex.agents.meta.scoring import OutcomeScorer
from codomyrmex.agents.meta.strategies import StrategyLibrary
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class EvolutionRecord:
    """Record of a strategy evolution step.

    Attributes:
        iteration: Iteration number.
        strategy: Strategy used.
        score: Outcome score.
    """

    iteration: int
    strategy: str
    score: float


class MetaAgent:
    """Self-improving meta-agent.

    Wraps task execution, scores outcomes, selects the best
    strategy, and tracks evolution history.

    Usage::

        meta = MetaAgent()
        meta.library.add(Strategy("fast", "Be quick: {task}"))
        meta.library.add(Strategy("careful", "Be thorough: {task}"))

        def execute_task(strategy_name: str) -> dict:
            return {"tests_passed": 9, "tests_total": 10}

        meta.run(execute_task, iterations=5)
        print(f"Best: {meta.library.best_strategy().name}")
    """

    def __init__(
        self,
        library: StrategyLibrary | None = None,
        scorer: OutcomeScorer | None = None,
        ab_engine: ABTestEngine | None = None,
    ) -> None:
        self.library = library or StrategyLibrary()
        self._scorer = scorer or OutcomeScorer()
        self._ab_engine = ab_engine or ABTestEngine()
        self._history: list[EvolutionRecord] = []

    @property
    def history(self) -> list[EvolutionRecord]:
        """History."""
        return list(self._history)

    @property
    def improvement(self) -> float:
        """Score improvement from first to last iteration."""
        if len(self._history) < 2:
            return 0.0
        return self._history[-1].score - self._history[0].score

    def run(
        self,
        task_fn: Callable[[str], dict[str, Any]],
        iterations: int = 5,
    ) -> list[EvolutionRecord]:
        """Run the meta-agent learning loop.

        For each iteration:
        1. Select best strategy
        2. Execute task with that strategy
        3. Score the outcome
        4. Update strategy success rate

        Args:
            task_fn: Function(strategy_name) → outcome dict.
                     Expected keys: tests_passed, tests_total,
                     tokens_used, quality_issues, elapsed.
            iterations: Number of iterations.

        Returns:
            List of evolution records.
        """
        strategies = self.library.list_strategies()
        if not strategies:
            logger.warning("No strategies available")
            return []

        for i in range(iterations):
            # Select strategy: best or round-robin
            strategy = self.library.best_strategy() or strategies[i % len(strategies)]

            # Execute
            try:
                outcome = task_fn(strategy.name)
            except Exception as exc:
                logger.warning(f"Task failed: {exc}")
                strategy.record_outcome(False)
                self._history.append(EvolutionRecord(i, strategy.name, 0.0))
                continue

            # Score
            score = self._scorer.score(
                tests_passed=outcome.get("tests_passed", 0),
                tests_total=outcome.get("tests_total", 1),
                tokens_used=outcome.get("tokens_used", 0),
                token_budget=outcome.get("token_budget", 1000),
                quality_issues=outcome.get("quality_issues", 0),
                elapsed_seconds=outcome.get("elapsed", 0.0),
            )

            # Update strategy
            strategy.record_outcome(score.composite > 0.5)

            record = EvolutionRecord(i, strategy.name, score.composite)
            self._history.append(record)

            logger.info(
                "Meta iteration complete",
                extra={
                    "iteration": i,
                    "strategy": strategy.name,
                    "score": round(score.composite, 3),
                },
            )

        return list(self._history)


__all__ = ["EvolutionRecord", "MetaAgent"]
