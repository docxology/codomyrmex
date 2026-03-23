from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring import get_logger

"""Decision making module for CEREBRUM."""

logger = get_logger(__name__)


@dataclass
class Decision:
    """Represents a choice made by the DecisionModule."""

    choice: Any
    confidence: float
    rationale: str
    metadata: dict[str, Any]


class DecisionModule:
    """Handles multi-criteria decision making."""

    def __init__(self):
        """Initialize decision module."""
        self.logger = get_logger(__name__)

    def decide(
        self, options: list[Any], criteria: dict[str, float], context: dict[str, Any]
    ) -> Decision:
        """Make a decision among options based on criteria and context.

        Args:
            options: list of available choices. If choices are objects,
                     they may need to have attributes matching criteria keys.
            criteria: Dictionary of criterion name to weight (0-1).
            context: Additional information for evaluation.
                     May include specific scores for options.

        Returns:
            The selected decision
        """
        if not options:
            return Decision(
                choice=None,
                confidence=0.0,
                rationale="No options provided",
                metadata={},
            )

        if not criteria:
            return Decision(
                choice=options[0],
                confidence=0.5,
                rationale="No criteria provided, selected first option",
                metadata={},
            )

        self.logger.info(
            "Making decision among %s options with %s criteria",
            len(options),
            len(criteria),
        )

        scores = []
        for option in options:
            total_score = 0.0
            total_weight = sum(criteria.values())

            for criterion, weight in criteria.items():
                # Try to find a score for this option/criterion pair in context
                # Context format expected: {"scores": {"Option1": {"Reliability": 0.9, ...}, ...}}
                context_scores = context.get("scores", {})
                option_scores = context_scores.get(str(option), {})

                score = option_scores.get(criterion)

                if score is None:
                    # Fallback: check if option has the criterion as an attribute
                    score = (
                        getattr(option, criterion.lower(), 0.5)
                        if hasattr(option, criterion.lower())
                        else 0.5
                    )

                total_score += score * weight

            final_score = total_score / total_weight if total_weight > 0 else 0.5

            scores.append(final_score)

        best_idx = scores.index(max(scores))
        best_option = options[best_idx]
        confidence = scores[best_idx]

        return Decision(
            choice=best_option,
            confidence=float(confidence),
            rationale=f"Selected {best_option} with score {confidence:.2f} based on weighted criteria",
            metadata={
                "all_scores": {
                    str(opt): float(score)
                    for opt, score in zip(options, scores, strict=False)
                },
                "criteria_used": list(criteria.keys()),
            },
        )
