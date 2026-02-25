"""Self-healing diagnosis and recovery planning.

Produces structured ``Diagnosis`` and ``RecoveryPlan`` from errors.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .failure_taxonomy import (
    ClassifiedError,
    FailureCategory,
    RecoveryStrategy,
    classify_error,
)

logger = get_logger(__name__)


@dataclass
class RecoveryStep:
    """A single step in a recovery plan.

    Attributes:
        action: What to do.
        strategy: Which recovery strategy.
        parameters: Action parameters.
        order: Execution order.
    """

    action: str
    strategy: RecoveryStrategy
    parameters: dict[str, Any] = field(default_factory=dict)
    order: int = 0


@dataclass
class Diagnosis:
    """Result of error diagnosis.

    Attributes:
        error: The classified error.
        root_cause: Identified root cause.
        impact: Impact assessment.
        recovery_plan: Ordered recovery steps.
        diagnosed_at: Timestamp.
    """

    error: ClassifiedError
    root_cause: str = ""
    impact: str = "unknown"
    recovery_plan: list[RecoveryStep] = field(default_factory=list)
    diagnosed_at: float = 0.0

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.diagnosed_at:
            self.diagnosed_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "error": self.error.to_dict(),
            "root_cause": self.root_cause,
            "impact": self.impact,
            "steps": [{"action": s.action, "strategy": s.strategy.value} for s in self.recovery_plan],
        }


class Diagnoser:
    """Diagnose errors and produce recovery plans.

    Usage::

        diagnoser = Diagnoser()
        diagnosis = diagnoser.diagnose(ValueError("Invalid config value"))
        for step in diagnosis.recovery_plan:
            print(f"{step.order}. {step.action}")
    """

    # Recovery action templates per strategy
    _ACTION_TEMPLATES: dict[RecoveryStrategy, str] = {
        RecoveryStrategy.RETRY: "Retry the operation with exponential backoff",
        RecoveryStrategy.ADJUST_CONFIG: "Adjust configuration parameters",
        RecoveryStrategy.FALLBACK: "Switch to fallback provider/method",
        RecoveryStrategy.ESCALATE: "Escalate to human operator for review",
        RecoveryStrategy.SKIP: "Skip this task and continue with next",
        RecoveryStrategy.RESTART: "Restart the affected component",
    }

    def diagnose(
        self,
        error: Exception | str,
        context: dict[str, Any] | None = None,
    ) -> Diagnosis:
        """Diagnose an error and create a recovery plan.

        Args:
            error: The error to diagnose.
            context: Additional context.

        Returns:
            ``Diagnosis`` with root cause and recovery steps.
        """
        classified = classify_error(error)
        if context:
            classified.context.update(context)

        # Generate root cause description
        root_cause = self._identify_root_cause(classified)

        # Build recovery plan from suggested strategies
        steps = []
        for i, strategy in enumerate(classified.suggested_strategies):
            action = self._ACTION_TEMPLATES.get(strategy, str(strategy))
            steps.append(RecoveryStep(
                action=action,
                strategy=strategy,
                order=i + 1,
            ))

        # Assess impact
        impact = self._assess_impact(classified)

        diagnosis = Diagnosis(
            error=classified,
            root_cause=root_cause,
            impact=impact,
            recovery_plan=steps,
        )

        logger.info(
            "Diagnosis complete",
            extra={
                "category": classified.category.value,
                "root_cause": root_cause[:50],
                "steps": len(steps),
            },
        )

        return diagnosis

    @staticmethod
    def _identify_root_cause(error: ClassifiedError) -> str:
        """Generate root cause description."""
        causes: dict[FailureCategory, str] = {
            FailureCategory.CONFIG_ERROR: "Invalid or missing configuration",
            FailureCategory.RESOURCE_EXHAUSTION: "System resources exceeded limits",
            FailureCategory.DEPENDENCY_FAILURE: "External dependency unavailable",
            FailureCategory.LOGIC_ERROR: "Programming error in logic",
            FailureCategory.TIMEOUT: "Operation exceeded time limit",
            FailureCategory.PERMISSION_ERROR: "Insufficient permissions",
            FailureCategory.UNKNOWN: "Unidentified failure",
        }
        return causes.get(error.category, "Unknown cause")

    @staticmethod
    def _assess_impact(error: ClassifiedError) -> str:
        """Assess the impact of the failure."""
        high_impact = {FailureCategory.RESOURCE_EXHAUSTION, FailureCategory.PERMISSION_ERROR}
        medium_impact = {FailureCategory.CONFIG_ERROR, FailureCategory.DEPENDENCY_FAILURE}
        if error.category in high_impact:
            return "high"
        if error.category in medium_impact:
            return "medium"
        return "low"


__all__ = [
    "Diagnoser",
    "Diagnosis",
    "RecoveryStep",
]
