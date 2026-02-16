"""
Flag evaluation engine.

Provides the core evaluation logic for feature flags, including targeting
rules and percentage-based rollout evaluation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

from ..strategies import EvaluationContext, EvaluationResult, EvaluationStrategy


@dataclass
class TargetingRule:
    """A single targeting rule that matches context attributes.

    Attributes:
        attribute: The context attribute key to match against.
        operator: Comparison operator (eq, neq, in, contains, gt, lt, gte, lte).
        value: The value to compare with.
    """
    attribute: str
    operator: str
    value: Any

    def matches(self, context: EvaluationContext) -> bool:
        """Return True if this rule matches the given context."""
        actual = context.get_attribute(self.attribute)
        if actual is None:
            return False

        operators = {
            "eq": lambda a, b: a == b,
            "neq": lambda a, b: a != b,
            "in": lambda a, b: a in b,
            "contains": lambda a, b: b in a,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
        }

        op_fn = operators.get(self.operator)
        if op_fn is None:
            return False

        try:
            return op_fn(actual, self.value)
        except (TypeError, ValueError):
            return False


@dataclass
class FlagDefinition:
    """Internal representation of a feature flag for evaluation purposes.

    Attributes:
        name: Unique flag identifier.
        enabled: Global kill-switch; if False the flag is always off.
        percentage: Rollout percentage (0.0 - 100.0).
        targeting_rules: Optional list of targeting rules.
    """
    name: str
    enabled: bool = True
    percentage: float = 100.0
    targeting_rules: list[TargetingRule] = field(default_factory=list)


class FlagEvaluator:
    """Stateless evaluator for feature flags.

    The evaluator checks a flag against an evaluation context by applying
    targeting rules, percentage rollouts, and the global enabled switch in
    the correct precedence order.
    """

    def evaluate(
        self,
        flag: FlagDefinition,
        context: EvaluationContext,
    ) -> EvaluationResult:
        """Evaluate a feature flag for the given context.

        Evaluation order:
        1. If the flag is globally disabled, return disabled.
        2. If targeting rules exist and none match, return disabled.
        3. Apply percentage rollout.

        Args:
            flag: The flag definition to evaluate.
            context: The evaluation context (user, environment, attributes).

        Returns:
            An EvaluationResult indicating whether the flag is enabled.
        """
        # 1. Global kill-switch
        if not flag.enabled:
            return EvaluationResult(
                enabled=False,
                reason="flag_disabled",
            )

        # 2. Targeting rules (if any exist, at least one must match)
        if flag.targeting_rules:
            if not self.evaluate_targeting_rules(flag.targeting_rules, context):
                return EvaluationResult(
                    enabled=False,
                    reason="targeting_rules_no_match",
                )

        # 3. Percentage rollout
        if flag.percentage < 100.0:
            user_id = context.user_id or context.session_id or ""
            enabled = self.evaluate_percentage_rollout(flag, user_id)
            return EvaluationResult(
                enabled=enabled,
                reason=f"percentage_rollout:{flag.percentage}%",
                metadata={"percentage": flag.percentage},
            )

        return EvaluationResult(enabled=True, reason="enabled")

    def evaluate_targeting_rules(
        self,
        rules: list[TargetingRule],
        context: EvaluationContext,
    ) -> bool:
        """Return True if at least one targeting rule matches the context.

        Args:
            rules: The list of targeting rules to evaluate (OR logic).
            context: The evaluation context.

        Returns:
            True if any rule matches.
        """
        return any(rule.matches(context) for rule in rules)

    def evaluate_percentage_rollout(
        self,
        flag: FlagDefinition,
        user_id: str,
    ) -> bool:
        """Determine if a user falls within the rollout percentage.

        Uses a deterministic hash of the flag name and user id so the same
        user always gets a consistent result for a given flag.

        Args:
            flag: The flag definition (provides name and percentage).
            user_id: A stable user/session identifier.

        Returns:
            True if the user is within the rollout percentage.
        """
        hash_input = f"{flag.name}:{user_id}"
        digest = hashlib.sha256(hash_input.encode()).hexdigest()
        bucket = int(digest[:8], 16) % 10000  # 0-9999 for 0.01% granularity
        threshold = flag.percentage * 100  # Convert percentage to basis points
        return bucket < threshold


__all__ = [
    "FlagDefinition",
    "FlagEvaluator",
    "TargetingRule",
]
